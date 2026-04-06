export type AppMode = "research" | "canvas";

export type TaskType = "research-basic" | "graph-traversal" | "";

export type ResearchDepth = "standard" | "deep" | "comprehensive";
export type JobStatus = "running" | "complete" | "failed";

export interface ResearchConfig {
  taskType: TaskType;
  model: string;
  depth: ResearchDepth;
  maxSources: number;
  keywords?: string;
  agentVersion?: string;
}

export interface ThoughtEvent {
  type: "thought" | "critique" | "sub_researcher_start" | "node_start";
  content: string;
  node?: string;
  metadata?: Record<string, unknown>;
  timestamp: number;
}

export type StatusLevel = "node" | "tool" | "researcher" | "done" | "error";

export interface StatusLine {
  timestamp: number; // ms since job start
  text: string;
  level: StatusLevel;
}

export interface Source {
  url: string;
  title: string;
}

export interface Job {
  id: string;
  query: string;
  config: ResearchConfig;
  status: JobStatus;
  createdAt: number;
  completedAt?: number;
  report?: string;
  qaReport?: string;
  sources?: Source[];
  paperCount?: number;
  thoughts?: ThoughtEvent[];
  toolCalls?: Record<string, number>;
  statusLog?: StatusLine[];
  error?: string;
  elapsed?: string;
}

// Tool category groupings for display
export const TOOL_CATEGORIES: Record<string, { label: string; tools: string[] }> = {
  academic_db: {
    label: "Academic DBs",
    tools: [
      "eric_search", "openalex_search", "arxiv_search", "elsevier_search",
      "semantic_scholar_search", "search_papers_by_relevance", "get_paper",
      "snippet_search", "search_paper_by_title", "get_citations",
      "search_authors_by_name", "get_author_papers",
    ],
  },
  web_search: {
    label: "Web Search",
    tools: ["anthropic_web_search", "openai_web_search"],
  },
  tavily: {
    label: "Tavily",
    tools: ["tavily_search"],
  },
  scholar: {
    label: "Google Scholar",
    tools: ["scholar_search"],
  },
};

export const TASK_TYPE_OPTIONS = [
  { value: "research-basic", label: "Research — Basic" },
];

export const MODEL_OPTIONS = [
  // OpenAI
  { value: "gpt-5.2",       label: "GPT-5.2" },
  { value: "gpt-5.4",       label: "GPT-5.4" },
  { value: "gpt-5-mini",    label: "GPT-5 Mini" },
  { value: "gpt-4.1",       label: "GPT-4.1" },
  { value: "gpt-4o",        label: "GPT-4o" },
  // Anthropic
  { value: "claude-sonnet-4-6", label: "Claude Sonnet 4.6" },
  { value: "claude-opus-4-6",   label: "Claude Opus 4.6" },
  { value: "claude-sonnet-4-5", label: "Claude Sonnet 4.5" },
  { value: "claude-opus-4-5",   label: "Claude Opus 4.5" },
  { value: "claude-haiku-4-5",  label: "Claude Haiku 4.5" },
];

export const DEPTH_OPTIONS: { value: ResearchDepth; label: string; description: string }[] = [
  { value: "standard", label: "Standard", description: "2 iterations" },
];

// ── Graph Traversal ──────────────────────────────────────────────────────────

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  intent?: string;
}

export interface GraphSession {
  id: string;        // also used as the LangGraph thread_id
  firstQuery: string;
  createdAt: number;
  updatedAt: number;
  messages: ChatMessage[];
  model: string;
}
