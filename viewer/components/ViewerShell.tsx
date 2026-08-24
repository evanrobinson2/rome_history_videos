"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import type { FeedbackAction, FeedbackStore, Manifest } from "@/lib/types";
import {
  copyPrompt,
  exportFeedback,
  loadFeedback,
  setFeedback,
} from "@/lib/feedback";
import { DetailTabs } from "./DetailTabs";
import { FeedbackToolbar } from "./FeedbackToolbar";
import { ImageStage } from "./ImageStage";
import { ThumbnailStrip, type ThumbSize } from "./ThumbnailStrip";

const THUMB_SIZE_KEY = "rome-viewer-thumb-size-v1";

interface ViewerShellProps {
  manifest: Manifest;
}

function loadThumbSize(): ThumbSize {
  if (typeof window === "undefined") return "M";
  const raw = localStorage.getItem(THUMB_SIZE_KEY);
  if (raw === "S" || raw === "M" || raw === "L" || raw === "XL") return raw;
  return "M";
}

export function ViewerShell({ manifest }: ViewerShellProps) {
  const [index, setIndex] = useState(0);
  const [feedback, setFeedbackState] = useState<FeedbackStore>({});
  const [copied, setCopied] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [thumbSize, setThumbSize] = useState<ThumbSize>("M");

  const items = manifest.items;
  const item = items[index];
  const currentAction = feedback[item?.id]?.action ?? null;

  useEffect(() => {
    setFeedbackState(loadFeedback());
    setThumbSize(loadThumbSize());
    setMounted(true);
  }, []);

  const handleThumbSize = useCallback((size: ThumbSize) => {
    setThumbSize(size);
    localStorage.setItem(THUMB_SIZE_KEY, size);
  }, []);

  const stats = useMemo(() => {
    let keep = 0;
    let discard = 0;
    let reroll = 0;
    for (const entry of Object.values(feedback)) {
      if (entry.action === "keep") keep++;
      if (entry.action === "discard") discard++;
      if (entry.action === "reroll") reroll++;
    }
    return {
      keep,
      discard,
      reroll,
      pending: items.length - keep - discard - reroll,
    };
  }, [feedback, items.length]);

  const goPrev = useCallback(() => {
    setIndex((i) => Math.max(0, i - 1));
  }, []);

  const goNext = useCallback(() => {
    setIndex((i) => Math.min(items.length - 1, i + 1));
  }, [items.length]);

  const handleAction = useCallback(
    (action: FeedbackAction) => {
      if (!item) return;
      const next = setFeedback(feedback, item.id, action);
      setFeedbackState(next);
      if (action === "reroll") {
        copyPrompt(item.prompt);
        setCopied(true);
        window.setTimeout(() => setCopied(false), 2000);
      }
      // Standard review flow: decide → advance
      if (action === "keep" || action === "discard") {
        window.setTimeout(() => {
          setIndex((i) => Math.min(items.length - 1, i + 1));
        }, 120);
      }
    },
    [feedback, item, items.length]
  );

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement
      ) {
        return;
      }
      if (e.key === "ArrowLeft") goPrev();
      if (e.key === "ArrowRight") goNext();
      if (e.key === "k" || e.key === "K")
        handleAction(currentAction === "keep" ? null : "keep");
      if (e.key === "d" || e.key === "D")
        handleAction(currentAction === "discard" ? null : "discard");
      if (e.key === "r" || e.key === "R")
        handleAction(currentAction === "reroll" ? null : "reroll");
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [goPrev, goNext, handleAction, currentAction]);

  if (!mounted || !item) {
    return (
      <div className="flex min-h-dvh items-center justify-center text-bone-muted">
        Loading…
      </div>
    );
  }

  return (
    <div className="min-h-dvh">
      <main className="mx-auto flex max-w-3xl flex-col gap-4 px-4 pb-28 pt-[max(0.75rem,env(safe-area-inset-top))] sm:px-6">
        <header className="flex items-baseline justify-between gap-3">
          <h1 className="font-serif text-lg text-bone sm:text-xl">
            Frame review
          </h1>
          <p className="text-xs text-bone-muted">
            {stats.pending} left
          </p>
        </header>

        <ImageStage
          item={item}
          index={index}
          total={items.length}
          onPrev={goPrev}
          onNext={goNext}
        />

        <ThumbnailStrip
          items={items}
          currentIndex={index}
          feedback={feedback}
          onSelect={setIndex}
          size={thumbSize}
          onSizeChange={handleThumbSize}
        />

        <DetailTabs item={item} styleSuffix={manifest.styleSuffix} />
      </main>

      <FeedbackToolbar
        currentAction={currentAction}
        onAction={handleAction}
        onExport={() => exportFeedback(manifest, feedback)}
        onCopyPrompt={() => {
          copyPrompt(item.prompt);
          setCopied(true);
          window.setTimeout(() => setCopied(false), 2000);
        }}
        copied={copied}
        stats={stats}
      />
    </div>
  );
}
