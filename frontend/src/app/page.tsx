"use client";

import type { DocumentListItem, SearchResult } from "@/lib/api";
import { answer, embedChunks, ingestPdf, listDocuments, search } from "@/lib/api";
import { clsx } from "@/components/ui";
import AnswerCard, { type AnswerCitationUI } from "@/components/lexicon/AnswerCard";
import IngestCard from "@/components/lexicon/IngestCard";
import SearchCard from "@/components/lexicon/SearchCard";
import Sidebar from "@/components/lexicon/Sidebar";
import * as React from "react";

type TabId = "ingest" | "search" | "answer";

export default function Home() {
  const [tab, setTab] = React.useState<TabId>("ingest");

  const [file, setFile] = React.useState<File | null>(null);
  const [title, setTitle] = React.useState("");
  const [ingestInfo, setIngestInfo] = React.useState<string>("");
  const [docs, setDocs] = React.useState<DocumentListItem[]>([]);
  const [selectedDocIds, setSelectedDocIds] = React.useState<Set<string>>(new Set());

  const [embedLimit, setEmbedLimit] = React.useState<number>(200);
  const [embedInfo, setEmbedInfo] = React.useState<string>("");

  const [query, setQuery] = React.useState("");
  const [topK, setTopK] = React.useState<number>(5);
  const [searchResults, setSearchResults] = React.useState<SearchResult[]>([]);

  const [question, setQuestion] = React.useState("");
  const [includeContext, setIncludeContext] = React.useState(true);
  const [answerText, setAnswerText] = React.useState("");
  const [citations, setCitations] = React.useState<AnswerCitationUI[]>([]);

  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState<string>("");

  React.useEffect(() => {
    setBusy(true);
    setError("");
    void listDocuments()
      .then((resp) => setDocs(resp.results || []))
      .catch((e) => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setBusy(false));
  }, []);

  async function run<T>(fn: () => Promise<T>) {
    setError("");
    setBusy(true);
    try {
      return await fn();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      throw e;
    } finally {
      setBusy(false);
    }
  }

  const selectedIds = React.useMemo(() => Array.from(selectedDocIds), [selectedDocIds]);
  const scopeLabel =
    selectedIds.length === 0 ? "All documents" : selectedIds.length === 1 ? "1 document" : `${selectedIds.length} documents`;

  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-900 dark:bg-black dark:text-zinc-100">
      <div className="mx-auto max-w-5xl px-4 py-8">
        <header className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Lexicon AI</h1>
            <p className="text-sm text-zinc-600 dark:text-zinc-400">
              MVP UI for ingestion, embedding, semantic search, and grounded answers.
            </p>
          </div>
          <div className="text-xs text-zinc-500 dark:text-zinc-400">
            API base:{" "}
            <span className="rounded-md border border-zinc-200 bg-white px-2 py-1 font-mono dark:border-zinc-800 dark:bg-zinc-950">
              {process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000"}
            </span>
          </div>
        </header>

        <div className="mt-6 flex flex-wrap gap-2">
          {(
            [
              ["ingest", "Ingest PDF"],
              ["search", "Search"],
              ["answer", "Answer (RAG)"],
            ] as const
          ).map(([id, label]) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className={clsx(
                "rounded-full px-3 py-1.5 text-sm transition-colors",
                tab === id
                  ? "bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900"
                  : "bg-white text-zinc-700 hover:bg-zinc-100 dark:bg-zinc-950 dark:text-zinc-200 dark:hover:bg-zinc-900"
              )}
            >
              {label}
            </button>
          ))}
        </div>

        {error ? (
          <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900 dark:border-red-900/40 dark:bg-red-950/40 dark:text-red-200">
            {error}
          </div>
        ) : null}

        <div className="mt-6 grid gap-4 lg:grid-cols-3">
          <Sidebar
            docs={docs}
            selectedDocIds={selectedDocIds}
            busy={busy}
            onRefreshDocs={() => void run(async () => setDocs((await listDocuments()).results || []))}
            onToggleDoc={(docId, checked) => {
              setSelectedDocIds((prev) => {
                const next = new Set(prev);
                if (checked) next.add(docId);
                else next.delete(docId);
                return next;
              });
            }}
            onSelectAllDocs={() => setSelectedDocIds(new Set(docs.map((d) => d.id)))}
            onClearDocs={() => setSelectedDocIds(new Set())}
            embedLimit={embedLimit}
            embedInfo={embedInfo}
            onChangeEmbedLimit={(limit) => setEmbedLimit(limit)}
            onEmbed={() =>
              void run(async () => {
                const resp = await embedChunks({
                  document_id: selectedIds.length === 1 ? selectedIds[0] : undefined,
                  document_ids: selectedIds.length > 1 ? selectedIds : undefined,
                  limit: embedLimit || undefined,
                });
                setEmbedInfo(`Embedded: ${resp.embedded}${resp.model ? ` (model: ${resp.model})` : ""}`);
                if (tab !== "search") setTab("search");
              })
            }
          />

          <div className="lg:col-span-2 space-y-4">
            {tab === "ingest" ? (
              <IngestCard
                busy={busy}
                title={title}
                file={file}
                ingestInfo={ingestInfo}
                onChangeTitle={setTitle}
                onChangeFile={setFile}
                onIngest={() =>
                  void run(async () => {
                    if (!file) return;
                    const resp = await ingestPdf({ file, title: title || undefined });
                    setIngestInfo(`Document: ${resp.document_id} · chunks: ${resp.chunks_created}`);
                    const list = await listDocuments();
                    setDocs(list.results || []);
                    setSelectedDocIds(new Set([resp.document_id]));
                    setTab("search");
                  })
                }
                onReset={() => {
                  setFile(null);
                  setTitle("");
                  setIngestInfo("");
                }}
              />
            ) : null}

            {tab === "search" ? (
              <SearchCard
                busy={busy}
                query={query}
                topK={topK}
                searchResults={searchResults}
                scopeLabel={scopeLabel}
                onChangeQuery={setQuery}
                onChangeTopK={setTopK}
                onSearch={() =>
                  void run(async () => {
                    const resp = await search({
                      query: query.trim(),
                      top_k: topK || undefined,
                      document_id: selectedIds.length === 1 ? selectedIds[0] : undefined,
                      document_ids: selectedIds.length > 1 ? selectedIds : undefined,
                    });
                    setSearchResults(resp.results || []);
                  })
                }
                onClearResults={() => setSearchResults([])}
                onUseResultsAsQuestion={(q) => {
                  setQuestion(q);
                  setTab("answer");
                }}
              />
            ) : null}

            {tab === "answer" ? (
              <AnswerCard
                busy={busy}
                question={question}
                topK={topK}
                includeContext={includeContext}
                answerText={answerText}
                citations={citations}
                onChangeQuestion={setQuestion}
                onChangeTopK={setTopK}
                onChangeIncludeContext={setIncludeContext}
                onGenerate={() =>
                  void run(async () => {
                    const resp = await answer({
                      question: question.trim(),
                      top_k: topK || undefined,
                      document_id: selectedIds.length === 1 ? selectedIds[0] : undefined,
                      document_ids: selectedIds.length > 1 ? selectedIds : undefined,
                      include_context: includeContext,
                    });
                    setAnswerText(resp.answer || "");
                    setCitations(
                      (resp.citations || []).map((c) => ({
                        chunk_id: c.chunk_id,
                        chunk_index: c.chunk_index,
                        distance: c.distance,
                      }))
                    );
                  })
                }
                onClear={() => {
                  setAnswerText("");
                  setCitations([]);
                }}
              />
            ) : null}
          </div>
        </div>

        <footer className="mt-10 text-xs text-zinc-500 dark:text-zinc-400">
          Tip: after ingesting, click <span className="font-medium">Embed</span> before searching/answering.
        </footer>
      </div>
    </div>
  );
}
