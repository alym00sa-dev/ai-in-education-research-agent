"use client";
import { useCallback, useRef, useState } from "react";
import { Job, ResearchConfig, ThoughtEvent, StatusLine, StatusLevel } from "@/lib/types";

// Node name → human label (v2 graph nodes)
const NODE_LABELS: Record<string, string> = {
  education_discovery:      "Analyzing research question",
  research_supervisor:      "Research supervisor planning",
  executive_summary:        "Building executive summary",
  critique:                 "Critiquing evidence gaps",
  citation_connector:       "Connecting citations",
  final_report_generation:  "Generating final report",
  qa_audit:                 "Running QA audit",
  kg_write:                 "Writing to knowledge graph",
  // supervisor subgraph nodes
  researcher:               "Researcher working",
  researcher_reflect:       "Reflecting on coverage",
  compress_research:        "Compressing research findings",
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

    const RENDER_URL = process.env.NEXT_PUBLIC_RENDER_API_URL || "http://127.0.0.1:2024";

    try {
      // Step 1: create thread + get stream payload from Vercel (fast, no timeout concern)
      const initRes = await fetch("/api/research/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, config, jobId }),
        signal: abortRef.current.signal,
      });
      if (!initRes.ok) throw new Error(`Init failed: ${initRes.status}`);
      const { thread_id, streamPayload } = await initRes.json();

      pushStatus("Pipeline thread created — connecting stream...", "node");

      // Step 2: stream directly from Render, bypassing Vercel's execution time limit
      const res = await fetch(
        `${RENDER_URL}/threads/${thread_id}/runs/stream`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(streamPayload),
          signal: abortRef.current.signal,
        }
      );

      if (!res.ok || !res.body) throw new Error(`Stream failed: ${res.status}`);

      pushStatus("Stream connected — pipeline starting", "node");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let currentEventType: string | null = null;

      // State diffing from values snapshots
      let prevNotesCount = 0;
      let prevProfilesCount = 0;
      let prevCompressCount = 0;
      let prevDraftCount = 0;
      let prevCritiqueCount = 0;
      let prevSupervisorMsgCount = 0;
      let seenResearchBrief = false;
      let seenFinalReport = false;
      let seenQAReport = false;

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

            // Custom log events emitted directly from graph nodes — display verbatim
            if (currentEventType === "custom") {
              const msg = (data as Record<string, unknown>).message as string | undefined;
              if (msg) pushStatus(msg, "node");
            }

            // Emit node-level status from LangGraph updates events
            if (currentEventType === "updates") {
              for (const node of Object.keys(data as Record<string, unknown>)) {
                if (NODE_LABELS[node]) {
                  pushStatus(`[${node}] ${NODE_LABELS[node]}...`, "node");
                }
              }
            }

            if (currentEventType === "values") {
              // Detect state transitions by diffing snapshots

              // 1. Research brief — education_discovery done
              if (data.research_brief && !seenResearchBrief) {
                seenResearchBrief = true;
                pushStatus("[education_discovery] Research brief ready.", "node");
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
                        pushStatus(`[research_supervisor] Dispatching researcher: "${topic}"`, "node");
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
                const newCount = notes.length - prevNotesCount;
                prevNotesCount = notes.length;
                pushStatus(`[researcher] ${newCount} new thread(s) completed — ${notes.length} total notes`, "node");
              }

              // 4. Paper profiles growing
              const profiles: unknown[] = data.paper_profiles ?? [];
              if (profiles.length > prevProfilesCount) {
                prevProfilesCount = profiles.length;
                pushStatus(`[pdf_extractor] ${profiles.length} paper profiles so far`, "node");
                onUpdate(jobId, { toolCalls: { papers_found: profiles.length } });
              }

              // 5. Compress findings iterations
              const compressHist: unknown[] = data.compress_findings_history ?? [];
              if (compressHist.length > prevCompressCount) {
                prevCompressCount = compressHist.length;
                pushStatus(`[compress_findings] Iteration ${compressHist.length} evidence summary ready.`, "node");
              }

              // 6. Draft report iterations
              const draftHist: unknown[] = data.draft_report_history ?? [];
              if (draftHist.length > prevDraftCount) {
                prevDraftCount = draftHist.length;
                pushStatus(`[draft_report] Iteration ${draftHist.length} draft ready.`, "node");
              }

              // 7. Critique iterations
              const critiqueHist: unknown[] = data.critique_history ?? [];
              if (critiqueHist.length > prevCritiqueCount) {
                prevCritiqueCount = critiqueHist.length;
                pushStatus(`[critique] Iteration ${critiqueHist.length} critique ready.`, "node");
              }

              // 8. Final report — store report but stay "running" until QA is done
              const report = data.final_report ?? data.final_report_generation?.final_report ?? "";
              if (report && !seenFinalReport) {
                seenFinalReport = true;
                reportBuffer = report;
                pushStatus("[final_report] Final report generated — waiting for QA audit…", "done");
                onUpdate(jobId, {
                  report,
                  sources: _extractSources(data),
                  toolCalls: { ...toolCalls, papers_found: (data.paper_profiles as unknown[] ?? []).length },
                  statusLog: [...statusLog],
                  thoughts: [...thoughts],
                });
              }

              // 9. QA report — complete the job only once QA is done
              const qaReport = (data.qa_report ?? "") as string;
              if (qaReport && !seenQAReport) {
                seenQAReport = true;
                const completedAt = Date.now();
                pushStatus("[qa_audit] QA audit complete.", "done");
                onUpdate(jobId, {
                  qaReport,
                  status: "complete",
                  completedAt,
                  statusLog: [...statusLog],
                });
                // Persist completed run to Redis via API (enables cross-device session history)
                fetch("/api/runs", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({
                    id: jobId,
                    query,
                    report: reportBuffer,
                    qaReport,
                    paperCount: (data.paper_profiles as unknown[] ?? []).length,
                    createdAt: jobStart,
                    completedAt,
                    status: "complete",
                    config,
                  }),
                }).catch(() => {});
              }
            }
          } catch {}
        }
      }

      if (!seenFinalReport) {
        pushStatus("No report generated", "error");
        onUpdate(jobId, { status: "failed", error: "No report generated", statusLog: [...statusLog] });
      } else if (!seenQAReport) {
        // Stream ended with report but no QA — still complete
        onUpdate(jobId, { status: "complete", completedAt: Date.now(), statusLog: [...statusLog] });
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
