export type IngestResponse = {
  document_id: string;
  chunks_created: number;
};

export type EmbedResponse = {
  embedded: number;
  model?: string;
} & Record<string, unknown>;

export type SearchResult = {
  document_id: string;
  chunk_id: string;
  chunk_index: number;
  distance: number;
  text: string;
};

export type SearchResponse = {
  model: string;
  results: SearchResult[];
};

export type AnswerCitation = {
  document_id: string;
  chunk_id: string;
  chunk_index: number;
  distance: number;
};

export type AnswerResponse = {
  model: string;
  answer: string;
  citations: AnswerCitation[];
  context?: string[];
};

export type DocumentListItem = {
  id: string;
  title: string;
  created_at: string;
};

export type DocumentListResponse = { results: DocumentListItem[] };

type ApiError = {
  error?: { type?: string; code?: string; message?: string };
  detail?: string;
};

function apiBase(): string {
  return (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");
}

async function parseError(resp: Response): Promise<string> {
  let payload: ApiError | null = null;
  try {
    payload = (await resp.json()) as ApiError;
  } catch {
    // ignore
  }

  const msg =
    payload?.error?.message ||
    payload?.detail ||
    `${resp.status} ${resp.statusText}`.trim();
  return msg || "Request failed";
}

export async function ingestPdf(params: { file: File; title?: string }): Promise<IngestResponse> {
  const fd = new FormData();
  fd.append("file", params.file);
  if (params.title) fd.append("title", params.title);

  const resp = await fetch(`${apiBase()}/api/documents/ingest`, {
    method: "POST",
    body: fd,
  });
  if (!resp.ok) throw new Error(await parseError(resp));
  return (await resp.json()) as IngestResponse;
}

export async function embedChunks(params: { document_id?: string; document_ids?: string[]; limit?: number }): Promise<EmbedResponse> {
  const resp = await fetch(`${apiBase()}/api/embeddings/embed`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!resp.ok) throw new Error(await parseError(resp));
  return (await resp.json()) as EmbedResponse;
}

export async function listDocuments(): Promise<DocumentListResponse> {
  const resp = await fetch(`${apiBase()}/api/documents`, { method: "GET" });
  if (!resp.ok) throw new Error(await parseError(resp));
  return (await resp.json()) as DocumentListResponse;
}

export async function search(params: { query: string; top_k?: number; document_id?: string; document_ids?: string[] }): Promise<SearchResponse> {
  const resp = await fetch(`${apiBase()}/api/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!resp.ok) throw new Error(await parseError(resp));
  return (await resp.json()) as SearchResponse;
}

export async function answer(params: { question: string; top_k?: number; document_id?: string; document_ids?: string[]; include_context?: boolean }): Promise<AnswerResponse> {
  const resp = await fetch(`${apiBase()}/api/answer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!resp.ok) throw new Error(await parseError(resp));
  return (await resp.json()) as AnswerResponse;
}

