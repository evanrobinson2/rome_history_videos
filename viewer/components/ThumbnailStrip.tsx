"use client";

import clsx from "clsx";
import Image from "next/image";
import { useEffect, useRef } from "react";
import type { FeedbackAction, ShotItem } from "@/lib/types";

export type ThumbSize = "S" | "M" | "L" | "XL";

export const THUMB_SIZES: {
  id: ThumbSize;
  label: string;
  width: string;
  sizesAttr: string;
}[] = [
  { id: "S", label: "S", width: "4.5rem", sizesAttr: "72px" },
  { id: "M", label: "M", width: "7rem", sizesAttr: "112px" },
  { id: "L", label: "L", width: "10rem", sizesAttr: "160px" },
  { id: "XL", label: "XL", width: "14rem", sizesAttr: "224px" },
];

interface ThumbnailStripProps {
  items: ShotItem[];
  currentIndex: number;
  feedback: Record<string, { action: FeedbackAction }>;
  onSelect: (index: number) => void;
  size: ThumbSize;
  onSizeChange: (size: ThumbSize) => void;
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
  size,
  onSizeChange,
}: ThumbnailStripProps) {
  const scrollerRef = useRef<HTMLDivElement>(null);
  const activeRef = useRef<HTMLButtonElement>(null);
  const sizeMeta = THUMB_SIZES.find((s) => s.id === size) ?? THUMB_SIZES[1];

  useEffect(() => {
    activeRef.current?.scrollIntoView({
      behavior: "smooth",
      inline: "center",
      block: "nearest",
    });
  }, [currentIndex, size]);

  return (
    <section className="rounded-2xl border border-white/10 bg-indigo-mid/25 backdrop-blur-sm">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 px-4 py-3">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-bone-muted">
            Frames
          </p>
          <p className="mt-0.5 font-serif text-base text-bone">
            {items.length} shots
          </p>
        </div>

        <div
          className="inline-flex items-center gap-1 rounded-xl border border-white/10 bg-indigo-deep/50 p-1"
          role="group"
          aria-label="Thumbnail size"
        >
          <span className="hidden px-2 text-[10px] uppercase tracking-wider text-bone-muted sm:inline">
            Size
          </span>
          {THUMB_SIZES.map((option) => (
            <button
              key={option.id}
              type="button"
              onClick={() => onSizeChange(option.id)}
              className={clsx(
                "min-w-9 rounded-lg px-2.5 py-1.5 text-xs font-semibold transition",
                size === option.id
                  ? "bg-gold-warm text-indigo-deep"
                  : "text-bone-muted hover:bg-white/5 hover:text-bone"
              )}
              aria-pressed={size === option.id}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      <div
        ref={scrollerRef}
        className="overflow-x-auto overflow-y-hidden px-3 py-3"
      >
        <div className="flex w-max gap-2.5">
          {items.map((item, index) => {
            const action = feedback[item.id]?.action;
            const isActive = currentIndex === index;
            return (
              <button
                key={item.id}
                ref={isActive ? activeRef : undefined}
                type="button"
                onClick={() => onSelect(index)}
                style={{ width: sizeMeta.width }}
                className={clsx(
                  "group relative shrink-0 overflow-hidden rounded-lg transition-all",
                  badgeFor(action),
                  isActive && "ring-2 ring-gold-warm scale-[1.03]"
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
                      sizes={sizeMeta.sizesAttr}
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
    </section>
  );
}
