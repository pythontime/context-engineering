# Pre-Class Checklist - Tomorrow Morning

**Class date:** 2026-04-27
**Owner:** Tim Warner
**Repo:** `C:\github\context-engineering`
**Run from:** `src/warnerco/backend/` unless noted

Run top to bottom. If a step fails, fix before moving on; nothing below assumes a broken step succeeded.

## 1. Environment

- [ ] **Python 3.13 active**
  ```bash
  python --version
  ```
  - Expect: `Python 3.13.x`
  - If `3.14.x`: stop and switch interpreters (`uv` will not build wheels for 3.14 yet). Use `uv python install 3.13` then `uv python pin 3.13`.

- [ ] **Sync deps**
  ```bash
  cd src/warnerco/backend
  uv sync
  ```
  - Expect: clean install, no resolver errors.

## 2. Data Layer

- [ ] **Knowledge graph DB exists**
  - File: `src/warnerco/backend/data/graph/knowledge.db`
  - If missing:
    ```bash
    uv run python scripts/index_graph.py
    ```
  - Expect: indexer logs ~25 schematics, ~117 entities, ~221 relationships.

## 3. Server Lifecycle

- [ ] **Free port 8000**
  ```bash
  uv run warnerco-restart --kill-only
  ```
  - Expect: confirms no listener on `:8000` (or kills the stale one).

- [ ] **Start server**
  ```bash
  uv run warnerco-restart
  ```
  - Expect: uvicorn boots, `Application startup complete.` on stderr.

- [ ] **Dashboard reachable**
  - Open <http://localhost:8000/dash> in a browser.
  - Expect: dashboard renders (no 404, no white screen).

## 4. REST Smoke Test

- [ ] **Memory stats endpoint**
  ```bash
  curl -i http://localhost:8000/api/memory/stats
  ```
  - Expect: `HTTP/1.1 200 OK`, JSON body reporting **25 schematics**.

## 5. MCP Inspector

- [ ] **Launch Inspector against the stdio server**
  ```bash
  npx @modelcontextprotocol/inspector uv run warnerco-mcp
  ```
  - Expect: Inspector UI opens (default <http://localhost:5173>) and the server appears as `connected`.

- [ ] **List tools via progressive loading**
  - In Inspector, call:
    ```
    warn_search_tools(query="", detail="name")
    ```
  - Expect: **21 tools listed** (the two meta tools `warn_search_tools` and `warn_describe_tool` self-skip; total decorated tools is 23).

- [ ] **Verify graph stats**
  - Call: `warn_graph_stats`
  - Expect: **117 entities**, **221 relationships**, 6 distinct predicates.

- [ ] **Verify semantic search**
  - Call: `warn_semantic_search(query="actuator")`
  - Expect: non-empty `results` array with schematic IDs and similarity scores.

## 6. Final Sanity

- [ ] Browser tab on `/dash` still alive.
- [ ] Inspector tab still connected.
- [ ] Terminal hosting `warnerco-restart` shows no stack traces.
- [ ] Coffee.

If all boxes are checked, you are clear to teach.
