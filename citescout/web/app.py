"""Small local web UI: type a question, watch the agent work, read the cited brief.

Run: `citescout-web` (or `uvicorn citescout.web.app:app`), then open http://127.0.0.1:8000
The agent runs in a worker thread; its trace events stream to the page over SSE.
"""

from __future__ import annotations

import json
import queue
import threading
from pathlib import Path
from typing import Iterator

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, StreamingResponse

from citescout.agent import ResearchAgent
from citescout.config import load_settings
from citescout.render import to_markdown

app = FastAPI(title="citescout")
_STATIC = Path(__file__).parent / "static"


@app.get("/")
def index() -> FileResponse:
    return FileResponse(_STATIC / "index.html")


@app.get("/api/ask")
def ask(q: str = Query(..., min_length=5, max_length=300), max_searches: int = 6) -> StreamingResponse:
    events: "queue.Queue[tuple[str, dict] | None]" = queue.Queue()

    def work() -> None:
        try:
            settings = load_settings(max_searches=max(1, min(max_searches, 10)))
            brief = ResearchAgent(settings, trace=lambda e, d: events.put((e, d))).run(q)
            from citescout import history
            history.save(brief, settings.cache_dir)
            data = brief.model_dump(mode="json")
            data["markdown"] = to_markdown(brief)
            events.put(("brief", data))
        except Exception as exc:  # noqa: BLE001 - surfaced to the page
            events.put(("error", {"message": str(exc)[:300]}))
        finally:
            events.put(None)

    threading.Thread(target=work, daemon=True).start()

    def stream() -> Iterator[str]:
        while (item := events.get()) is not None:
            event, data = item
            yield f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/api/history")
def recent() -> list[dict]:
    """Questions with saved briefs, newest first. Re-asking one replays cached searches (0 credits)."""
    from citescout import history

    return [{"question": q, "runs": n, "last": at.isoformat()}
            for q, n, at in history.list_questions(load_settings().cache_dir)[:12]]


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
