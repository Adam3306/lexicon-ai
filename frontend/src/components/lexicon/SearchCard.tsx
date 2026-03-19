"use client";

import * as React from "react";

import type { SearchResult } from "@/lib/api";
import { Button, Card, FieldHint, Input, Label } from "@/components/ui";

export type SearchCardProps = {
  busy: boolean;
  query: string;
  topK: number;
  searchResults: SearchResult[];
  scopeLabel: string;

  onChangeQuery: (q: string) => void;
  onChangeTopK: (k: number) => void;
  onSearch: () => void;
  onClearResults: () => void;
  onUseResultsAsQuestion: (question: string) => void;
};

export default function SearchCard(props: SearchCardProps) {
  const {
    busy,
    query,
    topK,
    searchResults,
    scopeLabel,
    onChangeQuery,
    onChangeTopK,
    onSearch,
    onClearResults,
    onUseResultsAsQuestion,
  } = props;

  return (
    <Card>
      <h2 className="text-lg font-semibold">Semantic search</h2>
      <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">Searches embedded chunks via pgvector cosine distance.</p>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <div className="sm:col-span-2">
          <Label>Query</Label>
          <Input value={query} onChange={(e) => onChangeQuery(e.target.value)} placeholder="e.g. proof of account details" />
        </div>
        <div>
          <Label>Top K</Label>
          <Input type="number" min={1} max={20} value={topK} onChange={(e) => onChangeTopK(Number(e.target.value))} />
        </div>
      </div>

      <div className="mt-4 flex gap-2">
        <Button disabled={busy || !query.trim()} onClick={onSearch}>
          Search
        </Button>
        <Button variant="secondary" disabled={busy} onClick={onClearResults}>
          Clear
        </Button>
      </div>

      <div className="mt-4 space-y-3">
        {searchResults.length === 0 ? (
          <FieldHint>
            Scope: <span className="font-medium">{scopeLabel}</span>. Ingest + embed first, then search.
          </FieldHint>
        ) : (
          searchResults.map((r) => (
            <div key={r.chunk_id} className="rounded-xl border border-zinc-200 p-3 dark:border-zinc-800">
              <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-zinc-500 dark:text-zinc-400">
                <div className="font-mono">
                  chunk {r.chunk_index} · {r.chunk_id.slice(0, 8)}… · distance {r.distance.toFixed(4)}
                </div>
                <button
                  className="rounded-md border border-zinc-200 bg-white px-2 py-1 hover:bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950 dark:hover:bg-zinc-900"
                  onClick={() => onUseResultsAsQuestion(query || "")}
                >
                  Ask using these
                </button>
              </div>
              <pre className="mt-2 whitespace-pre-wrap text-sm leading-6 text-zinc-800 dark:text-zinc-200">{r.text}</pre>
            </div>
          ))
        )}
      </div>
    </Card>
  );
}

