export interface DocumentOut {
  id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  chunk_count: number;
  status: string;
  uploaded_at: string;
}

export interface SourceOut {
  source: string;
  content: string;
  score: number;
}

export interface ChatResponse {
  session_id: string;
  answer: string;
  sources: SourceOut[];
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceOut[];
  pending?: boolean;
}
