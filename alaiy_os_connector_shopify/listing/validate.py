# Copyright (c) 2026, Alaiy and contributors
# For license information, please see license.txt
"""Shopify's listing rules, again -- in Python this time, and enforced.

`prompts/listing.md` states these rules as prose, and the prose is what gets a
listing right the first time. This is what makes sure. The duplication is
deliberate and not something to remove: a model that has read "SEO title under
about 60 characters" still writes 74 sometimes, and before this the only thing
between 74 and a saved listing was a JSON schema.

## Why a validator and not a stricter schema

JSON Schema can express `maxLength` and it cannot express most of what actually
matters here:

- "plain text only, no HTML or markdown" -- a pattern that catches real tags
  without rejecting an ampersand or a `<` inside a measurement.
- "always state the unit inside the value" -- a weight of `"1.5"` is a defect and
  `"1.5 kg"` is not, and no schema keyword knows the difference.
- "no promotional filler" -- a list of banned phrases, matched case-insensitively
  across a field that is otherwise free prose.
- "do not set prices" -- a price appearing in `variants[].suggestions`, which is
  a string array that legitimately holds almost anything else.

Every one of those is ordinary Python, and every one of them is a rule a real
listing has been rejected or embarrassed by.

## What it does not do

It does not check truth. "Never invent specifications" is the most important rule
in the prompt and is not enforceable here at all -- nothing in the payload says
whether a material was read off a photo or guessed. That stays a prompt rule
backed by `needs_review`, and the human review step is what catches it.

It also deliberately does not re-check what the JSON schema already enforces --
required keys, types, the `confidence` enum. The schema runs first and this
assumes it passed; duplicating it here would mean two places to update.
"""

import re

#: Shopify truncates a search-result title around here. Not a hard API limit --
#: Shopify accepts a longer one -- which is exactly why the schema cannot express
#: it and this can: the cost of breaking it is a snippet cut mid-word, not an error.
SEO_TITLE_MAX = 60

#: Shopify's own `seo.description` limit. Past this it is silently truncated.
SEO_DESCRIPTION_MAX = 320

TITLE_MIN, TITLE_MAX = 10, 255

#: Attributes whose value is meaningless without a unit. "1.5" is not a weight.
MEASUREMENT_ATTRIBUTES = ("weight", "dimensions", "size")

#: Promotional filler the prompt bans outright. Matched case-insensitively as
#: whole phrases, so "new arrival" is caught and "renewable" is not.
BANNED_PHRASES = (
    "hot sale",
    "free shipping",
    "best seller",
    "bestseller",
    "limited time",
    "act now",
    "buy now",
    "on sale now",
    "lowest price",
    "cheapest",
    "100% satisfaction",
    "money back guarantee",
    "new arrival",
    "must have",
    "don't miss",
    "dont miss",
    "hurry",
)

#: A real tag or entity, not a stray `<` in "< 5 kg" or an ampersand.
_HTML = re.compile(r"</?[a-zA-Z][a-zA-Z0-9]*\s*[^<>]*>|&[a-zA-Z]{2,10};|&#\d+;")

#: Markdown that carries formatting intent. Deliberately narrow: a hyphenated
#: word and an asterisked footnote in prose are not markdown, so this looks for
#: list and emphasis constructions at a line start or wrapping a word.
_MARKDOWN = re.compile(r"(?m)^\s{0,3}(?:[*+]\s|\d+\.\s|#{1,6}\s|>\s)|\*\*\S|__\S|\[[^\]]+\]\([^)]+\)")

#: A number with no letter anywhere after it -- "1.5", "12 x 8", "500".
_NO_UNIT = re.compile(r"^[\d\s.,x×*/-]+$")

#: A currency symbol, a currency code, or the word price.
_PRICE = re.compile(r"[$£€¥₹]\s*\d|\b\d+(?:[.,]\d+)?\s*(?:usd|eur|gbp|inr|aud|cad)\b|\bprice\b", re.I)

#: Enough consecutive capital LETTERS to be shouting rather than an acronym or a
#: code. Letters only, deliberately: a reference/model number like "AR170920265"
#: or "116610LN" is exactly the letter+digit shape the house style asks titles to
#: end with, and matching digits here made every such title a false "shouting"
#: defect -- the dominant cause of a wasted save_listing retry turn in practice.
_SHOUTING = re.compile(r"\b[A-Z]{6,}\b")


def _text(value):
    return (value or "").strip() if isinstance(value, str) else ""


def _truncate_at_word(text, limit):
    """`text`, cut to at most `limit` chars without splitting a word mid-way."""
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(",.;:-")
    return cut or text[:limit]


def normalize(listing):
    """`listing`, with the one defect that is mechanical rather than a real
    rewrite already fixed, so `save_listing` does not spend a whole model turn
    round-tripping something Python can settle on its own.

    Only `seo_title` duplicating `title` verbatim qualifies: it happens because
    the model has nothing shorter to put there yet, and the fix -- Shopify's own
    behaviour of cutting a long seo_title at `SEO_TITLE_MAX` -- is exactly what a
    human would do by hand, not a rewrite the model needs to be asked for. Every
    other defect (a shouting title, promotional filler, an invented price) is
    left alone: those are the model's mistake to correct, and silently patching
    them here would hide what its next attempt actually needs to fix.
    """
    listing = dict(listing or {})
    title = _text(listing.get("title"))
    seo_title = _text(listing.get("seo_title"))
    if seo_title and title and seo_title.lower() == title.lower():
        shortened = _truncate_at_word(title, SEO_TITLE_MAX)
        # Only when truncation actually makes it shorter -- a title that
        # already fits under SEO_TITLE_MAX truncates to itself, and that is
        # still identical to `title`. There is no mechanical fix for that case;
        # it genuinely needs different, shorter copy, so it is left for the
        # model's retry rather than "normalized" into the same defect.
        if shortened.lower() != title.lower():
            listing["seo_title"] = shortened
    return listing


