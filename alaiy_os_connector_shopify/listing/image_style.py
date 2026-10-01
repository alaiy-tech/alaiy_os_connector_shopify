# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""
The house studio finish: the part of a listing photo that must NOT be left to a model.

A retouched photograph and a catalog photograph are different things. The retouch —
even lighting, true colour, no dust — is judgement about a specific piece, and an
image model is good at it. The house look is the opposite: an exact background hex,
the same margin on every product, the same shadow at the same angle on all of them.
Ask a model for `#f4f4f4` and you get a grey near it, a different grey on the next
photo, and a margin that drifts with whatever it thought the composition wanted. So
the model is asked for the product on an empty white ground and nothing else, and
everything measurable is composited here, in code.

Two things live in this module:

  * `load()` — the style spec, contributed by the client app through the
    `listing_image_style` hook, exactly the way the attribute matrix arrives (see
    matrix.py). A look belongs to the store, not to this app: The Solist's catalog
    is light grey with a hard, light shadow; another client's is not, and a base app
    that hardcodes one customer's brand guidelines is a base app no one else can
    install. No provider means no finish, which is this app's behaviour to date.

  * `apply_finish()` — the compositor. Free of Frappe, so it can run on a worker
    thread; pure Pillow apart from the matte.

How the product is separated from its background is the one real choice in here,
and there are five ways — four that never let a model touch the product's own
pixels, and one that does:

  * `photoroom` — Photoroom's Image Editing API (v2/edit) does the matting, the
    flat background fill AND the AI shadow, in one call. Opt-in, not the default:
    it costs a network round trip and a per-photo fee that `segment` did not, but
    it is a production matting service rather than a local mask, and it draws the
    shadow itself instead of this module faking one in Pillow. See
    `_finish_photoroom`.
  * `segment` — a local segmentation model (rembg / ISNet) computes an alpha
    mask. It reads the photo and outputs an opacity per pixel; it does not draw
    anything. The product's own pixels are carried through untouched — no
    network call, no per-photo fee, but the shadow and background fill are still
    hand-rolled Pillow (see `_compose` / `_cast_shadow`), and this catalog's own
    photos are the evidence ISNet needs over rembg's u2net default (see
    `segment_model` below). THE DEFAULT: no site gets Photoroom's network cost
    or per-photo fee without asking for it.
  * `gemini` — Gemini is asked to place the SAME photo on the house's exact
    background colour, and that render is used only to find the product's
    outline: a flood-fill run over it, exactly `flood`'s algorithm, because
    Gemini (unlike a real photo shoot) can be told to make the ground clean
    enough for one. Whatever Gemini draws for the product itself is discarded —
    the cutout that reaches the canvas is always cropped from the ORIGINAL
    photo's own pixels, never from Gemini's render. See `_gemini_isolated`. A
    site reaches for this over `segment` when the local model's mask is visibly
    wrong on its catalog (a metal watch bracelet or bag chain punched full of
    holes) and reaches for it over `photoroom` to keep every generative call on
    the one provider — at the cost of a network round trip and a generation fee
    per photo that `segment` does not pay. When Gemini itself cannot make the
    ground clean enough to flood-fill (a strongly patterned or richly coloured
    original backdrop), this falls back to `segment` for that one photo rather
    than skip it — Gemini is here to fix what a real segmentation model gets
    wrong, not to give up the cases it already gets right.
  * `flood` — fill inward from the frame edge over near-white pixels. No model, no
    network call, no dependency, and no cost, but it only works on a photo that is
    ALREADY on a clean, even, pale ground. Kept for exactly that case.
  * `gemini_full` — the odd one out, and the only matte where this module's own
    "the model is asked for the product on an empty ground and nothing else"
    promise (see the top of this docstring) does NOT hold. One `generate_image`
    call does the whole job — background, shadow, everything — and whatever
    Gemini returns ships as the finished photo, with only its ground pulled
    onto the exact house hex in place (see `_snap_background`) — Gemini lands
    near a requested colour, not on it — and, where Gemini framed a complete piece
    tighter than `padding` or in another shape, the ground grown out to the
    house margin and aspect (see `_frame_to_spec`).
    No mask, no crop from the original, no local compositor, so its shadow stays
    as drawn. Simpler, and it is what a plain
    manual test of the same prompt against the same photo produced cleanly when
    `gemini`'s mask-only path could not separate a busy backdrop — but it means
    the product's own pixels are no longer guaranteed to be the photographer's:
    a resale catalog that turned generative retouching off for exactly that
    reason (see `retouch` below) should treat this as a considered trade, not a
    default. Kept as a sibling of the other four, not a replacement for any of
    them, precisely so a site can move to it and back by changing one config
    value. See `_finish_gemini_full`.

Either way the compositor refuses rather than guesses: if what comes back is not a
believable separation, the original image is returned with a note a reviewer can
read. A mangled photo of a $40k watch is worse than an unfinished one.

## Why this lives in the connector

It came from `alaiy_os_agent_shopify_listing`, now retired. The image step is the
channel's — Shopify is the only channel that declares a `prepare_images` handler
— so the whole producing side moved here with it, this module included.

