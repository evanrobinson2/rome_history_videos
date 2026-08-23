"use client";

import clsx from "clsx";
import Image from "next/image";
import type { FeedbackAction, ShotItem } from "@/lib/types";

interface ThumbnailStripProps {
  items: ShotItem[];
  currentIndex: number;
  feedback: Record<string, { action: FeedbackAction }>;
  onSelect: (index: number) => void;
}

function badgeFor(action?: FeedbackAction) {
  if (action === "keep") return "ring-2 ring-keep";
  if (action === "discard") return "ring-2 ring-discard opacity-50";
  if (action === "reroll") return "ring-2 ring-gold-warm";
  return "ring-1 ring-white/10";
}

export function ThumbnailStrip({
  items,
  currentIndex,
  feedback,
  onSelect,
}: ThumbnailStripProps) {
  return (
    <aside className="flex w-full shrink-0 flex-col border-r border-white/10 bg-indigo-deep/80 lg:w-56 xl:w-64">
      <div className="border-b border-white/10 px-4 py-3">
        <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-bone-muted">
          Frames
        </p>
        <p className="mt-1 font-serif text-lg text-bone">
          {items.length} shots
        </p>
      </div>
      <div className="flex-1 overflow-y-auto p-2">
        <div className="grid grid-cols-3 gap-2 sm:grid-cols-4 lg:grid-cols-1">
          {items.map((item, index) => {
            const action = feedback[item.id]?.action;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onSelect(index)}
                className={clsx(
                  "group relative overflow-hidden rounded-lg transition-all",
                  badgeFor(action),
                  currentIndex === index && "ring-2 ring-gold-warm"
                )}
                title={`#${item.shotNumber} ${item.filename}`}
              >
                <div className="relative aspect-video w-full bg-indigo-mid/50">
                  {item.exists ? (
                    <Image
                      src={item.imagePath}
                      alt={item.description}
                      fill
                      className="object-cover"
                      sizes="160px"
                    />
                  ) : (
                    <div className="flex h-full items-center justify-center text-[10px] text-bone-muted">
                      missing
                    </div>
                  )}
                </div>
                <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/80 to-transparent px-1.5 py-1">
                  <span className="text-[10px] font-mono text-bone/90">
                    {String(item.shotNumber).padStart(2, "0")}
                  </span>
                </div>
                {action && (
                  <span
                    className={clsx(
                      "absolute right-1 top-1 rounded px-1 text-[9px] font-bold uppercase",
                      action === "keep" && "bg-keep text-bone",
                      action === "discard" && "bg-discard text-bone",
                      action === "reroll" && "bg-gold-warm text-indigo-deep"
                    )}
                  >
                    {action[0]}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </aside>
  );
}
