import { NextRequest } from "next/server";
import * as fs from "fs";
import * as path from "path";

export const dynamic = "force-dynamic";

const BACKEND_ROOT = path.join(
  process.env.HOME || "",
  "Documents/A-Moosa-Dev/AI-EDU-Dev/eduagent/eduagent_backend/output"
);

function findLogFile(sessionId: string): string | null {
  // Check frontend run dir first, then CLI dir
  const candidates = [
    path.join(BACKEND_ROOT, sessionId, "run.log"),
    path.join(BACKEND_ROOT, "final-test", sessionId, "run.log"),
  ];
  for (const p of candidates) {
    if (fs.existsSync(p)) return p;
  }
  return null;
}

export async function GET(req: NextRequest) {
  const sessionId = req.nextUrl.searchParams.get("id");
  if (!sessionId) return new Response("Missing id", { status: 400 });

  const stream = new ReadableStream({
    start(controller) {
      let offset = 0;
      let logPath: string | null = null;
      let done = false;

      const send = (line: string) => {
        controller.enqueue(
          new TextEncoder().encode(`data: ${JSON.stringify({ line })}\n\n`)
        );
      };

      const poll = () => {
        if (done) return;

        // Wait for the log file to appear (run may not have started yet)
        if (!logPath) {
          logPath = findLogFile(sessionId);
          if (!logPath) return;
        }

        try {
          const stat = fs.statSync(logPath);
          if (stat.size > offset) {
            const buf = Buffer.alloc(stat.size - offset);
            const fd = fs.openSync(logPath, "r");
            fs.readSync(fd, buf, 0, buf.length, offset);
            fs.closeSync(fd);
            offset = stat.size;

            const text = buf.toString("utf8");
            const lines = text.split("\n");
            for (const line of lines) {
              if (line.trim()) send(line);
            }
          }
        } catch {}
      };

      const interval = setInterval(poll, 500);

      req.signal.addEventListener("abort", () => {
        done = true;
        clearInterval(interval);
        controller.close();
      });
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "X-Accel-Buffering": "no",
    },
  });
}
