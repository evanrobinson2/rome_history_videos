/**
 * Generic frame catalog — works with local paths or Vercel Blob URLs.
 * Adding frames = upload + upsert catalog entry (no app redeploy).
 */

export type ReviewStatus = "pass" | "reject" | "flagged" | "unreviewed";
export type FeedbackAction = "keep" | "discard" | "reroll" | null;

export interface Mood {
  number: number;
  name: string;
}

export interface ReviewMeta {
  status: ReviewStatus;
  notes?: string;
  rejectReason?: string;
  v2Fix?: string;
  flagged?: boolean;
}

/** One reviewable still. New images only need id + url + facets. */
export interface ShotItem {
  id: string;
  /** CDN or local path to the image */
  url: string;
  filename?: string;
  shotNumber?: number;
  /** Facet: story section / part (e.g. "D. Marcianople banquet") */
  storyPart?: string;
  /** Facet: beat description */
  storyBeat?: string;
  /** Facet: mood label */
  mood?: Mood | string;
  register?: string;
  category?: string;
  description?: string;
  prompt?: string;
  /** Extra freeform facets for filtering */
  tags?: string[];
  stanza?: string;
  review?: ReviewMeta;
  archivedUrl?: string;
  /** @deprecated use url */
  imagePath?: string;
  section?: string;
  sectionTitle?: string;
  sectionNarrative?: string;
  archivedPath?: string;
  exists?: boolean;
}

export interface Manifest {
  generatedAt: string;
  title: string;
  styleSuffix?: string;
  totalShots: number;
  items: ShotItem[];
  /** Where this catalog lives (blob URL when remote) */
  source?: string;
}

export interface FeedbackEntry {
  action: FeedbackAction;
  note?: string;
  updatedAt: string;
}

export type FeedbackStore = Record<string, FeedbackEntry>;

export type FacetKey = "storyPart" | "mood" | "category" | "stanza" | "tags";

export function moodLabel(mood?: Mood | string): string {
  if (!mood) return "—";
  if (typeof mood === "string") return mood;
  if (mood.number > 0) return `${mood.number} ${mood.name}`;
  return mood.name || "—";
}

export function shotUrl(item: ShotItem): string {
  return item.url || item.imagePath || "";
}

export function shotPart(item: ShotItem): string {
  return (
    item.storyPart ||
    (item.section && item.sectionTitle
      ? `${item.section}. ${item.sectionTitle}`
      : item.sectionTitle) ||
    "Unsorted"
  );
}

export function shotBeat(item: ShotItem): string {
  return item.storyBeat || item.description || item.id;
}