The look itself does NOT belong to any app here. It arrives from the client app
through the `listing_image_style` hook, the same seam `matrix.py` uses for the
mandatory-attribute guideline, and both are read the same way for the same
reason: what a specific seller's catalogue looks like is that seller's business,
and a connector every Shopify site installs must not carry one store's brand
guidelines. No provider means no finish.
"""

import base64
import io
import threading

import frappe
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat

HOOK = "listing_image_style"

# A site can tune the look without a code change — same idea as `listing_image_queue`
# in image_stage.py. Merged OVER whatever the client app's hook returns, so a bench
# can nudge padding or shadow for one store without editing that store's app.
CONF_KEY = "listing_image_style"

# Everything but the background has a working default: a client contributing a look
# has an opinion about the colour, and usually not about blur radii.
DEFAULTS = {
    # The ground every product is composited onto.
    "background": None,
    # How the product is separated from its background: "segment" (a local model
    # computes an alpha mask and the product's pixels are untouched,
    # background/shadow composited here in Pillow), "photoroom" (a hosted matting
    # service that also draws the background fill and shadow), "gemini" (Gemini
    # isolates the product onto the house ground; only used to find the outline
    # via a flood-fill, never for the product's own pixels — see the module
    # docstring), "flood" (fill in from the frame edge; needs an already-clean
    # pale background), "gemini_key" (as "gemini", but Gemini isolates the product
    # onto a vivid key colour that is then removed by colour, gaps inside the
    # product included — see `_gemini_keyed`) or "gemini_full" (Gemini does the
    # whole finish — background,
    # shadow, everything — and its own render ships as the finished photo; the
    # only one of the five where the product's pixels are not guaranteed to be
    # the photographer's own — see the module docstring).
    "matte": "segment",
    # Which segmentation model, when matte is "segment". ISNet over rembg's u2net
    # default on the strength of the catalog it will actually see: u2net erases a
    # bag's chain strap and a watch bracelet almost entirely, which for a jewelry
    # and accessories catalog is the common case, not the corner case. ISNet keeps
    # them link for link at roughly twice the (still sub-two-second) cost.
    "segment_model": "isnet-general-use",
    # Whether the photo is sent through a generative retouch BEFORE it is
    # composited. Off means nothing regenerates the product: the original
    # photograph's pixels are what get composited, and only the ground changes.
    "retouch": False,
    # Minimum clear margin on each side, as a fraction of the canvas. A MINIMUM, not
    # a target — see `apply_finish` on why the product is never scaled up to meet it.
    "padding": 0.06,
    # Canvas width / height. 1.0 is square.
    "aspect": 1.0,
    # Longest edge of the finished image. Only ever scales a product DOWN.
    "max_size": 2048,
    # "Soft, but light": blur above _PHOTOROOM_HARD_BLUR_MAX so
    # _finish_photoroom's hard/soft read picks Photoroom's ai.soft, a low
    # opacity so it reads as contact with a surface rather than as a second
    # object, and a short drop. Not a reflection — there is no mirrored copy
    # anywhere in this module.
    "shadow": {
        "offset": 0.025,
        "blur": 0.03,
        "opacity": 0.15,
        "color": "#000000",
    },
    # Keep the transparent cutout as its own file, so the background can be changed
    # later without paying for the photo again.
    "keep_cutout": True,
    # Where the product runs out of the original frame (a strap cropped at the top
    # and bottom of the shot), let it run out of the finished canvas on that side
    # too, instead of padding it and leaving the cut end in mid-air. Off keeps the
    # padding on every side. See `_cut_edges`.
    "bleed_cut_edges": False,
}

_UNSET = object()

# Built lazily by _session and then reused for the life of the worker.
_SESSIONS = {}
_SESSION_LOCK = threading.Lock()

# ── what "the model did as it was told" means, in numbers ────────────────────

# How wide a ring around the edge counts as "the background", as a fraction of the
# shorter side. Wide enough to catch a gradient, narrow enough that a product
# running to the edge of a tight crop does not dominate it.
_BORDER_FRACTION = 0.04

# The ring has to be pale and it has to be flat. A ground with a gradient, a
# vignette or a visible surface has a standard deviation well above this; a clean
# white sweep sits near zero.
_BORDER_MIN_MEAN = 225
_BORDER_MAX_STDEV = 12

# How much of the ring must be ground — see `_ground_complaint`. A strap running
# out of both ends of a shot covered 13% of it.
_BORDER_MIN_GROUND = 0.6

# How far from its seed's own colour the fill is allowed to travel. Generous enough
# to cross the slight unevenness of a real render, tight enough to stop at the
# edge of anything that is actually the product.
_FILL_TOLERANCE = 36

# How close an edge pixel must be to the ground to seed the fill — the same
# 1-norm distance Pillow's floodfill measures `thresh` in. The edge of the frame is
# not all ground: a strap that runs out of the shot puts the product itself on the
# edge, often in a corner, and a fill seeded there takes the strap's colour for
# the ground and erases the whole strap. A pale pink strap measured 129-149 from a
# light grey ground; a render that lands near the requested ground rather than on
# it stays well inside this.
_SEED_TOLERANCE = 60

# How many evenly spaced points along each side of the frame are tried as seeds,
# corners included. Enough to reach every pocket of ground a product crossing the
# edge can cut off; a seed already filled by an earlier one costs nothing.
_SEEDS_PER_EDGE = 64

# A pixel counts as "filled" if the flood moved it at all. Compared against the
# untouched original rather than against the fill colour, so a product that happens
# to contain the sentinel colour is not punched full of holes.
_FILL_DELTA = 8
_FILL_COLOR = (255, 0, 255)

# What fraction of the frame the product may occupy for the result to be believable.
# Below the floor the fill ate the piece; above the ceiling it found no background
# at all and we would be "cutting out" the whole frame. The floor is very low on
# purpose: it is there to catch a flood that swallowed the product (which leaves
# essentially zero), NOT to insist a product be large in its frame — a stud shot at
# the same distance as a cuff is supposed to occupy very little of it.
_MIN_SUBJECT = 0.001
_MAX_SUBJECT = 0.98

# How much variation the selected region must contain to be a product at all —
# see _featureless. Very low: this separates "a patch of flat background" from any
# real photograph of an object, and is not a judgement about the object.
# Calibrated against the catalog rather than guessed: over a sample of real
# product photos the flattest subject measured 10.5 and most sit between 20 and
# 60, while a hallucinated blob on a blank frame is 0. This sits ~7x under the
# worst real photo and well clear of the failure it is for.
_MIN_SUBJECT_DETAIL = 1.5

# How close to a side of the frame, as a fraction of the shorter side, the product
# must reach for that side to be looked at — see `_cut_edges`. Not zero: a photo
# exported with a thin white rim (one had 3px of it on a 371px frame) crops the
# strap just inside the rim, not at the frame's own edge.
_CUT_EDGE_REACH = 0.015

# How much of the product's own width (or height) its outermost line on a side
# must cover for that side to count as cut on its own. Cropped straps, straight
# across or diagonal, measured 11-33%; a round bezel touching the side of a tight
# crop measured 1.3%, and a crown 4%.
_CUT_RUN_MIN = 0.08

# A thin product cropped by the shot — a chain leaving through the top of the
# frame — covers far less than that: two strands measured 6.6%. What marks it as
# cut is that it is straight at the edge: its outermost line is as wide as the
# line `reach` pixels in (99% for the chain), where a curve meeting the side is
# still narrowing to a point (11% for a bezel, 49% for a crown). Cropped straps
# measured 75-140%. `_CUT_THIN_MIN` keeps a speck on the edge from counting.
_CUT_STRAIGHT_MIN = 0.7
_CUT_THIN_MIN = 0.01

# Softens the one-pixel staircase the flood leaves behind. Deliberately under a
# pixel: any more and a bright metal edge starts to glow against the grey.
_EDGE_FEATHER = 0.7

# ── repairing what a segmentation mask reliably gets wrong ───────────────────

# How close a hole's colour must be to the product around it — plain RGB distance
# between the two means, 0..441 — for the hole to be read as a defect in the mask
# rather than somewhere you can genuinely see through the piece.
#
# Not a guess. Measured over the catalog's own photos: the mask's own bite marks
# out of a rubber watch strap sit at 0.6, 1.4 and 17 (they are the strap, so of
# course they match it), while every real gap measured far off — 44 through the
# handle of a chain-strap bag onto the wood behind it, 56 and 65 through the same
# bag's chain, 73 onto grass, 111 and 134 onto denim, 155 and 175 between the
# fingers of a hand holding a watch. So the whole catalog separates into a band
# under 20 and a band over 40, and this sits in the empty middle.
#
# Getting this wrong in the generous direction is the expensive one: a threshold
# high enough to catch 44 fills the gap inside a bag's chain handle with the wood
# it was photographed on, and re-pastes a slab of the old background into the
# middle of the finished image. Under-filling leaves a mask defect; over-filling
# invents a solid bag.
_HOLE_MATCH = 25.0

# How far out from a hole to look for "the product around it", in pixels. A few,
# so the comparison is against the material the hole was punched out of rather
# than against the average of the whole piece.
_HOLE_RING = 4

# Holes smaller than this are left alone whatever their colour. At a handful of
# pixels the mean colour is noise, and a hole that small is invisible anyway.
_HOLE_MIN_PIXELS = 20

# How far the matte is pulled in before compositing, in mask pixels — that is, in
# pixels of the 1024-square the segmentation model actually works at, scaled up to
# whatever the photo's real size is.
#
# That scaling is the point. The fringe this removes is created by the upscale: a
# mask computed at 1024 and stretched over a 3000px photo lands its edge a few
# real pixels wide, and those pixels are a blend of product and background. Left
# in, a watch shot on an orange backdrop keeps a thin orange outline once it is on
# grey. Expressed in mask pixels the correction is the same physical width on a
# 1080px photo and a 4500px one.
#
# Kept small on purpose: a couple of mask pixels is enough for the blend, and much
# more starts eating real edges — the thin gold chain of a bag is only a few mask
# pixels wide to begin with.
_EDGE_PULL = 1.5


# ── the spec ─────────────────────────────────────────────────────────────────


def load():
    """
    The house style for this site, or None when no client app contributes one.

    Validated once per request and cached on `frappe.local`, like matrix.load().
    None is a first-class answer: it means "finish nothing", which is what every
    site did before this module existed and what a site with no brand guidelines
    should keep doing.
    """
    cached = getattr(frappe.local, "_listing_image_style", _UNSET)
    if cached is not _UNSET:
        return cached

    spec = _build()
    frappe.local._listing_image_style = spec
    return spec


def _build():
    providers = frappe.get_hooks(HOOK) or []
    override = frappe.conf.get(CONF_KEY) or {}

    if not providers and not override:
        return None

    if len(providers) > 1:
        # Two looks would silently merge into one, and the losing store's catalog
        # would quietly start publishing in another store's brand colours.
        frappe.throw(
            f"More than one app provides {HOOK}: {providers}. A site has one "
            "store and one house style, so leave only the customer app whose "
            "store this site is."
        )

    spec = dict(DEFAULTS)
    if providers:
        spec.update(frappe.get_attr(providers[0])() or {})
    if override:
        # Shadow is merged a level deeper: a site tuning the opacity should not
        # have to restate the offset, blur and colour to keep them.
        shadow = dict(spec["shadow"], **(override.get("shadow") or {}))
        spec.update(override)
        spec["shadow"] = shadow

    if not spec.get("background"):
        source = providers[0] if providers else f"site_config {CONF_KEY}"
        frappe.throw(f"{HOOK} ({source}) does not name a background colour.")

    return spec


# ── the compositor ───────────────────────────────────────────────────────────


def apply_finish(content, spec, client=None):
    """
    Put one rendered photo onto the house ground. Returns

        {"image": bytes, "mime": str, "cutout": bytes|None, "note": str|None}

    `content` is what the image service returned; `spec` is `load()`'s. `client`
    is the active `ai_client` (see `alaiy_os.engine.llm.image_client`), needed
    only when `spec["matte"]` is `photoroom` or `gemini` — never for `segment` or
    `flood`, which are both local. Touches no Frappe at all — it runs on a worker
    thread beside the render (see image_generation._try_generate), where there is
    no site context to read; `client` is resolved on the main thread and handed
    in for exactly that reason (see engine/ai_client.py's threading contract).

    Never raises and never approximates. If the render did not come back on a clean
    empty ground, `image` is `content` unchanged and `note` says the finish was
    skipped, because a bad cutout on a luxury piece is worse than an unfinished
    photograph — a halo or a bitten-off clasp is a misrepresentation, while a plain
    white background is merely off-brand.
    """
    try:
        return _finish(content, spec, client)
    except Exception as exc:
        return _skipped(content, f"could not be processed ({exc})")


def finish_capability(spec):
    """Which `ai_client.image_support()` capability `apply_finish` needs for
    this style's matte, or None when the matte is local (`segment`/`flood`)
    and never calls out. Read by image_generation.py both to decide whether to
    resolve a client at all, and to gate-check it for the right capability.

    `photoroom` matting is Photoroom's `remove_background` endpoint; `gemini`
    and `gemini_full` matting are both an ordinary `generate_image` call (the
    same one a generative retouch makes) — `gemini` asks it to isolate rather
    than retouch, `gemini_full` asks it to finish the photo outright.
    """
    if not spec:
        return None
    matte = spec.get("matte") or DEFAULTS["matte"]
    if matte == "photoroom":
        return "remove_background"
    if matte in ("gemini", "gemini_key", "gemini_full"):
        return "generate"
    return None


def _finish(content, spec, client):
    matte = spec.get("matte") or DEFAULTS["matte"]

    if matte == "photoroom":
        return _finish_photoroom(content, spec, client)
    if matte == "gemini_full":
        return _finish_gemini_full(content, spec, client)

    image = Image.open(io.BytesIO(content))
    image.load()
    image = image.convert("RGB")

    if matte == "segment":
        alpha = _segment_alpha(image, spec.get("segment_model") or DEFAULTS["segment_model"])
        alpha = _repair(image, alpha)
    elif matte == "gemini":
        if not client:
            return _skipped(content, "no background/matting provider is configured")
        alpha = _gemini_mask(client, image, spec)
    elif matte == "gemini_key":
        if not client:
            return _skipped(content, "no background/matting provider is configured")
        # A photo whose own colours leave no key clear, or a render that did not
        # come back on a clean key, is matted the `gemini` way instead.
        alpha = _gemini_keyed(client, image)
        if alpha is None:
            alpha = _gemini_mask(client, image, spec)
    else:
        # The flood needs the ground to already be clean; the model does not.
        uneven = _ground_complaint(image)
        if uneven:
            return _skipped(content, uneven)
        alpha = _subject_alpha(image)
        if alpha is None:
            return _skipped(content, "no background could be found along the edge of the photo")

    subject = _coverage(alpha)
    if subject < _MIN_SUBJECT:
        return _skipped(content, "almost nothing was left after separating the product")
    if subject > _MAX_SUBJECT:
        return _skipped(content, "no background could be separated from the product")
    if _featureless(image, alpha):
        return _skipped(content, "no product could be made out in the photo")

    box = alpha.getbbox()
    if not box:
        return _skipped(content, "no product could be separated from the background")

    cut = _cut_edges(alpha) if spec.get("bleed_cut_edges") else frozenset()

    cutout = image.convert("RGBA")
    cutout.putalpha(alpha)
    cutout = cutout.crop(box)

    return {
        "image": _encode(_compose(cutout, image.size, spec, cut)),
        "mime": "image/png",
        "cutout": _encode(cutout) if spec.get("keep_cutout") else None,
        "note": None,
    }


# ── the Photoroom finish ──────────────────────────────────────────────────

# Photoroom's AI shadow has no literal offset/opacity knobs (see
# `engine/ai_client.py`'s PHOTOROOM_SHADOW_MODES) — the closest it exposes is a
# hard/soft edge plus an intensity. A blur this small or smaller reads as
# "hard"; the house style's own DEFAULTS (blur=0.03) sits above it on purpose,
# to get Photoroom's ai.soft.
_PHOTOROOM_HARD_BLUR_MAX = 0.02

# The two shadow.*Override fields that pin the shadow's geometry, not just its
# darkness — sent alongside shadow_intensity, never on their own (Photoroom's
# override mode needs at least one; this module always supplies all three
# together). Left unset, a first production photo came back with a shadow at
# an inconsistent angle and length, because Photoroom guessed both itself.
#
# "short" (Photoroom's own 10° preset): the shortest, tightest shadow the
# override exposes — matching "a short drop... sitting on the surface, not
# floating" (see DEFAULTS["shadow"]) far better than the longer presets, which
# read as a raking, elongated shadow rather than a contact shadow.
_PHOTOROOM_SHADOW_SPREAD = "short"
# "behind": light from the front, shadow directly behind/below the subject —
# not off to a side, which is what a "behindLeft"/"behindRight" preset (or an
# unset direction, left to Photoroom's own guess) would produce.
_PHOTOROOM_SHADOW_DIRECTION = "behind"


def _finish_photoroom(content, spec, client):
    """The Photoroom equivalent of `_finish`'s segment/flood branches, in one
    round trip instead of a local mask plus Pillow compositing.

    Two calls, not one, and deliberately in this order:

      1. A transparent cutout, cropped tight to the subject
         (`outputSize=croppedSubject`) — this both measures the product's own
         pixel size (there is no local mask to read it from any more) and IS
         the `keep_cutout` artifact, so asking for it is never wasted work.
      2. The finish itself: matted, given the house background colour and an
         AI shadow, at a canvas size and padding computed from (1) using
         EXACTLY the padding/aspect/max_size arithmetic `_compose` used to use
         — so the product's scale relative to the rest of the catalog, and the
         floor-not-target reading of `padding`, are unchanged by moving the
         compositing itself off this module and onto Photoroom. The padding is
         sent as four exact pixel values (not a fraction), which pins the
         product's on-canvas size — Photoroom is not left to decide how much
         to scale it to "fill" the frame.

    Needs a live Photoroom key to verify the exact placement behaviour this
    relies on (that explicit `outputSize` + pixel `paddingSides` together fully
    pin the subject's size and position) — see the module docstring's note on
    where this integration came from and check a real product photo against it
    before relying on it in production.
    """
    if not client:
        return _skipped(content, "no background/matting provider is configured")

    # Re-encoded as PNG rather than sent as-is: `content` may be whatever format
    # the image service (or the original photo) used, and re-encoding through
    # Pillow here means this never has to guess a media type for the data URI —
    # every other caller of this module (`_encode`) already treats PNG as the
    # standard interchange format.
    source = Image.open(io.BytesIO(content))
    source.load()
    frame_w, frame_h = source.size
    data_uri = f"data:image/png;base64,{base64.b64encode(_encode(source.convert('RGB'))).decode('ascii')}"

    cutout_bytes, _ = _photoroom_call(client, data_uri, output_size="croppedSubject")
    cutout = Image.open(io.BytesIO(cutout_bytes))
    cutout.load()
    if cutout.mode != "RGBA" or not cutout.getbbox():
        return _skipped(content, "no product could be separated from the background")

    width, height = cutout.size
    padding = float(spec.get("padding", DEFAULTS["padding"]))
    aspect = float(spec.get("aspect") or DEFAULTS["aspect"])
    max_size = int(spec.get("max_size") or DEFAULTS["max_size"])
    usable = max(1.0 - 2.0 * padding, 0.05)

    # Same formula _compose used: the canvas starts at the size of the photo the
    # product was shot in (so a photo that already has room keeps its own
    # framing) and only grows past that to satisfy the padding floor.
    canvas_h = max(frame_h, frame_w / aspect, height / usable, width / (usable * aspect))
    canvas_w = canvas_h * aspect

    longest = max(canvas_w, canvas_h)
    if longest > max_size:
        scale = max_size / longest
        canvas_w *= scale
        canvas_h *= scale
        width, height = max(1, round(width * scale)), max(1, round(height * scale))

    canvas_w, canvas_h = max(1, round(canvas_w)), max(1, round(canvas_h))
    pad_left = (canvas_w - width) // 2
    pad_top = (canvas_h - height) // 2
    # The remainder, not a second halving — so left+right add up to EXACTLY
    # canvas_w - width even when that is odd, and the product is not shifted by
    # a rounding pixel that would show up as an off-centre crop on review.
    pad_right = canvas_w - width - pad_left
    pad_bottom = canvas_h - height - pad_top

    shadow = dict(DEFAULTS["shadow"], **(spec.get("shadow") or {}))
    opacity = float(shadow.get("opacity") or 0)
    mode = "none" if opacity <= 0 else ("hard" if float(shadow.get("blur") or 0) <= _PHOTOROOM_HARD_BLUR_MAX else "soft")

    finished_bytes, finished_media_type = _photoroom_call(
        client,
        data_uri,
        background_color=spec["background"],
        shadow=mode,
        shadow_intensity=opacity if mode != "none" else None,
        # "Short" + "behind": a tight, near-vertical contact shadow directly
        # under the product — see _PHOTOROOM_SHADOW_SPREAD/_DIRECTION. Without
        # these Photoroom guesses the shadow's angle and length per photo,
        # which is what read as "improper" against a real product photo.
        shadow_spread=_PHOTOROOM_SHADOW_SPREAD if mode != "none" else None,
        shadow_direction=_PHOTOROOM_SHADOW_DIRECTION if mode != "none" else None,
        output_size=f"{canvas_w}x{canvas_h}",
        padding_sides={
            "top": f"{pad_top}px",
            "bottom": f"{pad_bottom}px",
            "left": f"{pad_left}px",
            "right": f"{pad_right}px",
        },
    )

    return {
        "image": finished_bytes,
        "mime": finished_media_type,
        "cutout": cutout_bytes if spec.get("keep_cutout") else None,
        "note": None,
    }


def _photoroom_call(client, data_uri, **kwargs):
    """One `remove_background` round trip -> (raw bytes, media_type).

    Thin wrapper so `_finish_photoroom` reads as two calls rather than two
    b64-decodes; the seam itself is `alaiy_os.engine.llm.remove_background`'s
    contract (`{"b64", "media_type"}`), reached here via the client instance
    handed down from the main thread — see `apply_finish`'s docstring on why
    this never resolves its own client.
    """
    result = client.remove_background(data_uri, **kwargs)
    return base64.b64decode(result["b64"]), result.get("media_type") or "image/png"


def _segment_alpha(image, model):
    """An opacity mask for the product, from a segmentation model.

    The model is only ever asked for the MASK — `only_mask=True`. It never gets to
    compose or repaint anything, so whatever it decides about the edges, the pixels
    that survive are the photograph's own: the background changes and the product
    cannot. Kept as the local fallback for exactly that guarantee, for a site with
    no Photoroom key.

    Alpha matting is deliberately off. rembg can refine the edge with it, at rather
    more than double the time, and on this catalog's photography it made no visible
    difference to the thing it would be for — a chain strap against white.
    """
    from rembg import remove

    return remove(image, session=_session(model), only_mask=True, post_process_mask=True)


# The cheaper of the two Gemini image tiers this codebase has used, not the
# "studio-quality" one `alaiy_os_thesolist`'s WORN_PHOTO_MODEL pins — and
# deliberately so. That constant's own comment records why worn-photo
# generation needed the pro tier: the cheap tier "kept producing illegible
# watch numerals" on a rendered dial. That failure mode cannot happen here —
# `_gemini_isolated`'s render is discarded below except for a flood-fill over
# it, never shown to a customer — so there is no reason to pay the pro tier's
# cost for a mask nobody looks at. "google/" routes the billing service
# straight to Google rather than through OpenRouter.
_GEMINI_MASK_MODEL = "google/gemini-3.1-flash-image"

# Told the house's own hex rather than "white" or "a neutral colour": asking for
# the exact background the finished photo will use means the ground Gemini
# returns already passes `_ground_complaint`'s paleness/evenness check on the
# colour a real house style actually wants, not a colour this module has to
# convert on the way in.
#
# Deliberately short. An earlier version of this prompt spelled out every
# constraint at length (an exhaustive "no gradient, no vignette, no surface,
# no horizon line..." list, plus "every pixel of the product itself must read
# as identical to the original") and Gemini would come back with a visibly
# patchy ground on a busy original backdrop. A one-line ask — background
# colour, keep the product as-is, no shadow — is what a plain manual test
# against the same photo separated cleanly; the elaborate phrasing was making
# the model's job harder, not easier. No shadow is still asked for, unlike
# that manual test: this module draws its own house shadow afterward (see
# `_cast_shadow`), and a shadow in Gemini's render would get read as part of
# the product by the flood-fill below, pasting a chunk of the real backdrop
# into the finished photo where the fake shadow was.
_GEMINI_ISOLATE_PROMPT = (
    "Put this exact product photo on a plain, even {hex} background. Keep the "
    "product exactly as it is - do not retouch, restyle, or redraw it. Do not "
    "add any shadow, reflection, or texture to the background."
)


def _gemini_mask(client, image, spec):
    """The `gemini` matte's alpha for `image`: Gemini isolates the product onto
    the house ground and the ground is flooded in from the edge."""
    mask_source = _gemini_isolated(client, image, spec["background"])

    # The same believability check `flood` makes on a real photo, made here
    # on Gemini's render instead — Gemini can be told to make its ground
    # clean, but is not always able to: a strongly patterned or richly
    # coloured original backdrop can come back from Gemini still uneven
    # enough to fail this. That is exactly the case `segment` never cared
    # about — a real segmentation model reads the product regardless of
    # what is behind it — so rather than skip a photo Gemini could not
    # clean up, fall back to the local model for THIS photo only. Gemini
    # still gets to fix what it is here for (the holes ISNet punches
    # through a metal bracelet or chain on an ordinary clean photo).
    if _ground_complaint(mask_source):
        alpha = _repair(
            image, _segment_alpha(image, spec.get("segment_model") or DEFAULTS["segment_model"])
        )
    else:
        alpha = _subject_alpha(mask_source)
    if alpha is None:
        # No point on the render's edge is its ground — the product covers
        # the whole border. Same fallback as above.
        alpha = _repair(
            image, _segment_alpha(image, spec.get("segment_model") or DEFAULTS["segment_model"])
        )
    elif alpha.size != image.size:
        # Gemini is not contracted to return the exact pixel dimensions
        # it was handed, only the same framing — resize the MASK to
        # match the original, never the other way around, since the
        # cutout below is cropped from `image`, not from Gemini's
        # render.
        alpha = alpha.resize(image.size, Image.LANCZOS)
    return alpha


def _gemini_isolated(client, image, background_hex, prompt=_GEMINI_ISOLATE_PROMPT):
    """Gemini's placement of this photo's product onto the house ground.

    Used for exactly one thing below: a flood-fill run over it to find where
    the product is. Whatever Gemini actually drew for the product itself never
    reaches the finished photo — `_finish` crops the cutout from the CALLER's
    own `image` (the untouched original), using this render only for its alpha.
    That is the same guarantee `_segment_alpha`'s `only_mask=True` gives, kept a
    different way for a provider that has no "give me a mask" mode.
    """
    reference = f"data:image/png;base64,{base64.b64encode(_encode(image)).decode('ascii')}"
    result = client.generate_image(
        prompt.format(hex=background_hex),
        reference_data_uri=reference,
        model=_GEMINI_MASK_MODEL,
    )
    mask_source = Image.open(io.BytesIO(base64.b64decode(result["b64"])))
    mask_source.load()
    return mask_source.convert("RGB")


# ── the gemini_key matte ─────────────────────────────────────────────────────
#
# `gemini` floods the render's ground in from the frame's edge, which cannot reach
# ground the product encloses — the inside of a bangle, the loop of a cord
# bracelet, the gaps between a pendant's petals. It must not: on a pale ground a
# pearl or a diamond's table is the ground's colour too, and only connectivity
# tells them apart. So those gaps were kept as "product", and the original
# photo's own backdrop showed through them on the finished ground.
#
# Put the render on a colour no part of the product is, and colour alone is
# enough: every pixel of the key is ground wherever it is, enclosed or not. The
# cutout is still cropped from the original photo; only the alpha comes from the
# render.

# The keys tried, in order of preference. Vivid primaries, because a photographed
# product almost never contains one at full saturation.
_KEY_COLORS = ("#ff00ff", "#00ff00", "#0000ff")

# 1-norm distance from a key at which a pixel of the ORIGINAL photo counts as
# that key's colour, and the share of the photo allowed to be — above it the key
# is not clear of the product, and the next key is tried. Measured on a 256px
# thumbnail.
_KEY_CLASH = 200
_KEY_MAX_CLASH = 0.002

# How the render's key becomes alpha, in 1-norm distance from the key colour the
# render actually used: fully ground inside _KEY_IN, fully product past
# _KEY_OUT, a ramp between them for the antialiased edge.
_KEY_IN = 60
_KEY_OUT = 140

# How far the render's own ground may land from the requested key and still be
# taken as that key.
_KEY_MAX_DRIFT = 120

_GEMINI_KEY_PROMPT = (
    "Put this exact product photo on a plain, even {hex} background. Keep the "
    "product exactly as it is - do not retouch, restyle, or redraw it. Fill every "
    "gap and opening where the background shows through the product with the same "
    "{hex}. Do not add any shadow, reflection, or texture to the background."
)


def _gemini_keyed(client, image):
    """The `gemini_key` matte's alpha for `image`, or None when this photo cannot
    be keyed: none of `_KEY_COLORS` is clear of its colours, or the render did
    not come back on a clean key.

    Where the original photo is itself near the key, the pixel stays product
    whatever the render shows — a key that clashes with a sliver of the product
    must not cut that sliver out.
    """
    key = _pick_key(image)
    if key is None:
        return None
    render = _gemini_isolated(client, image, key, prompt=_GEMINI_KEY_PROMPT)

    ring = _border_ring(render.size)
    if ring is None:
        return None
    ground = _ground_mask(render, ring)
    ring_pixels = ImageStat.Stat(ring).sum[0] / 255.0
    if ImageStat.Stat(ground).sum[0] / 255.0 < _BORDER_MIN_GROUND * ring_pixels:
        return None
    rendered_key = tuple(int(v) for v in ImageStat.Stat(render, ring).median)
    if _distance_to(Image.new("RGB", (1, 1), rendered_key), _rgb(key)).getpixel((0, 0)) > _KEY_MAX_DRIFT:
        return None

    span = _KEY_OUT - _KEY_IN
    alpha = _distance_to(render, rendered_key).point(
        lambda v: 0 if v <= _KEY_IN else 255 if v >= _KEY_OUT else round((v - _KEY_IN) * 255 / span)
    )
    if alpha.size != image.size:
        alpha = alpha.resize(image.size, Image.LANCZOS)

    keep = _distance_to(image, _rgb(key)).point(lambda v: 255 if v < _KEY_OUT else 0)
    return ImageChops.lighter(alpha, keep)


def _pick_key(image):
    """The first of `_KEY_COLORS` the photo's own colours leave clear, or None."""
    small = image.copy()
    small.thumbnail((256, 256))
    for key in _KEY_COLORS:
        near = _distance_to(small, _rgb(key)).point(lambda v: 255 if v < _KEY_CLASH else 0)
        if ImageStat.Stat(near).mean[0] / 255.0 <= _KEY_MAX_CLASH:
            return key
    return None


def _distance_to(image, color):
    """Per-pixel 1-norm distance from `color`, clipped at 255 (past every
    threshold it is compared with)."""
    r, g, b = ImageChops.difference(image, Image.new("RGB", image.size, color)).split()
    return ImageChops.add(ImageChops.add(r, g), b)


# The pro tier, unlike `_GEMINI_MASK_MODEL` — and for the mirror-image reason.
# `_finish_gemini_full`'s render is NOT discarded; it ships to the customer
# as-is, dial numerals included, which is exactly the case
# `alaiy_os_thesolist`'s WORN_PHOTO_MODEL comment says the cheap tier fails on.
_GEMINI_FULL_FINISH_MODEL = "google/gemini-3-pro-image"

_GEMINI_FULL_FINISH_PROMPT = (
    "Put this exact product photo on a plain, even {hex} background, with "
    "soft, natural shadows. Keep the product exactly as it is - do not "
    "retouch, restyle, or redraw it."
)


def _finish_gemini_full(content, spec, client):
    """The whole finish — background AND shadow — done by Gemini in one call.

    The simplest of the five matte paths, and the only one where Gemini's own
    pixels reach the customer: nothing here re-crops from the original or
    composites a house-exact shadow, so there is no guarantee the product
    itself survived untouched the way `segment`/`gemini`/`flood`/`photoroom`
    all give. See the module docstring's `gemini_full` entry for why that is a
    considered trade rather than an oversight.

    Two things are corrected afterward: the ground colour, in place — see
    `_snap_background` — and the frame, grown to the house margin and aspect
    — see `_frame_to_spec`. If the render has no plain ground to correct, the
    finish is skipped rather than shipped on the wrong background.

    No mask means no cutout to keep: `spec["keep_cutout"]` has no effect on
    this path, `cutout` is always None.
    """
    if not client:
        return _skipped(content, "no background/matting provider is configured")

    image = Image.open(io.BytesIO(content))
    image.load()
    image = image.convert("RGB")
    reference = f"data:image/png;base64,{base64.b64encode(_encode(image)).decode('ascii')}"

    result = client.generate_image(
        _GEMINI_FULL_FINISH_PROMPT.format(hex=spec["background"]),
        reference_data_uri=reference,
        model=_GEMINI_FULL_FINISH_MODEL,
    )
    finished = Image.open(io.BytesIO(base64.b64decode(result["b64"])))
    finished.load()

    snapped = _snap_background(finished.convert("RGB"), spec["background"])
    if snapped is None:
        return _skipped(content, "the rendered photo did not come back on a plain background to recolour")

    framed = _frame_to_spec(snapped, spec)

    return {
        "image": _encode(framed),
        "mime": "image/png",
        "cutout": None,
        "note": None,
    }


# How the ground of a gemini_full render is pulled onto the exact house hex.
#
# Within _SNAP_EXACT (plain RGB distance from the ground colour Gemini used) a
# pixel becomes the hex exactly, blending out to _SNAP_CORE. Kept to a couple of
# levels on purpose: the faint outer edge of a soft shadow is also close to the
# ground, and a wider snap flattened it — at 8/16 a light shadow lost a fifth
# of its area and gained a hard edge. Past this the hue correction below still
# takes the ground onto the hex on average; each pixel just keeps its own grain.
# A ramp, not a cut-off, so the snap's own edge draws no ring either.
#
# Beyond that, background is recognised by HUE, not by brightness: a shadow is
# the ground made darker, so scaled back up to the ground's brightness it is the
# ground again. _SNAP_HUE_IN/_OUT are that scaled distance — full correction
# inside the first, fading to none at the second, so there is no line where it
# stops. Keying on brightness instead left the middle of the shadow in
# Gemini's own tint.
_SNAP_EXACT = 3
_SNAP_CORE = 6
_SNAP_HUE_IN = 20
_SNAP_HUE_OUT = 36

# Past this, Gemini did not put the photo on anything like the requested colour
# (it returned the original backdrop, say), and there is no plain ground to
# recolour — shifting a marble table toward grey would be worse than skipping.
_SNAP_MAX_DRIFT = 60


def _snap_background(image, hex_color):
    """`image` with its background pulled onto exactly `hex_color`, or None.

    Gemini lands near the requested colour, not on it. Rather than rebuild the
    photo — which would re-frame it and hand the product's edges to a mask —
    only the ground and its shadow are touched: the region connected to the
    frame edge whose hue matches the ground Gemini used. They get the
    per-channel correction that takes that ground onto the hex, so the shadow
    keeps its shape and depth but sits on the new colour. The product and its
    framing are left as drawn.

    Neutral steel has the ground's hue too, so a bracelet running off the frame
    gets the same small correction. That is the same colour-cast fix the ground
    gets, not a change to the piece: the correction is only ever as big as the
    gap between Gemini's ground and the hex.

    The ground colour is the median of the border ring, which stays right when
    the product runs off one or two edges — they are a minority of the ring.
    """
    import numpy as np
    from scipy import ndimage

    pixels = np.asarray(image, dtype=np.float32)
    height, width = pixels.shape[:2]
    ring = max(1, int(min(width, height) * _BORDER_FRACTION))
    if width <= ring * 2 or height <= ring * 2:
        return None

    border = np.ones((height, width), dtype=bool)
    border[ring:-ring, ring:-ring] = False
    ground = np.median(pixels[border], axis=0)
    target = np.array(_rgb(hex_color), dtype=np.float32)
    if float(np.linalg.norm(ground - target)) > _SNAP_MAX_DRIFT:
        return None

    distance = np.linalg.norm(pixels - ground, axis=2)
    brightness = pixels.sum(axis=2, keepdims=True)
    at_ground_brightness = pixels * (ground.sum() / np.maximum(brightness, 1.0))
    hue_distance = np.linalg.norm(at_ground_brightness - ground, axis=2)

    # Only ground reachable from the frame edge: a pale highlight or a white
    # stone enclosed by the product is not background, whatever its colour.
    near, _ = ndimage.label(hue_distance <= _SNAP_HUE_OUT)
    edge_labels = np.unique(np.concatenate([near[0], near[-1], near[:, 0], near[:, -1]]))
    region = np.isin(near, edge_labels[edge_labels > 0])

    ratio = target / np.maximum(ground, 1.0)
    corrected = np.clip(pixels * ratio, 0, 255)
    weight = np.clip((_SNAP_HUE_OUT - hue_distance) / (_SNAP_HUE_OUT - _SNAP_HUE_IN), 0, 1)
    weight = np.where(region, weight, 0.0)[..., None]

    out = pixels + weight * (corrected - pixels)
    exact = np.clip((_SNAP_CORE - distance) / (_SNAP_CORE - _SNAP_EXACT), 0, 1)
    exact = np.where(region, exact, 0.0)[..., None]
    out = out + exact * (target - out)
    return Image.fromarray(np.round(out).astype(np.uint8), "RGB")


# What counts as the product when a gemini_full render is measured for its
# margin: plain RGB distance from the house ground past _PAD_PRODUCT_DISTANCE,
# minus shadow (darker than the ground, same hue within _SNAP_HUE_IN). Low on
# purpose — a white strap on #f4f4f4 is only a few levels off the ground, and
# its outline is what has to be found. A row or column needs _PAD_MIN_RUN of
# the frame's width in such pixels (at least 3) to count, so ground grain
# doesn't.
_PAD_PRODUCT_DISTANCE = 10
_PAD_MIN_RUN = 0.002

# A side the product is closer to than this, in pixels, is one it runs off —
# a strap cut by the frame on purpose. That side is left flush: growing the
# ground past it would leave the strap ending in mid-air.
_PAD_BLEED = 1

# Over how much of the new band, as a fraction of the finished canvas, the
# render's own edge fades onto the flat hex. A shadow Gemini drew right to the
# frame edge would otherwise stop in a hard line where the new ground starts.
_PAD_FADE = 0.03


def _frame_to_spec(image, spec):
    """`image` on a canvas of the house aspect, with the product clear of `padding`.

    The gemini_full path's one concession to the house frame. Gemini frames the
    photo itself: it returns whatever shape it likes, and sometimes a complete
    piece — a watch with both strap ends in shot — comes back with those ends a
    hair off the frame, which reads as crowded (slide 7). This measures the
    product, adds plain ground on each side that is inside the floor without
    running off it, then grows the ground again until the canvas is `aspect`.

    Same floor-not-target reading as `_compose`: the render is never scaled up
    and a margin never drops below the floor. A side the product runs off stays
    flush, so a strap the frame cuts on purpose stays cut. The one case that
    cannot be met by adding ground alone is a short side the product runs off
    at both ends (a landscape render of a strap cut top and bottom): there,
    spare ground is trimmed off the long side first, and only what that cannot
    cover is added across the cut — the canvas is always `aspect`.
    """
    import numpy as np

    padding = max(float(spec.get("padding", DEFAULTS["padding"])), 0.0)
    aspect = float(spec.get("aspect") or DEFAULTS["aspect"])

    pixels = np.asarray(image, dtype=np.float32)
    height, width = pixels.shape[:2]
    target = np.array(_rgb(spec["background"]), dtype=np.float32)

    distance = np.linalg.norm(pixels - target, axis=2)
    brightness = pixels.sum(axis=2, keepdims=True)
    at_ground_brightness = pixels * (target.sum() / np.maximum(brightness, 1.0))
    shadow = (brightness[..., 0] < target.sum()) & (
        np.linalg.norm(at_ground_brightness - target, axis=2) <= _SNAP_HUE_IN
    )
    product = (distance > _PAD_PRODUCT_DISTANCE) & ~shadow

    run = max(3, round(max(width, height) * _PAD_MIN_RUN))
    rows = np.flatnonzero(product.sum(axis=1) >= run)
    cols = np.flatnonzero(product.sum(axis=0) >= run)
    # Clear ground on each side: top, bottom, left, right. With no product
    # found every side is all ground — the canvas is still squared, just
    # never trimmed.
    if len(rows) and len(cols):
        margins = [rows[0], height - 1 - rows[-1], cols[0], width - 1 - cols[-1]]
    else:
        margins = [height, height, width, width]
    bleeds = [margin <= _PAD_BLEED for margin in margins]

    def grow(near, far, size):
        """New (near, far) margins along one axis, each at least the floor."""
        extent = size - near - far
        bleed_near, bleed_far = near <= _PAD_BLEED, far <= _PAD_BLEED
        if padding <= 0 or (bleed_near and bleed_far) or extent >= size:
            return near, far
        new_near, new_far = near, far
        # The floor is a fraction of the grown canvas, so a few rounds settle it.
        for _ in range(8):
            total = extent + new_near + new_far
            new_near = near if bleed_near else max(near, padding * total)
            new_far = far if bleed_far else max(far, padding * total)
        return new_near, new_far

    top, bottom = grow(margins[0], margins[1], height)
    left, right = grow(margins[2], margins[3], width)
    # Signed, per side: ground added (positive) or trimmed (negative).
    add = [top - margins[0], bottom - margins[1], left - margins[2], right - margins[3]]

    # Then to the house aspect. The short axis takes the extra on the sides the
    # product does not run off; failing that, the long axis gives up spare ground.
    new_h = height + add[0] + add[1]
    new_w = width + add[2] + add[3]
    if new_w / new_h < aspect:
        short, long_, extra = (2, 3), (0, 1), new_h * aspect - new_w
        long_size, to_long = new_h, 1 / aspect
    else:
        short, long_, extra = (0, 1), (2, 3), new_w / aspect - new_h
        long_size, to_long = new_w, aspect
    if extra >= 0.5:
        open_sides = [side for side in short if not bleeds[side]]
        if open_sides:
            for side in open_sides:
                add[side] += extra / len(open_sides)
        else:
            # Trim the long axis toward the size the short one already is,
            # never past the floor of the canvas that leaves.
            short_size = long_size - extra * to_long
            floor = padding * short_size
            spare = {
                side: max(margins[side] + add[side] - floor, 0) for side in long_ if not bleeds[side]
            }
            needed = long_size - short_size
            # Evenly where both sides have room, the rest from whichever does.
            open_long = sorted(spare, key=spare.get)
            for index, side in enumerate(open_long):
                cut = min(spare[side], needed / (len(open_long) - index))
                add[side] -= cut
                needed -= cut
            long_size = short_size + needed
            short_now = sum(add[side] for side in short) + (width if short == (2, 3) else height)
            # What trimming could not cover goes across the cut, split evenly.
            for side in short:
                add[side] += (long_size / to_long - short_now) / 2

    top_add, bottom_add, left_add, right_add = (round(value) for value in add)
    if not any((top_add, bottom_add, left_add, right_add)):
        return image

    # Trim first (a negative side), then grow (a positive one).
    cropped = pixels[
        max(-top_add, 0) : height - max(-bottom_add, 0),
        max(-left_add, 0) : width - max(-right_add, 0),
    ]
    inner_h, inner_w = cropped.shape[:2]
    pad_top, pad_bottom, pad_left, pad_right = (max(value, 0) for value in (top_add, bottom_add, left_add, right_add))
    grown = np.pad(cropped, ((pad_top, pad_bottom), (pad_left, pad_right), (0, 0)), mode="edge")

    grown_h, grown_w = grown.shape[:2]
    ys = np.arange(grown_h)[:, None]
    xs = np.arange(grown_w)[None, :]
    outside = np.maximum(
        np.maximum(pad_top - ys, ys - (pad_top + inner_h - 1)).clip(0),
        np.maximum(pad_left - xs, xs - (pad_left + inner_w - 1)).clip(0),
    )
    fade = max(1.0, max(grown_w, grown_h) * _PAD_FADE)
    weight = np.clip(outside / fade, 0, 1)[..., None]
    grown = grown + weight * (target - grown)
    framed = Image.fromarray(np.round(grown).astype(np.uint8), "RGB")

    # Rounding each side can leave the canvas a pixel off; settle it exactly.
    want_w = round(framed.height * aspect)
    if framed.width != want_w:
        settled = Image.new("RGB", (want_w, framed.height), _rgb(spec["background"]))
        settled.paste(framed, ((want_w - framed.width) // 2, 0))
        framed = settled
    return framed


def _session(model):
    """One rembg session per model, built once and shared.

    Building a session loads a ~180MB ONNX graph, which is far too expensive to do
    per photo, and the pool renders several photos at once. onnxruntime releases
    the GIL and its `Run` is safe to call from several threads, so the session is
    shared rather than made thread-local; only the building is serialised, so two
    threads arriving together cannot both pay for it.

    The model file itself is downloaded to ~/.rembg on first use. On a fresh bench
    that makes the very first photo slow rather than broken — see the README.
    """
    with _SESSION_LOCK:
        if model not in _SESSIONS:
            from rembg import new_session

            _SESSIONS[model] = new_session(model)
        return _SESSIONS[model]


def _repair(image, alpha):
    """The two things a segmentation mask reliably gets wrong, undone.

    Both are failures of the SAME kind and neither is a judgement about the piece:
    the model works on a 1024-square thumbnail of the photo, and the mask that comes
    back is stretched over the real thing. What that costs is holes it punched
    through the product and a rim of background colour left clinging to the edge —
    see `_fill_defect_holes` and `_pull_in_edge`.

    Only the mask is touched. Not one product pixel is read for anything except
    deciding which side of the cut it falls on, which keeps the guarantee the
    `segment` matte exists for: the background changes and the product does not.

    This is applied to the segmentation matte only. The flood matte cannot punch a
    hole in a product — it reaches background connected to the frame edge and
    nothing else — and it has its own feather already.
    """
    return _pull_in_edge(_fill_defect_holes(image, alpha))


def _fill_defect_holes(image, alpha):
    """Holes the mask punched through the product itself, made opaque again.

    A segmentation mask working from a thumbnail drops patches out of the middle of
    large, evenly-toned areas — the ribbed black rubber of a watch strap is the case
    this catalog hits, and it arrives on the finished image as bites of background
    grey taken out of the strap.

    The fix cannot be "fill every enclosed hole", which is the obvious
    implementation and does real damage: the gap inside the chain handle of a
    shoulder bag is an enclosed hole too, and filling it pastes a slab of the wood
    the bag was photographed on into the middle of an otherwise finished image.

    What separates them is colour. A hole punched through the strap IS the strap —
    its pixels and the strap's around it are the same black rubber. A gap you can
    genuinely see through shows whatever was behind the piece, which is the thing
    being removed and therefore looks nothing like it. So every hole is compared
    against the product immediately around it, and only the ones that match are
    filled. `_HOLE_MATCH` carries the measurements.
    """
    import numpy as np
    from scipy import ndimage

    opaque = np.asarray(alpha) > 128
    enclosed = ndimage.binary_fill_holes(opaque) & ~opaque
    if not enclosed.any():
        return alpha

    holes, count = ndimage.label(enclosed)
    if not count:
        return alpha

    pixels = np.asarray(image, dtype=np.float32)
    repaired = np.array(alpha)
    filled = False

    # Each hole is measured inside its own bounding box rather than across the whole
    # frame: there are only ever a handful of them, and on a 3000x4500 photograph a
    # full-frame dilation per hole costs more than the entire matte did.
    for label, box in enumerate(ndimage.find_objects(holes), start=1):
        if box is None:
            continue
        near = tuple(
            slice(max(0, axis.start - _HOLE_RING), min(size, axis.stop + _HOLE_RING))
            for axis, size in zip(box, opaque.shape, strict=True)
        )

        hole = holes[near] == label
        if hole.sum() < _HOLE_MIN_PIXELS:
            continue

        # The product immediately around this hole, and only around this hole.
        ring = ndimage.binary_dilation(hole, iterations=_HOLE_RING) & ~hole & opaque[near]
        if not ring.any():
            continue

        patch = pixels[near]
        if float(np.linalg.norm(patch[hole].mean(axis=0) - patch[ring].mean(axis=0))) > _HOLE_MATCH:
            continue

        repaired[near][hole] = 255
        filled = True

    return Image.fromarray(repaired) if filled else alpha


def _pull_in_edge(alpha):
    """The matte pulled in a little, so the rim of old background falls outside it.

    Where the mask's edge lands, a pixel is part product and part whatever the
    product was photographed on — and at the scale the model works at, "a pixel" of
    mask is several of the photograph. Composite that rim onto the house grey and it
    reads as an outline in the colour of the backdrop: a watch shot on an orange
    table keeps a thin orange line all the way around its case.

    Pulling the cut in by the width of that blend drops those pixels instead of
    shipping them. It costs a sliver of genuine edge, which is the right trade —
    nobody can see a missing half-millimetre of case, and everybody can see a halo.

    It is NOT a fix for colour the photograph really contains. A polished case
    standing next to an orange backdrop reflects it, and that reflection is metres
    of real product surface rather than a rim of edge pixels. No matte can remove
    it, and this does not try to.
    """
    pull = round(_EDGE_PULL * max(alpha.size) / 1024.0)
    if pull < 1:
        return alpha

    pulled = alpha
    for _ in range(pull):
        # Repeated 3x3 minimum: each pass retreats the edge by one pixel.
        pulled = pulled.filter(ImageFilter.MinFilter(3))
    # The erosion leaves the same hard staircase the flood does, and wants the same
    # sub-pixel softening for the same reason.
    return pulled.filter(ImageFilter.GaussianBlur(_EDGE_FEATHER))


def _ground_complaint(image):
    """Why this photo's edge is not the empty ground we asked for, or None.

    Only the border ring is judged. What is inside the frame is the product's
    business — a dark dial or a black strap says nothing about whether the ground
    behind it is clean.

    And only the ground within the ring: a product that runs out of the shot (a
    strap cropped at the top and bottom) crosses the ring, and measured together
    with the ground it reads as a badly uneven background. So the ring's pixels
    near its median colour are taken as the ground and judged on their own, and
    they must make up most of the ring — a patterned or graded backdrop leaves too
    few of them to pass.
    """
    ring = _border_ring(image.size)
    if ring is None:
        return "the rendered photo is too small to finish"

    ground = _ground_mask(image, ring)
    ring_pixels = ImageStat.Stat(ring).sum[0] / 255.0
    if ImageStat.Stat(ground).sum[0] / 255.0 < _BORDER_MIN_GROUND * ring_pixels:
        return "the background of the rendered photo was not even enough to separate"

    stat = ImageStat.Stat(image, ground)
    if min(stat.mean) < _BORDER_MIN_MEAN:
        return "the rendered photo did not come back on a plain light background"
    if max(stat.stddev) > _BORDER_MAX_STDEV:
        return "the background of the rendered photo was not even enough to separate"
    return None


def _ground_mask(image, ring):
    """The pixels of `ring` within `_SEED_TOLERANCE` of the ring's median colour."""
    median = tuple(int(v) for v in ImageStat.Stat(image, ring).median)
    near = _distance_to(image, median).point(lambda v: 255 if v <= _SEED_TOLERANCE else 0)
    return ImageChops.multiply(near, ring)


def _border_ring(size):
    """A mask of the band around the frame's edge that counts as "the background",
    or None when the frame is too small to have one."""
    width, height = size
    ring = max(1, int(min(width, height) * _BORDER_FRACTION))
    if width <= ring * 2 or height <= ring * 2:
        return None

    # The ring, laid out as one strip: the two full-width bands plus what is left
    # of the sides between them.
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle([0, 0, width - 1, height - 1], fill=255)
    draw.rectangle([ring, ring, width - 1 - ring, height - 1 - ring], fill=0)
    return mask


def _subject_alpha(image):
    """An opacity mask for the product: the frame minus the ground touching its edge,
    or None when no point on the edge is ground.

    Flooded inward from the edge rather than keyed on a colour. A colour key is the
    obvious implementation and the wrong one for this catalog: white is not only the
    background here, it is also a pearl, the table of a diamond and the specular
    highlight down a polished band, and keying would punch every one of them out of
    the middle of the product. A flood only ever reaches background that is
    connected to the edge of the frame, so an enclosed white stays.

    Seeded only from edge points that are the ground — the median colour of the
    border ring, which the ground dominates even where the product crosses it. A
    fill seeded on the product itself (a strap running out of a corner of the shot)
    would take the product's colour for the ground and erase it.
    """
    mask = _border_ring(image.size)
    if mask is None:
        return None
    ground = tuple(int(v) for v in ImageStat.Stat(image, mask).median)

    flooded = image.copy()
    width, height = flooded.size
    pixels = image.load()
    seeded = False
    for xy in _edge_points(width, height):
        if sum(abs(a - b) for a, b in zip(pixels[xy], ground)) <= _SEED_TOLERANCE:
            ImageDraw.floodfill(flooded, xy, _FILL_COLOR, thresh=_FILL_TOLERANCE)
            seeded = True
    if not seeded:
        return None

    # "Filled" is "this pixel moved", not "this pixel is now magenta" — so a product
    # that genuinely contains the sentinel colour survives.
    moved = ImageChops.difference(flooded, image).convert("L")
    alpha = moved.point(lambda v: 0 if v > _FILL_DELTA else 255)
    return alpha.filter(ImageFilter.GaussianBlur(_EDGE_FEATHER))


def _edge_points(width, height):
    """Evenly spaced points along all four sides of the frame, corners included."""
    xs = sorted({round(i * (width - 1) / (_SEEDS_PER_EDGE - 1)) for i in range(_SEEDS_PER_EDGE)})
    ys = sorted({round(i * (height - 1) / (_SEEDS_PER_EDGE - 1)) for i in range(_SEEDS_PER_EDGE)})
    points = [(x, y) for x in xs for y in (0, height - 1)]
    points += [(x, y) for y in ys for x in (0, width - 1)]
    return list(dict.fromkeys(points))


def _cut_edges(alpha):
    """The sides of the frame the product runs out of, as a subset of
    {"left", "top", "right", "bottom"}.

    Only a side the product reaches within `_CUT_EDGE_REACH` of is looked at, and
    reaching it is not enough: a round bezel or a crown touching the side of a
    tight crop reaches it too, and setting that side flush pushes the whole piece
    off centre. A side counts when either

      * the product's outermost line on that side covers at least
        `_CUT_RUN_MIN` of its own extent along it — a crop cuts across the
        piece, where a curve meeting the side only touches it;
      * it covers less, but is as wide at that line as just inside it — a thin
        chain cropped straight across (see `_CUT_STRAIGHT_MIN`); or
      * the product runs out through a corner of it, next to a side that counts
        by the rules above — a strap leaving the shot diagonally crosses one
        side broadly and only clips the other.
    """
    solid = alpha.point(lambda v: 255 if v > 128 else 0)
    box = solid.getbbox()
    if not box:
        return frozenset()
    width, height = solid.size
    reach = max(1, round(min(width, height) * _CUT_EDGE_REACH))
    x0, y0, x1, y1 = box
    extent_w, extent_h = x1 - x0, y1 - y0

    def column(x):
        return solid.crop((x, y0, x + 1, y1))

    def row(y):
        return solid.crop((x0, y, x1, y + 1))

    def share(line):
        return ImageStat.Stat(line).mean[0] / 255.0

    near = {
        "left": x0 <= reach,
        "top": y0 <= reach,
        "right": x1 >= width - reach,
        "bottom": y1 >= height - reach,
    }
    outer = {
        "left": column(x0),
        "top": row(y0),
        "right": column(x1 - 1),
        "bottom": row(y1 - 1),
    }
    inner = {
        "left": column(min(x0 + reach, x1 - 1)),
        "top": row(min(y0 + reach, y1 - 1)),
        "right": column(max(x1 - 1 - reach, x0)),
        "bottom": row(max(y1 - 1 - reach, y0)),
    }

    def crosses(side):
        edge, inside = share(outer[side]), share(inner[side])
        if edge >= _CUT_RUN_MIN:
            return True
        return edge >= _CUT_THIN_MIN and edge >= _CUT_STRAIGHT_MIN * inside

    cut = {side for side in outer if near[side] and crosses(side)}

    # The corner rule: does the product's run along this side reach the end of it
    # that meets an already-cut side?
    ends = {
        "left": {"top": (0, 0, 1, reach), "bottom": (0, extent_h - reach, 1, extent_h)},
        "right": {"top": (0, 0, 1, reach), "bottom": (0, extent_h - reach, 1, extent_h)},
        "top": {"left": (0, 0, reach, 1), "right": (extent_w - reach, 0, extent_w, 1)},
        "bottom": {"left": (0, 0, reach, 1), "right": (extent_w - reach, 0, extent_w, 1)},
    }
    for side in ("left", "top", "right", "bottom"):
        if side in cut or not near[side]:
            continue
        for neighbour, end in ends[side].items():
            if neighbour in cut and outer[side].crop(end).getbbox():
                cut.add(side)
                break
    return frozenset(cut)


def _featureless(image, alpha):
    """True when what was selected has no detail in it, and so is not a product.

    Handed a blank or near-blank frame, a segmentation model does not answer "there
    is nothing here" — it invents a subject, and reliably the same one: on a plain
    white frame ISNet returns a confident blob over about 6% of the image, in the
    same place every time. Coverage bounds cannot catch that, because 6% is a
    perfectly ordinary size for a stud earring.

    What separates the two is texture. A real piece has structure inside its
    outline — an edge, a highlight, a change of tone somewhere. A hallucinated blob
    is a patch of the flat background it was cut from, and its standard deviation
    is essentially zero. So the selection is measured, not its size.
    """
    mask = alpha.point(lambda v: 255 if v > 128 else 0)
    if not mask.getbbox():
        return True
    return max(ImageStat.Stat(image, mask).stddev) < _MIN_SUBJECT_DETAIL


def _coverage(alpha):
    """What fraction of the frame the product occupies, 0..1."""
    width, height = alpha.size
    return ImageStat.Stat(alpha).sum[0] / (255.0 * width * height)


def _compose(cutout, frame, spec, cut=frozenset()):
    """The cutout on the house ground, with its margin and its shadow.

    `frame` is the size of the photo the cutout came out of, and it matters as much
    as the cutout does — see below. `cut` is the sides of that frame the product
    runs out of (see `_cut_edges`); on those sides the product is set flush to the
    canvas edge with no margin, so what the shot cropped still reads as cropped
    rather than as a piece that ends in mid-air.
    """
    shadow = dict(DEFAULTS["shadow"], **(spec.get("shadow") or {}))
    padding = float(spec.get("padding", DEFAULTS["padding"]))
    aspect = float(spec.get("aspect") or DEFAULTS["aspect"])
    max_size = int(spec.get("max_size") or DEFAULTS["max_size"])

    product = cutout
    width, height = product.size

    # The product is never resized to fit the canvas; the canvas is grown around the
    # product. That is the whole difference between a catalog where a stud reads as
    # small and one where every piece is blown up to the same width — fitting each
    # cutout to a fixed frame would put a 4mm earring and a 60mm hoop on the page at
    # the same size, which the guidelines explicitly rule out.
    #
    # So the canvas starts at the size of the photo the product was shot in, which is
    # what carries that relative scale, and only grows when the product sits closer to
    # an edge than the margin allows. A photo that already has room keeps its own
    # framing and its own resolution. Padding is a FLOOR on the empty space, never a
    # target, and the only resize in this whole module is downward, for max_size.
    #
    # A cut side takes no margin. When both opposite sides are cut but the canvas
    # still has to be larger than the product on that axis (to keep the aspect),
    # the product is centred on it, as it is when neither side is cut.
    def margin(side):
        return 0.0 if side in cut else padding

    usable_w = max(1.0 - margin("left") - margin("right"), 0.05)
    usable_h = max(1.0 - margin("top") - margin("bottom"), 0.05)
    frame_w, frame_h = frame
    canvas_h = max(frame_h, frame_w / aspect, height / usable_h, width / (usable_w * aspect))
    canvas_w = canvas_h * aspect

    longest = max(canvas_w, canvas_h)
    if longest > max_size:
        scale = max_size / longest
        canvas_w *= scale
        canvas_h *= scale
        product = product.resize(
            (max(1, round(width * scale)), max(1, round(height * scale))),
            Image.LANCZOS,
        )

    canvas_w, canvas_h = max(1, round(canvas_w)), max(1, round(canvas_h))
    width, height = product.size
    left = _place(canvas_w, width, "left" in cut, "right" in cut)
    top = _place(canvas_h, height, "top" in cut, "bottom" in cut)

    base = Image.new("RGB", (canvas_w, canvas_h), _rgb(spec["background"]))
    base = _cast_shadow(base, product, (left, top), shadow)
    base.paste(product, (left, top), product)
    return base


def _place(canvas, size, near_cut, far_cut):
    """Offset of the product along one axis: flush to whichever end is cut,
    centred when neither or both are."""
    if near_cut and not far_cut:
        return 0
    if far_cut and not near_cut:
        return canvas - size
    return (canvas - size) // 2


def _cast_shadow(base, product, position, shadow):
    """Drop the product's own silhouette onto the ground, below it.

    One offset copy of the alpha, blurred a little and held down to a low opacity —
    "hard, but light". There is deliberately no mirrored, fading second copy: the
    guidelines ask for a shadow and rule out a reflection, and the two are easy to
    conflate when reaching for a stock "product on a surface" effect.
    """
    opacity = float(shadow.get("opacity") or 0)
    if opacity <= 0:
        return base

    canvas_w, canvas_h = base.size
    left, top = position
    drop = round(canvas_h * float(shadow.get("offset") or 0))
    blur = canvas_h * float(shadow.get("blur") or 0)

    mask = Image.new("L", base.size, 0)
    mask.paste(product.getchannel("A"), (left, top + drop))
    if blur > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
    mask = mask.point(lambda v: round(v * opacity))

    base.paste(Image.new("RGB", base.size, _rgb(shadow.get("color") or "#000000")), (0, 0), mask)
    return base


def _rgb(color):
    """`#rrggbb` (or any Pillow colour name) as an (r, g, b) tuple."""
    if isinstance(color, list | tuple):
        return tuple(color[:3])
    from PIL import ImageColor

    return ImageColor.getrgb(color)


def _encode(image):
    buffer = io.BytesIO()
    # PNG, not JPEG: the ground is a single flat tone and the product edge sits
    # right against it, which is exactly where JPEG puts its worst ringing — on a
    # catalog whose whole point is zooming into a stone.
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def _skipped(content, why):
    """The original render, with an account of why it was not finished."""
    return {
        "image": content,
        "mime": None,
        "cutout": None,
        "note": f"Studio finish skipped: {why}.",
    }
