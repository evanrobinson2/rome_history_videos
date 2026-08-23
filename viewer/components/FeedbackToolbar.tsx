"use client";

import clsx from "clsx";
import { Check, Copy, Download, RotateCcw, Trash2 } from "lucide-react";
import type { FeedbackAction } from "@/lib/types";

interface FeedbackToolbarProps {
  currentAction: FeedbackAction;
  onAction: (action: FeedbackAction) => void;
  onExport: () => void;
  onCopyPrompt: () => void;
  copied: boolean;
  stats: { keep: number; discard: number; reroll: number; pending: number };
}

const actions: {
  key: FeedbackAction;
  label: string;
  icon: typeof Check;
  shortcut: string;
  tone: string;
}[] = [
  {
    key: "keep",
    label: "Keep",
    icon: Check,
    shortcut: "K",
    tone: "bg-keep/20 border-keep/50 text-bone hover:bg-keep/35",
  },
  {
    key: "discard",
    label: "Discard",
    icon: Trash2,
    shortcut: "D",
    tone: "bg-discard/20 border-discard/50 text-bone hover:bg-discard/35",
  },
  {
    key: "reroll",
    label: "Reroll",
    icon: RotateCcw,
    shortcut: "R",
    tone: "bg-reroll/20 border-reroll/50 text-bone hover:bg-reroll/35",
  },
];

export function FeedbackToolbar({
  currentAction,
  onAction,
  onExport,
  onCopyPrompt,
  copied,
  stats,
}: FeedbackToolbarProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-white/10 bg-indigo-mid/40 px-4 py-3 backdrop-blur-sm">
      <div className="flex flex-wrap items-center gap-2">
        {actions.map(({ key, label, icon: Icon, shortcut, tone }) => (
          <button
            key={key}
            type="button"
            onClick={() => onAction(currentAction === key ? null : key)}
            className={clsx(
              "inline-flex items-center gap-2 rounded-xl border px-4 py-2 text-sm font-medium transition-all",
              currentAction === key
                ? "ring-2 ring-gold-warm/60 scale-[1.02]"
                : "opacity-90",
              tone
            )}
            title={`${label} (${shortcut})`}
          >
            <Icon size={16} strokeWidth={2} />
            {label}
            <kbd className="rounded bg-black/20 px-1.5 py-0.5 text-[10px] font-mono opacity-70">
              {shortcut}
            </kbd>
          </button>
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-3 text-xs text-bone-muted">
        <span className="hidden sm:inline">
          {stats.keep} keep · {stats.discard} discard · {stats.reroll} reroll ·{" "}
          {stats.pending} pending
        </span>
        <button
          type="button"
          onClick={onCopyPrompt}
          className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 px-3 py-1.5 text-bone transition hover:bg-white/5"
        >
          {copied ? <Check size={14} /> : <Copy size={14} />}
          {copied ? "Copied" : "Copy prompt"}
        </button>
        <button
          type="button"
          onClick={onExport}
          className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 px-3 py-1.5 text-bone transition hover:bg-white/5"
        >
          <Download size={14} />
          Export
        </button>
      </div>
    </div>
  );
}
