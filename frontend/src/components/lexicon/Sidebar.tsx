"use client";

import * as React from "react";

import type { DocumentListItem } from "@/lib/api";
import { Button, Card, FieldHint, Input, Label } from "@/components/ui";

export type SidebarProps = {
  docs: DocumentListItem[];
  selectedDocIds: Set<string>;
  busy: boolean;
  onRefreshDocs: () => void;
  onToggleDoc: (docId: string, checked: boolean) => void;
  onSelectAllDocs: () => void;
  onClearDocs: () => void;

  embedLimit: number;
  embedInfo: string;
  onChangeEmbedLimit: (limit: number) => void;
  onEmbed: () => void;
};

export default function Sidebar(props: SidebarProps) {
  const {
    docs,
    selectedDocIds,
    busy,
    onRefreshDocs,
    onToggleDoc,
    onSelectAllDocs,
    onClearDocs,
    embedLimit,
    embedInfo,
    onChangeEmbedLimit,
    onEmbed,
  } = props;

  return (
    <Card className="lg:col-span-1">
      <div className="space-y-4">
        <div>
          <div className="flex items-center justify-between gap-2">
            <Label>Documents</Label>
            <Button variant="secondary" disabled={busy} onClick={onRefreshDocs}>
              Refresh
            </Button>
          </div>
          <FieldHint className="mt-1">Select one or more documents to scope search/answer.</FieldHint>

          <div className="mt-3 max-h-80 space-y-2 overflow-auto pr-1">
            {docs.length === 0 ? (
              <div className="rounded-xl border border-zinc-200 p-3 text-sm text-zinc-600 dark:border-zinc-800 dark:text-zinc-400">
                No documents yet. Upload one in the Ingest tab.
              </div>
            ) : (
              docs.map((d) => {
                const checked = selectedDocIds.has(d.id);
                return (
                  <label
                    key={d.id}
                    className="flex cursor-pointer items-start gap-3 rounded-xl border border-zinc-200 p-3 hover:bg-zinc-50 dark:border-zinc-800 dark:hover:bg-zinc-900"
                  >
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={(e) => onToggleDoc(d.id, e.target.checked)}
                      className="mt-1 h-4 w-4 rounded border-zinc-300 dark:border-zinc-700"
                    />
                    <div className="min-w-0">
                      <div className="truncate text-sm font-medium">{d.title || "(untitled)"}</div>
                      <div className="mt-0.5 font-mono text-[11px] text-zinc-500 dark:text-zinc-400">
                        {d.id.slice(0, 8)}… · {new Date(d.created_at).toLocaleString()}
                      </div>
                    </div>
                  </label>
                );
              })
            )}
          </div>

          <div className="mt-3 flex flex-wrap gap-2">
            <Button variant="secondary" disabled={busy || docs.length === 0} onClick={onSelectAllDocs}>
              Select all
            </Button>
            <Button variant="secondary" disabled={busy} onClick={onClearDocs}>
              Clear
            </Button>
          </div>
        </div>

        <div>
          <Label>Embed chunks</Label>
          <div className="mt-2 flex gap-2">
            <Input
              type="number"
              min={1}
              max={500}
              value={embedLimit}
              onChange={(e) => onChangeEmbedLimit(Number(e.target.value))}
            />
            <Button disabled={busy} onClick={onEmbed}>
              Embed
            </Button>
          </div>
          {embedInfo ? <FieldHint className="mt-2">{embedInfo}</FieldHint> : null}
        </div>
      </div>
    </Card>
  );
}