def _banned_in(text, where, defects):
    lowered = text.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            defects.append(
                f"{where} contains the banned promotional phrase '{phrase}'. "
                "Remove it and state what the product actually is."
            )


def validate(listing):
    """Every rule this listing breaks, as sentences a model can act on.

    Returns a list of defect strings; empty means it passes. Phrased as
    instructions rather than error codes, because the reader is the model that
    just wrote the listing and its next move is to fix it.
    """
    listing = listing or {}
    defects = []

    # --- title ---------------------------------------------------------------
    title = _text(listing.get("title"))
    if len(title) < TITLE_MIN:
        defects.append(
            f"title is {len(title)} characters, under the minimum of {TITLE_MIN}. "
            "Write a real product title that leads with the most-searched term."
        )
    elif len(title) > TITLE_MAX:
        defects.append(f"title is {len(title)} characters, over Shopify's limit of {TITLE_MAX}.")
    if title:
        _banned_in(title, "title", defects)
        if _SHOUTING.search(title):
            defects.append(
                "title contains a run of capitals that reads as shouting. Use normal "
                "capitalisation; a genuine acronym is fine, a capitalised word is not."
            )

    # --- description ---------------------------------------------------------
    description = _text(listing.get("description"))
    if not description:
        defects.append("description is empty.")
    else:
        if _HTML.search(description):
            defects.append(
                "description contains HTML. Plain text only -- write it as a single "
                "continuous block of prose."
            )
        if _MARKDOWN.search(description):
            defects.append(
                "description contains markdown (a list, a heading or bold). Plain text "
                "only, as a single continuous block of prose."
            )
        if "\n" in description:
            defects.append(
                "description contains a line break. Write it as one unbroken block of "
                "prose -- no paragraph breaks, no line breaks."
            )
        _banned_in(description, "description", defects)

    # --- SEO -----------------------------------------------------------------
    seo_title = _text(listing.get("seo_title"))
    if not seo_title:
        defects.append("seo_title is empty.")
    elif len(seo_title) > SEO_TITLE_MAX:
        defects.append(
            f"seo_title is {len(seo_title)} characters, over the {SEO_TITLE_MAX} a search "
            "result shows. It will be cut mid-phrase -- shorten it, keyword first."
        )

    seo_description = _text(listing.get("seo_description"))
    if not seo_description:
        defects.append("seo_description is empty.")
    elif len(seo_description) > SEO_DESCRIPTION_MAX:
        defects.append(
            f"seo_description is {len(seo_description)} characters, over Shopify's "
            f"{SEO_DESCRIPTION_MAX} limit. Anything past it is silently dropped."
        )

    if seo_title and title and seo_title.lower() == title.lower():
        defects.append(
            "seo_title is identical to title. They are for different readers -- the "
            "SEO pair is the shorter, keyword-first copy a search result shows."
        )
    if seo_description and description and seo_description.strip() == description.strip():
        defects.append(
            "seo_description repeats the description verbatim. Write the snippet copy "
            "separately, one or two sentences."
        )

    # --- category and product type -------------------------------------------
    for field in ("category", "product_type"):
        if not _text(listing.get(field)):
            defects.append(
                f"{field} is empty. Take a value already in use on this store from "
                "get_reference_values rather than inventing one."
            )

    # --- tags ----------------------------------------------------------------
    tags = listing.get("shopify_tags") or []
    if isinstance(tags, list):
        cleaned = [_text(t) for t in tags]
        if any(not t for t in cleaned):
            defects.append("shopify_tags contains an empty tag.")
        lowered = [t.lower() for t in cleaned if t]
        duplicates = {t for t in lowered if lowered.count(t) > 1}
        if duplicates:
            defects.append(
                f"shopify_tags repeats {sorted(duplicates)}. Tags are catalog "
                "vocabulary; one spelling each."
            )

    # --- attributes ----------------------------------------------------------
    attributes = listing.get("attributes") or {}
    if isinstance(attributes, dict):
        for key in MEASUREMENT_ATTRIBUTES:
            value = _text(attributes.get(key))
            if value and _NO_UNIT.match(value):
                defects.append(
                    f"attributes.{key} is '{value}', a number with no unit. State the "
                    "unit inside the value, e.g. '1.5 kg' or '30 x 20 cm'."
                )

    # --- variants ------------------------------------------------------------
    for entry in listing.get("variants") or []:
        if not isinstance(entry, dict):
            continue
        variant = entry.get("item_variant") or "(unnamed)"
        for suggestion in entry.get("suggestions") or []:
            if isinstance(suggestion, str) and _PRICE.search(suggestion):
                defects.append(
                    f"variants[{variant}].suggestions mentions a price. Pricing is "
                    "handled elsewhere and never belongs in a suggestion."
                )

    # --- images --------------------------------------------------------------
    for index, image in enumerate(listing.get("images") or []):
        if isinstance(image, dict) and not _text(image.get("source_url")):
            defects.append(
                f"images[{index}] has no source_url. Copy the image tool's returned "
                "list verbatim rather than composing entries."
            )

    return defects
