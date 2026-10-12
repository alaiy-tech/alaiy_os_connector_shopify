"use client";

import { useEffect, useState } from "react";

import { Alert, AlertDescription, AlertTitle } from "@alaiy-os/ui/alert";
import { Badge } from "@alaiy-os/ui/badge";
import { Button } from "@alaiy-os/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@alaiy-os/ui/card";
import { Input } from "@alaiy-os/ui/input";
import { Label } from "@alaiy-os/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@alaiy-os/ui/select";
import { Skeleton } from "@alaiy-os/ui/skeleton";
import { Spinner } from "@alaiy-os/ui/spinner";
import { Textarea } from "@alaiy-os/ui/textarea";
import { CircleAlert, Sparkles } from "lucide-react";
import { toast } from "sonner";

import {
  type EnrichedListingAttribute,
  type EnrichedListingDetail,
  enrichmentErrorMessage,
  fetchEnrichedListing,
  saveEnrichedListing,
} from "@/lib/frappe/shopify-enrichment";

import { PhotoStudio } from "./photo-studio";

const CONFIDENCE_OPTIONS = ["high", "medium", "low"];

export function EnrichmentWorkspace({ itemCode }: { itemCode: string }) {
  const [listing, setListing] = useState<EnrichedListingDetail | null | undefined>(undefined);
  const [saving, setSaving] = useState(false);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let cancelled = false;
    fetchEnrichedListing(itemCode).then((result) => {
      if (!cancelled) setListing(result);
    });
    return () => {
      cancelled = true;
    };
  }, [itemCode, reloadToken]);

  function reload() {
    setReloadToken((t) => t + 1);
  }

  async function save(patch: Record<string, unknown>, successMessage: string) {
    setSaving(true);
    try {
      await saveEnrichedListing(itemCode, patch);
      toast.success(successMessage);
      reload();
    } catch (error) {
      toast.error(enrichmentErrorMessage(error, "Could not save."));
    } finally {
      setSaving(false);
    }
  }

  if (listing === undefined) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-40 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (listing === null) {
    return (
      <Card>
        <CardContent className="py-10 text-center text-muted-foreground text-sm">
          This product has no enrichment record yet. It's created automatically the first time it goes through the
          listing agent or a photo is retouched from its listing page.
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <Badge variant="outline" className="border-0 font-medium">
          {listing.status}
        </Badge>
        {listing.confidence && (
          <Badge variant="outline" className="border-0 font-medium capitalize">
            {listing.confidence} confidence
          </Badge>
        )}
      </div>

      {listing.needs_review && (
        <Alert>
          <CircleAlert />
          <AlertTitle>Needs review</AlertTitle>
          <AlertDescription>{listing.needs_review}</AlertDescription>
        </Alert>
      )}

      <ContentCard listing={listing} saving={saving} onSave={save} />
      <PhotoStudio itemCode={itemCode} images={listing.images} onChanged={reload} />

      <div className="flex flex-wrap items-center gap-2">
        <Button disabled={saving || listing.status === "Approved"} onClick={() => void save({ status: "Approved" }, "Approved — pushed to the live listing.")}>
          {saving ? <Spinner /> : <Sparkles />} Approve
        </Button>
        {listing.status !== "Approved" && (
          <p className="text-muted-foreground text-xs">Approving overwrites the live listing's title, description, attributes and photos with what's here.</p>
        )}
      </div>
    </div>
  );
}

function ContentCard({
  listing,
  saving,
  onSave,
}: {
  listing: EnrichedListingDetail;
  saving: boolean;
  onSave: (patch: Record<string, unknown>, message: string) => Promise<void>;
}) {
  const [title, setTitle] = useState(listing.title ?? "");
  const [description, setDescription] = useState(listing.description ?? "");
  const [category, setCategory] = useState(listing.category ?? "");
  const [productType, setProductType] = useState(listing.product_type ?? "");
  const [confidence, setConfidence] = useState(listing.confidence ?? "");
  const [seoTitle, setSeoTitle] = useState(listing.seo_title ?? "");
  const [seoDescription, setSeoDescription] = useState(listing.seo_description ?? "");
  const [tags, setTags] = useState(listing.shopify_tags ?? "");
  const [attributes, setAttributes] = useState<EnrichedListingAttribute[]>(listing.attributes);

  useEffect(() => {
    setTitle(listing.title ?? "");
    setDescription(listing.description ?? "");
    setCategory(listing.category ?? "");
    setProductType(listing.product_type ?? "");
    setConfidence(listing.confidence ?? "");
    setSeoTitle(listing.seo_title ?? "");
    setSeoDescription(listing.seo_description ?? "");
    setTags(listing.shopify_tags ?? "");
    setAttributes(listing.attributes);
  }, [listing]);

  function updateAttribute(index: number, value: string) {
    setAttributes((current) => current.map((a, i) => (i === index ? { ...a, value } : a)));
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Content</CardTitle>
        <CardDescription>Edit before approving — approval writes these fields onto the live listing.</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label>Title</Label>
          <Input value={title} onChange={(e) => setTitle(e.target.value)} disabled={saving} />
        </div>
        <div className="space-y-2">
          <Label>Confidence</Label>
          <Select value={confidence || undefined} onValueChange={setConfidence} disabled={saving}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Not set" />
            </SelectTrigger>
            <SelectContent>
              {CONFIDENCE_OPTIONS.map((c) => (
                <SelectItem key={c} value={c} className="capitalize">
                  {c}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2 md:col-span-2">
          <Label>Description</Label>
          <Textarea value={description} onChange={(e) => setDescription(e.target.value)} disabled={saving} rows={4} />
        </div>
        <div className="space-y-2">
          <Label>Category</Label>
          <Input value={category} onChange={(e) => setCategory(e.target.value)} disabled={saving} />
        </div>
        <div className="space-y-2">
          <Label>Product Type</Label>
          <Input value={productType} onChange={(e) => setProductType(e.target.value)} disabled={saving} />
        </div>
        <div className="space-y-2">
          <Label>SEO Title</Label>
          <Input value={seoTitle} onChange={(e) => setSeoTitle(e.target.value)} disabled={saving} />
        </div>
        <div className="space-y-2">
          <Label>SEO Description</Label>
          <Input value={seoDescription} onChange={(e) => setSeoDescription(e.target.value)} disabled={saving} />
        </div>
        <div className="space-y-2 md:col-span-2">
          <Label>Shopify Tags</Label>
          <Textarea value={tags} onChange={(e) => setTags(e.target.value)} disabled={saving} rows={2} placeholder="One tag per line" />
        </div>

        {attributes.length > 0 && (
          <div className="space-y-2 md:col-span-2">
            <Label>Attributes</Label>
            <div className="flex flex-col gap-2">
              {attributes.map((attr, index) => (
                <div key={attr.name ?? attr.key} className="flex items-start gap-2">
                  <div className="w-40 shrink-0 pt-2 text-muted-foreground text-sm">{attr.key}</div>
                  <Textarea
                    value={attr.value ?? ""}
                    onChange={(e) => updateAttribute(index, e.target.value)}
                    disabled={saving}
                    rows={1}
                    className="flex-1"
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="md:col-span-2">
          <Button
            variant="outline"
            size="sm"
            disabled={saving}
            onClick={() =>
              void onSave(
                {
                  title,
                  description,
                  category,
                  product_type: productType,
                  confidence,
                  seo_title: seoTitle,
                  seo_description: seoDescription,
                  shopify_tags: tags,
                  attributes: attributes.map((a) => ({ key: a.key, value: a.value })),
                },
                "Saved.",
              )
            }
          >
            Save content
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
