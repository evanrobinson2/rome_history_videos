"use client";

import clsx from "clsx";
import { useEffect, useState } from "react";
import type { ShotItem } from "@/lib/types";
import { moodLabel } from "@/lib/types";

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
    <div className="grid gap-0.5 border-b border-white/5 py-2.5 sm:grid-cols-[7rem_1fr] sm:gap-3">
      <dt className="text-[11px] font-medium uppercase tracking-wide text-bone-muted">
        {label}
      </dt>
      <dd className="text-sm leading-snug text-bone">{children}</dd>
    </div>
  );
}

export function DetailTabs({ item, styleSuffix }: DetailTabsProps) {
  const [active, setActive] = useState<TabId>("details");

  useEffect(() => {
    setActive("details");
  }, [item.id]);

  return (
    <div className="rounded-xl border border-white/10 bg-indigo-mid/25">
      <div className="flex gap-1 overflow-x-auto border-b border-white/10 p-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActive(tab.id)}
            className={clsx(
              "h-9 shrink-0 rounded-lg px-3 text-sm font-medium",
              active === tab.id
                ? "bg-white/10 text-bone"
                : "text-bone-muted active:bg-white/5"
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="max-h-64 overflow-y-auto p-4">
        {active === "details" && (
          <dl>
            <DetailRow label="Shot">{item.shotNumber}</DetailRow>
            <DetailRow label="File">
              <code className="break-all text-xs">{item.filename}</code>
            </DetailRow>
            <DetailRow label="Part">{item.storyPart}</DetailRow>
            <DetailRow label="Mood">{moodLabel(item.mood)}</DetailRow>
            <DetailRow label="Register">{item.register}</DetailRow>
            {item.archivedPath && (
              <DetailRow label="v1">
                <a
                  href={item.archivedPath}
                  target="_blank"
                  rel="noreferrer"
                  className="text-gold-warm underline-offset-2 hover:underline"
                >
                  Open archive
                </a>
              </DetailRow>
            )}
          </dl>
        )}

        {active === "story" && (
          <p className="font-serif text-base leading-relaxed text-bone">
            {item.storyBeat}
          </p>
        )}

        {active === "prompt" && (
          <p className="whitespace-pre-wrap break-words font-mono text-[11px] leading-relaxed text-bone/90">
            {item.prompt}
          </p>
        )}

        {active === "review" && (
          <dl>
            <DetailRow label="Status">
              <span className="capitalize">
                {item.review?.status ?? "unreviewed"}
              </span>
              {item.review?.flagged ? " · flagged" : ""}
            </DetailRow>
            {item.review?.notes && (
              <DetailRow label="Notes">{item.review.notes}</DetailRow>
            )}
            {item.review?.rejectReason && (
              <DetailRow label="Reason">{item.review.rejectReason}</DetailRow>
            )}
            {item.review?.v2Fix && (
              <DetailRow label="Fix">{item.review.v2Fix}</DetailRow>
            )}
            {!item.review?.notes &&
              !item.review?.rejectReason &&
              !item.review?.v2Fix && (
                <p className="text-sm text-bone-muted">No review notes.</p>
              )}
          </dl>
        )}

        {active === "prompt" && (
          <details className="mt-3">
            <summary className="cursor-pointer text-xs text-bone-muted">
              Style suffix
            </summary>
            <p className="mt-2 whitespace-pre-wrap font-mono text-[10px] text-bone-muted">
              {styleSuffix}
            </p>
          </details>
        )}
      </div>
    </div>
  );
}
