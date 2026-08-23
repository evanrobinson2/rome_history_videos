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
import { ThumbnailStrip } from "./ThumbnailStrip";

interface ViewerShellProps {
  manifest: Manifest;
}

export function ViewerShell({ manifest }: ViewerShellProps) {
  const [index, setIndex] = useState(0);
  const [feedback, setFeedbackState] = useState<FeedbackStore>({});
  const [copied, setCopied] = useState(false);
  const [mounted, setMounted] = useState(false);

  const items = manifest.items;
  const item = items[index];
  const currentAction = feedback[item?.id]?.action ?? null;

  useEffect(() => {
    setFeedbackState(loadFeedback());
    setMounted(true);
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
    },
    [feedback, item]
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
      if (e.key === "k" || e.key === "K") handleAction(currentAction === "keep" ? null : "keep");
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
      <div className="flex min-h-screen items-center justify-center text-bone-muted">
        Loading frames…
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col lg:flex-row">
      <ThumbnailStrip
        items={items}
        currentIndex={index}
        feedback={feedback}
        onSelect={setIndex}
      />

      <main className="flex min-h-0 flex-1 flex-col gap-4 p-4 sm:p-6">
        <header className="flex items-center justify-between gap-4 border-b border-white/10 pb-4">
          <div>
            <p className="text-[11px] uppercase tracking-[0.25em] text-gold-warm">
              Frame review
            </p>
            <h2 className="font-serif text-2xl text-bone">{manifest.title}</h2>
          </div>
          <p className="hidden text-xs text-bone-muted sm:block">
            ← → navigate · K keep · D discard · R reroll
          </p>
        </header>

        <ImageStage
          item={item}
          index={index}
          total={items.length}
          onPrev={goPrev}
          onNext={goNext}
        />

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

        <DetailTabs item={item} styleSuffix={manifest.styleSuffix} />
      </main>
    </div>
  );
}
