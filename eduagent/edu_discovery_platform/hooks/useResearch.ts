"use client";
import { useCallback, useRef, useState } from "react";
import { Job, ResearchConfig, ThoughtEvent, StatusLine, StatusLevel } from "@/lib/types";

// Node name → human label
const NODE_LABELS: Record<string, string> = {
  education_discovery:      "Analyzing research question",
  research_supervisor:      "Supervisor planning",
  supervisor_critique:      "Critiquing synthesis",
  researcher:               "Researcher starting",
  researcher_reflect:       "Reflecting on coverage",
  compress_research:        "Compressing findings",
  final_report_generation:  "Generating final report",
};

// Tool name → human label
const TOOL_LABELS: Record<string, string> = {
  eric_search:                 "ERIC",
  openalex_search:             "OpenAlex",
  arxiv_search:                "arXiv",
  elsevier_search:             "Elsevier / Scopus",
  semantic_scholar_search:     "Semantic Scholar",
  search_papers_by_relevance:  "Semantic Scholar (relevance)",
  snippet_search:              "Semantic Scholar (snippets)",
  get_paper:                   "Semantic Scholar (paper lookup)",
  search_paper_by_title:       "Semantic Scholar (title search)",
  get_citations:               "Semantic Scholar (citations)",
  search_authors_by_name:      "Semantic Scholar (authors)",
  get_author_papers:           "Semantic Scholar (author papers)",
  scholar_search:              "Google Scholar",
  tavily_search:               "Tavily",
  anthropic_web_search:        "Web search (Anthropic)",
  openai_web_search:           "Web search (OpenAI)",
  think_tool:                  "Thinking",
};

export function useResearch(onUpdate: (id: string, patch: Partial<Job>) => void) {
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const startResearch = useCallback(async (jobId: string, query: string, config: ResearchConfig) => {
    setActiveJobId(jobId);
    abortRef.current = new AbortController();

    const jobStart = Date.now();
    const elapsed = () => Date.now() - jobStart;

    const statusLog: StatusLine[] = [];
    const toolCalls: Record<string, number> = {};
    const thoughts: ThoughtEvent[] = [];
    let reportBuffer = "";

    const pushStatus = (text: string, level: StatusLevel) => {
      statusLog.push({ timestamp: elapsed(), text, level });
      onUpdate(jobId, { statusLog: [...statusLog] });
    };

    pushStatus("Connecting to research pipeline...", "node");

    try {
      const res = await fetch("/api/research/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, config }),
        signal: abortRef.current.signal,
      });

      if (!res.ok || !res.body) throw new Error(`Stream failed: ${res.status}`);

      pushStatus("Stream connected — pipeline starting", "node");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let currentEventType: string | null = null;

      // State diffing from values snapshots
      let prevNotesCount = 0;
      let prevSupervisorMsgCount = 0;
      let seenResearchBrief = false;
      let seenCritique = false;
      let seenFinalReport = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) { currentEventType = null; continue; }

          if (trimmed.startsWith("event: ")) {
            currentEventType = trimmed.slice(7).trim();
            continue;
          }
          if (!trimmed.startsWith("data: ")) continue;
          const dataStr = trimmed.slice(6);
          if (dataStr === "[DONE]") continue;

          try {
            const data = JSON.parse(dataStr);

            if (currentEventType === "values") {
              // Detect state transitions by diffing snapshots

              // 1. Research brief — education_discovery done
              if (data.research_brief && !seenResearchBrief) {
                seenResearchBrief = true;
                const title = data.research_brief?.title || data.research_brief?.query || "";
                pushStatus("Research question analyzed" + (title ? `: ${String(title).slice(0, 80)}` : ""), "node");
              }

              // 2. Supervisor dispatching researchers — detect new ConductResearch tool calls
              const supervisorMsgs: unknown[] = data.supervisor_messages ?? [];
              if (supervisorMsgs.length > prevSupervisorMsgCount) {
                const newMsgs = supervisorMsgs.slice(prevSupervisorMsgCount);
                prevSupervisorMsgCount = supervisorMsgs.length;
                for (const msg of newMsgs) {
                  const m = msg as Record<string, unknown>;
                  const toolCalls_: unknown[] = (m.tool_calls as unknown[]) ?? (m.additional_kwargs as Record<string, unknown>)?.tool_calls as unknown[] ?? [];
                  for (const tc of toolCalls_) {
                    const t = tc as Record<string, unknown>;
                    const name = t.name ?? (t as Record<string, unknown>).function;
                    const args = (t.args ?? t.arguments ?? {}) as Record<string, unknown>;
                    if (name === "ConductResearch") {
                      const topic = String(args.research_topic ?? "").slice(0, 80);
                      if (topic) {
                        pushStatus(`Researcher dispatched: "${topic}"`, "researcher");
                        thoughts.push({ type: "sub_researcher_start", content: topic, timestamp: Date.now() });
                        onUpdate(jobId, { thoughts: [...thoughts] });
                      }
                    }
                  }
                }
              }

              // 3. Notes growing — a researcher completed
              const notes: unknown[] = data.notes ?? [];
              if (notes.length > prevNotesCount) {
                const added = notes.length - prevNotesCount;
                prevNotesCount = notes.length;
                pushStatus(`Researcher completed (${notes.length} researcher${notes.length > 1 ? "s" : ""} done)`, "node");
                // Count paper profiles as toolCalls proxy
                const profiles: unknown[] = data.paper_profiles ?? [];
                if (profiles.length > 0) {
                  onUpdate(jobId, { toolCalls: { papers_found: profiles.length } });
                }
              }

              // 4. Critique cycle
              if ((data.critique_cycles ?? 0) > 0 && !seenCritique) {
                seenCritique = true;
                pushStatus("Running critique — checking for gaps", "node");
              }

              // 5. Final report
              const report = data.final_report ?? data.final_report_generation?.final_report ?? "";
              if (report && !seenFinalReport) {
                seenFinalReport = true;
                reportBuffer = report;
                pushStatus("Report generated", "done");
                onUpdate(jobId, {
                  report,
                  status: "complete",
                  completedAt: Date.now(),
                  sources: _extractSources(data),
                  toolCalls: { ...toolCalls, papers_found: (data.paper_profiles as unknown[] ?? []).length },
                  statusLog: [...statusLog],
                  thoughts: [...thoughts],
                });
              }
            }
          } catch {}
        }
      }

      if (!seenFinalReport) {
        pushStatus("No report generated", "error");
        onUpdate(jobId, { status: "failed", error: "No report generated", statusLog: [...statusLog] });
      }
    } catch (err: unknown) {
      if ((err as Error).name === "AbortError") {
        pushStatus("Cancelled by user", "error");
        onUpdate(jobId, { status: "failed", error: "Cancelled", statusLog: [...statusLog] });
      } else {
        pushStatus(`Error: ${(err as Error).message}`, "error");
        onUpdate(jobId, { status: "failed", error: (err as Error).message, statusLog: [...statusLog] });
      }
    } finally {
      setActiveJobId(null);
    }
  }, [onUpdate]);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  return { activeJobId, startResearch, cancel };
}

function _extractSources(state: Record<string, unknown>) {
  const sources: { url: string; title: string }[] = [];
  const report = (state.final_report || "") as string;
  const urlRegex = /https?:\/\/[^\s\)\]"']+/g;
  for (const url of report.matchAll(urlRegex)) {
    sources.push({ url: url[0], title: url[0].split("/").pop() || url[0] });
  }
  return sources.slice(0, 30);
}
