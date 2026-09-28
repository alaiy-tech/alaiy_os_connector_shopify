"use client";

import { useEffect, useRef, useState } from "react";

import { Badge } from "@alaiy-os/ui/badge";
import { Button } from "@alaiy-os/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@alaiy-os/ui/card";
import { Input } from "@alaiy-os/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@alaiy-os/ui/select";
import { Spinner } from "@alaiy-os/ui/spinner";
import { Check, Sparkles, Upload, X } from "lucide-react";
import { toast } from "sonner";

import {
  type EnrichedListingImageRow,
  type ListingImagesPoll,
  acceptAdditionalImage,
  discardPreviewImage,
  enrichListingImage,
  enrichmentErrorMessage,
  fetchListingImages,
  previewLifestyleImage,
  previewWornImage,
  publishListingImages,
  removeAdditionalImage,
  revertListingImage,
} from "@/lib/frappe/shopify-enrichment";

const POLL_MS = 3000;

/**
 * Per-photo retouch + AI lifestyle/worn generation for one product.
 *
 * `images` (from the parent's enriched-listing read) seeds the hero/variant
 * photo list; get_listing_images is then polled independently for live
 * status, since a retouch/generate can still be rendering after this loads
 * and the parent record won't reflect that until its own next read.
 */
export function PhotoStudio({
  itemCode,
  images,
  onChanged,
}: {
  itemCode: string;
  images: EnrichedListingImageRow[];
  onChanged: () => void;
}) {
  const [poll, setPoll] = useState<ListingImagesPoll | null>(null);
  const [publishing, setPublishing] = useState(false);

  function reload() {
    fetchListingImages(itemCode)
      .then(setPoll)
      .catch(() => {
        // transient — next poll tick picks it up
      });
  }

  useEffect(() => {
    reload();
    const timer = setInterval(reload, POLL_MS);
    return () => clearInterval(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [itemCode]);

  const hero = images.filter((row) => !["lifestyle", "worn"].includes(row.kind));
  const additional = images.filter((row) => row.kind === "lifestyle" || row.kind === "worn");

  async function publish() {
    setPublishing(true);
    try {
      const result = await publishListingImages(itemCode);
      toast.success(`Published ${result.published} photo(s) to the live listing.`);
    } catch (error) {
      toast.error(enrichmentErrorMessage(error, "Could not publish photos."));
    } finally {
      setPublishing(false);
    }
  }

  const hasFinishedRenders = poll?.images.some((row) => row.url && !row.pending) ?? false;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Photo Studio</CardTitle>
          <CardDescription>Retouch existing photos, or generate lifestyle/worn variants.</CardDescription>
        </div>
        <Button size="sm" variant="outline" disabled={publishing || !hasFinishedRenders} onClick={() => void publish()}>
          {publishing ? <Spinner /> : <Upload />} Publish photos
        </Button>
      </CardHeader>
      <CardContent className="flex flex-col gap-6">
        <div>
          <p className="mb-2 font-medium text-sm">Product photos</p>
          {hero.length === 0 ? (
            <p className="text-muted-foreground text-sm">No photos yet.</p>
          ) : (
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-5">
              {hero.map((row) => (
                <HeroTile key={row.source_url} row={row} poll={poll} itemCode={itemCode} onChanged={() => (reload(), onChanged())} />
              ))}
            </div>
          )}
        </div>

        <div>
          <p className="mb-2 font-medium text-sm">Lifestyle &amp; worn photos</p>
          {additional.length > 0 && (
            <div className="mb-3 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-5">
              {additional.map((row) => (
                <AdditionalTile key={`${row.source_url}-${row.url}`} row={row} itemCode={itemCode} onChanged={() => (reload(), onChanged())} />
              ))}
            </div>
          )}
          <GeneratorPanel itemCode={itemCode} heroPhotos={hero} onChanged={() => (reload(), onChanged())} />
        </div>
      </CardContent>
    </Card>
  );
}

function HeroTile({
  row,
  poll,
  itemCode,
  onChanged,
}: {
  row: EnrichedListingImageRow;
  poll: ListingImagesPoll | null;
  itemCode: string;
  onChanged: () => void;
}) {
  const [busy, setBusy] = useState(false);
  const liveRow = poll?.images.find((r) => r.source_url === row.source_url && r.kind !== "lifestyle" && r.kind !== "worn");
  const pending = liveRow?.pending ?? false;
  const displayUrl = liveRow?.url || row.url || row.source_url;
  const isRetouched = !!row.url && row.url !== row.source_url;

  async function retouch(force?: boolean) {
    if (!row.source_url) return;
    setBusy(true);
    try {
      await enrichListingImage(itemCode, row.source_url, force);
      toast.success("Queued — this can take a moment.");
      onChanged();
    } catch (error) {
      toast.error(enrichmentErrorMessage(error, "Could not queue the retouch."));
    } finally {
      setBusy(false);
    }
  }

  async function revert() {
    if (!row.source_url) return;
    setBusy(true);
    try {
      await revertListingImage(itemCode, row.source_url);
      toast.success("Reverted to the original photo.");
      onChanged();
    } catch (error) {
      toast.error(enrichmentErrorMessage(error, "Could not revert."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-col gap-1 rounded-md border p-2">
      <div className="relative aspect-square w-full overflow-hidden rounded-md bg-muted">
        {displayUrl && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={displayUrl} alt="" className="h-full w-full object-cover" />
        )}
        {pending && (
          <div className="absolute inset-0 flex items-center justify-center bg-background/70">
            <Spinner />
          </div>
        )}
      </div>
      {row.item_variant && (
        <span className="truncate text-muted-foreground text-xs" title={row.item_variant}>
          {row.item_variant}
        </span>
      )}
      {liveRow?.note && !pending && <p className="text-destructive text-xs">{liveRow.note}</p>}
      <div className="flex flex-wrap gap-1">
        <Button size="sm" variant="outline" className="h-7 flex-1 px-2 text-xs" disabled={busy || pending} onClick={() => void retouch(isRetouched)}>
          <Sparkles className="size-3" /> {isRetouched ? "Redo" : "Retouch"}
        </Button>
        {isRetouched && (
          <Button size="sm" variant="ghost" className="h-7 px-2 text-xs" disabled={busy || pending} onClick={() => void revert()}>
            Revert
          </Button>
        )}
      </div>
    </div>
  );
}

function AdditionalTile({
  row,
  itemCode,
  onChanged,
}: {
  row: EnrichedListingImageRow;
  itemCode: string;
  onChanged: () => void;
}) {
  const [busy, setBusy] = useState(false);

  async function remove() {
    if (!row.source_url || !row.url) return;
    setBusy(true);
    try {
      await removeAdditionalImage(itemCode, row.source_url, row.url);
      toast.success("Removed.");
      onChanged();
    } catch (error) {
      toast.error(enrichmentErrorMessage(error, "Could not remove this photo."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-col gap-1 rounded-md border p-2">
      <div className="relative aspect-square w-full overflow-hidden rounded-md bg-muted">
        {row.url && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={row.url} alt="" className="h-full w-full object-cover" />
        )}
        <Badge variant="outline" className="absolute top-1 left-1 border-0 bg-background/80 font-medium capitalize">
          {row.kind}
        </Badge>
      </div>
      {row.brief && <p className="truncate text-muted-foreground text-xs" title={row.brief}>{row.brief}</p>}
      <Button size="sm" variant="ghost" className="h-7 px-2 text-xs" disabled={busy} onClick={() => void remove()}>
        <X className="size-3" /> Remove
      </Button>
    </div>
  );
}

function GeneratorPanel({
  itemCode,
  heroPhotos,
  onChanged,
}: {
  itemCode: string;
  heroPhotos: EnrichedListingImageRow[];
  onChanged: () => void;
}) {
  const [kind, setKind] = useState<"lifestyle" | "worn">("lifestyle");
  const [sourceUrl, setSourceUrl] = useState(heroPhotos[0]?.source_url ?? "");
  const [prompt, setPrompt] = useState("");
  const [generating, setGenerating] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const promptRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!sourceUrl && heroPhotos[0]?.source_url) setSourceUrl(heroPhotos[0].source_url);
  }, [heroPhotos, sourceUrl]);

  async function generate() {
    if (!sourceUrl) {
      toast.warning("Pick a source photo first.");
      return;
    }
    if (kind === "lifestyle" && !prompt.trim()) {
      toast.warning("Describe the scene first.");
      return;
    }
    setGenerating(true);
    try {
      const result =
        kind === "lifestyle" ? await previewLifestyleImage(itemCode, sourceUrl, prompt.trim()) : await previewWornImage(itemCode, sourceUrl, prompt.trim() || undefined);
      setPreview(result.url);
    } catch (error) {
      toast.error(enrichmentErrorMessage(error, "Could not generate a preview."));
    } finally {
      setGenerating(false);
    }
  }

  async function accept() {
    if (!preview || !sourceUrl) return;
    try {
      await acceptAdditionalImage(itemCode, sourceUrl, kind, preview, { query: prompt.trim() || undefined });
      toast.success("Added to the gallery.");
      setPreview(null);
      setPrompt("");
      onChanged();
    } catch (error) {
      toast.error(enrichmentErrorMessage(error, "Could not keep this photo."));
    }
  }

  async function discard() {
    if (!preview) return;
    try {
      await discardPreviewImage(preview);
    } finally {
      setPreview(null);
    }
  }

  return (
    <div className="flex flex-col gap-3 rounded-lg border p-3">
      <div className="flex flex-wrap items-center gap-2">
        <Button size="sm" variant={kind === "lifestyle" ? "secondary" : "outline"} onClick={() => setKind("lifestyle")}>
          Lifestyle
        </Button>
        <Button size="sm" variant={kind === "worn" ? "secondary" : "outline"} onClick={() => setKind("worn")}>
          Worn / staged
        </Button>
      </div>

      <div className="flex flex-wrap items-end gap-2">
        <Select value={sourceUrl || undefined} onValueChange={setSourceUrl}>
          <SelectTrigger size="sm" className="w-56">
            <SelectValue placeholder="Pick a photo" />
          </SelectTrigger>
          <SelectContent>
            {heroPhotos.map((row) =>
              row.source_url ? (
                <SelectItem key={row.source_url} value={row.source_url}>
                  {row.item_variant ? `Variant: ${row.item_variant}` : "Main product photo"}
                </SelectItem>
              ) : null,
            )}
          </SelectContent>
        </Select>
        <Input
          ref={promptRef}
          className="h-8 min-w-48 flex-1"
          placeholder={kind === "lifestyle" ? "Describe the scene, e.g. \"on a marble countertop\"" : "Optional scene notes"}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          disabled={generating}
        />
        <Button size="sm" disabled={generating} onClick={() => void generate()}>
          {generating ? <Spinner /> : <Sparkles />} Generate preview
        </Button>
      </div>

      {preview && (
        <div className="flex items-start gap-3 rounded-md border p-2">
          <div className="aspect-square w-32 overflow-hidden rounded-md bg-muted">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={preview} alt="Preview" className="h-full w-full object-cover" />
          </div>
          <div className="flex flex-col gap-2">
            <p className="text-muted-foreground text-xs">Not saved yet — accept to add it to the gallery, or discard.</p>
            <div className="flex gap-2">
              <Button size="sm" onClick={() => void accept()}>
                <Check className="size-3" /> Keep
              </Button>
              <Button size="sm" variant="outline" onClick={() => void discard()}>
                <X className="size-3" /> Discard
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
