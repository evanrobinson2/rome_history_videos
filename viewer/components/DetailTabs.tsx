"use client";

import clsx from "clsx";
import { useState } from "react";
import type { ShotItem } from "@/lib/types";

type TabId = "details" | "story" | "prompt" | "review";

interface DetailTabsProps {
  item: ShotItem;
  styleSuffix: string;
}

const tabs: { id: TabId; label: string }[] = [
  { id: "details", label: "Details" },
  { id: "story", label: "Story" },
  { id: "prompt", label: "Prompt" },
  { id: "review", label: "Review" },
];

function DetailRow({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="grid gap-1 border-b border-white/5 py-3 sm:grid-cols-[140px_1fr]">
      <dt className="text-xs font-medium uppercase tracking-wider text-bone-muted">
        {label}
      </dt>
      <dd className="text-sm leading-relaxed text-bone">{children}</dd>
    </div>
  );
}

function StatusBadge({
  status,
  flagged,
}: {
  status: string;
  flagged?: boolean;
}) {
  return (
    <span className="inline-flex items-center gap-2">
      <span
        className={clsx(
          "rounded-full px-2.5 py-0.5 text-xs font-medium capitalize",
          status === "pass" && "bg-keep/30 text-bone",
          status === "reject" && "bg-discard/30 text-bone",
          status === "unreviewed" && "bg-white/10 text-bone-muted"
        )}
      >
        {status}
      </span>
      {flagged && (
        <span className="rounded-full bg-gold-warm/30 px-2.5 py-0.5 text-xs text-bone">
          flagged for eye
        </span>
      )}
    </span>
  );
}

export function DetailTabs({ item, styleSuffix }: DetailTabsProps) {
  const [active, setActive] = useState<TabId>("details");

  return (
    <div className="rounded-2xl border border-white/10 bg-indigo-mid/30 backdrop-blur-sm">
      <div className="flex overflow-x-auto border-b border-white/10">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActive(tab.id)}
            className={clsx(
              "whitespace-nowrap border-b-2 px-5 py-3 text-sm font-medium transition",
              active === tab.id
                ? "border-gold-warm text-bone"
                : "border-transparent text-bone-muted hover:text-bone"
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="min-h-[220px] p-5">
        {active === "details" && (
          <dl>
            <DetailRow label="Shot #">{item.shotNumber}</DetailRow>
            <DetailRow label="File">
              <code className="rounded bg-black/20 px-2 py-0.5 text-xs">
                {item.filename}
              </code>
            </DetailRow>
            <DetailRow label="Story part">{item.storyPart}</DetailRow>
            <DetailRow label="Mood">
              {item.mood.number > 0
                ? `${item.mood.number} — ${item.mood.name}`
                : item.mood.name}
            </DetailRow>
            <DetailRow label="Register">{item.register}</DetailRow>
            <DetailRow label="Category">{item.category}</DetailRow>
            {item.sectionNarrative && (
              <DetailRow label="Section note">{item.sectionNarrative}</DetailRow>
            )}
            {item.archivedPath && (
              <DetailRow label="v1 archive">
                <a
                  href={item.archivedPath}
                  target="_blank"
                  rel="noreferrer"
                  className="text-gold-warm underline-offset-2 hover:underline"
                >
                  View rejected v1
                </a>
              </DetailRow>
            )}
          </dl>
        )}

        {active === "story" && (
          <>
            <p className="font-serif text-lg leading-relaxed text-bone">
              {item.storyBeat}
            </p>
            {item.sectionNarrative && (
              <p className="mt-4 text-sm leading-relaxed text-bone-muted">
                {item.sectionNarrative}
              </p>
            )}
          </>
        )}

        {active === "prompt" && (
          <>
            <p className="whitespace-pre-wrap font-mono text-xs leading-relaxed text-bone/90">
              {item.prompt}
            </p>
            <details className="mt-4">
              <summary className="cursor-pointer text-xs text-bone-muted hover:text-bone">
                Standing style suffix
              </summary>
              <p className="mt-2 whitespace-pre-wrap font-mono text-[11px] leading-relaxed text-bone-muted">
                {styleSuffix}
              </p>
            </details>
          </>
        )}

        {active === "review" && (
          <dl>
            <DetailRow label="Agent review">
              <StatusBadge
                status={item.review.status}
                flagged={item.review.flagged}
              />
            </DetailRow>
            {item.review.notes && (
              <DetailRow label="Notes">{item.review.notes}</DetailRow>
            )}
            {item.review.rejectReason && (
              <DetailRow label="Reject reason">
                {item.review.rejectReason}
              </DetailRow>
            )}
            {item.review.v2Fix && (
              <DetailRow label="v2 fix">{item.review.v2Fix}</DetailRow>
            )}
          </dl>
        )}
      </div>
    </div>
  );
}
