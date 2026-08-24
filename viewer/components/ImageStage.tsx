"use client";

import Image from "next/image";
import { ChevronLeft, ChevronRight } from "lucide-react";
import type { ShotItem } from "@/lib/types";

interface ImageStageProps {
  item: ShotItem;
  index: number;
  total: number;
  onPrev: () => void;
  onNext: () => void;
}

export function ImageStage({
  item,
  index,
  total,
  onPrev,
  onNext,
}: ImageStageProps) {
  return (
    <div className="relative flex min-h-0 flex-1 flex-col">
      <div className="mb-3 flex items-start justify-between gap-4">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-bone-muted">
            Shot {String(item.shotNumber).padStart(2, "0")} /{" "}
            {String(total).padStart(2, "0")}
          </p>
          <h1 className="mt-1 font-serif text-xl text-bone sm:text-2xl">
            {item.mood.name}
          </h1>
          <p className="mt-1 text-sm text-bone-muted">{item.storyPart}</p>
        </div>
        <div className="flex shrink-0 gap-2">
          <NavButton onClick={onPrev} label="Previous" disabled={index === 0}>
            <ChevronLeft size={20} />
          </NavButton>
          <NavButton
            onClick={onNext}
            label="Next"
            disabled={index === total - 1}
          >
            <ChevronRight size={20} />
          </NavButton>
        </div>
      </div>

      <div className="relative aspect-video w-full max-h-[min(62vh,820px)] overflow-hidden rounded-2xl border border-white/10 bg-black/30 shadow-2xl">
        {item.exists ? (
          <Image
            src={item.imagePath}
            alt={item.description}
            fill
            className="object-contain"
            sizes="(max-width: 1280px) 100vw, 80vw"
            priority
          />
        ) : (
          <div className="flex h-full min-h-[240px] items-center justify-center text-bone-muted">
            Image not found: {item.filename}
          </div>
        )}
      </div>
    </div>
  );
}

function NavButton({
  onClick,
  label,
  disabled,
  children,
}: {
  onClick: () => void;
  label: string;
  disabled: boolean;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-label={label}
      className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-indigo-mid/50 text-bone transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-30"
    >
      {children}
    </button>
  );
}
