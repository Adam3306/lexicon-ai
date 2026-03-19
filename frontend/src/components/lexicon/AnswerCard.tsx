"use client";

import * as React from "react";

import { Button, Card, Input, Label, Textarea } from "@/components/ui";

export type AnswerCitationUI = {
  chunk_id: string;
  chunk_index: number;
  distance: number;
};

export type AnswerCardProps = {
  busy: boolean;
  question: string;
  topK: number;
  includeContext: boolean;
  answerText: string;
  citations: AnswerCitationUI[];

  onChangeQuestion: (q: string) => void;
  onChangeTopK: (k: number) => void;
  onChangeIncludeContext: (v: boolean) => void;

  onGenerate: () => void;
  onClear: () => void;
};

export default function AnswerCard(props: AnswerCardProps) {
  const {
    busy,
    question,
    topK,
    includeContext,
    answerText,
    citations,
    onChangeQuestion,
    onChangeTopK,
    onChangeIncludeContext,
    onGenerate,
    onClear,
  } = props;

  return (
    <Card>
      <h2 className="text-lg font-semibold">Answer (RAG)</h2>
      <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">Retrieves top chunks and generates a grounded answer with citations.</p>

      <div className="mt-4 space-y-3">
        <div>
          <Label>Question</Label>
          <Textarea rows={3} value={question} onChange={(e) => onChangeQuestion(e.target.value)} placeholder="Ask a question about your documents…" />
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <input
              id="includeContext"
              type="checkbox"
              checked={includeContext}
              onChange={(e) => onChangeIncludeContext(e.target.checked)}
              className="h-4 w-4 rounded border-zinc-300 dark:border-zinc-700"
            />
            <Label htmlFor="includeContext">Include context in response</Label>
          </div>

          <div className="ml-auto flex items-center gap-2">
            <span className="text-sm text-zinc-600 dark:text-zinc-400">Top K</span>
            <Input className="w-24" type="number" min={1} max={20} value={topK} onChange={(e) => onChangeTopK(Number(e.target.value))} />
          </div>
        </div>

        <div className="flex gap-2">
          <Button disabled={busy || !question.trim()} onClick={onGenerate}>
            Generate
          </Button>
          <Button variant="secondary" disabled={busy} onClick={onClear}>
            Clear
          </Button>
        </div>
      </div>

      {answerText ? (
        <div className="mt-5 space-y-3">
          <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-4 text-sm leading-7 dark:border-zinc-800 dark:bg-zinc-900/30">
            {answerText}
          </div>
          {citations.length ? (
            <div className="rounded-xl border border-zinc-200 p-4 dark:border-zinc-800">
              <div className="text-sm font-medium">Citations</div>
              <div className="mt-2 space-y-1 text-xs text-zinc-600 dark:text-zinc-400">
                {citations.map((c) => (
                  <div key={c.chunk_id} className="font-mono">
                    chunk {c.chunk_index} · {c.chunk_id.slice(0, 8)}… · distance {c.distance.toFixed(4)}
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      ) : null}
    </Card>
  );
}

