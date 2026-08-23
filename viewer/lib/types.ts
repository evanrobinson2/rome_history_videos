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

export interface ShotItem {
  shotNumber: number;
  id: string;
  filename: string;
  section: string;
  sectionTitle: string;
  sectionNarrative: string;
  mood: Mood;
  register: string;
  description: string;
  category: "character" | "scene";
  imagePath: string;
  prompt: string;
  storyBeat: string;
  storyPart: string;
  review: ReviewMeta;
  archivedPath?: string;
  exists: boolean;
}

export interface Manifest {
  generatedAt: string;
  title: string;
  styleSuffix: string;
  totalShots: number;
  items: ShotItem[];
}

export interface FeedbackEntry {
  action: FeedbackAction;
  note?: string;
  updatedAt: string;
}

export type FeedbackStore = Record<string, FeedbackEntry>;
