"use client";

import type * as React from "react";

import { Button, Card, Input, Label } from "@/components/ui";

export type IngestCardProps = {
  busy: boolean;
  title: string;
  file: File | null;
  ingestInfo: string;
  onChangeTitle: (title: string) => void;
  onChangeFile: (file: File | null) => void;
  onIngest: () => void;
  onReset: () => void;
};

export default function IngestCard(props: IngestCardProps) {
  const { busy, title, file, ingestInfo, onChangeTitle, onChangeFile, onIngest, onReset } = props;

  return (
    <Card>
      <h2 className="text-lg font-semibold">Ingest a PDF</h2>
      <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
        Upload a PDF, extract text, chunk it, and persist it.
      </p>

      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <div>
          <Label>Title (optional)</Label>
          <Input value={title} onChange={(e) => onChangeTitle(e.target.value)} placeholder="e.g. Wise help" />
        </div>
        <div>
          <Label>PDF file</Label>
          <Input
            type="file"
            accept="application/pdf"
            onChange={(e) => onChangeFile(e.target.files?.[0] || null)}
          />
        </div>
      </div>

      <div className="mt-4 flex gap-2">
        <Button disabled={busy || !file} onClick={onIngest}>
          Ingest
        </Button>
        <Button variant="secondary" disabled={busy} onClick={onReset}>
          Reset
        </Button>
      </div>

      {ingestInfo ? (
        <div className="mt-4 rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3 text-sm dark:border-zinc-800 dark:bg-zinc-900/30">
          {ingestInfo}
        </div>
      ) : null}
    </Card>
  );
}

