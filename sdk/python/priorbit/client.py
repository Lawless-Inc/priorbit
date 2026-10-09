"""Thin MCP Streamable-HTTP client for Priorbit. Standard library only.

Auth order: explicit key → PRIORBIT_API_KEY → stored OAuth sign-in (`priorbit login`)."""
import json
import os
import time
import urllib.error
import urllib.request

from . import auth

DEFAULT_URL = os.environ.get("PRIORBIT_MCP_URL", "https://patdb-mcp-production.up.railway.app/mcp")
TIMEOUT = int(os.environ.get("PRIORBIT_TIMEOUT", "180"))
PROTOCOL = "2025-06-18"


class PriorbitError(Exception):
    def __init__(self, message, status=None, payload=None):
        super().__init__(message)
        self.status = status
        self.payload = payload


class Priorbit:
    """p = Priorbit(); p.search_patents(queries=["door security bar"], k=10) → dict (the tool's JSON).
    Any tool on the server is callable as a method; p.tools() lists them with input schemas."""

    def __init__(self, key=None, url=None, task_id=None):
        self.url = (url or DEFAULT_URL).rstrip("/")
        self._key = key or os.environ.get("PRIORBIT_API_KEY") or None
        self._session = None
        self._id = 0
        self._tools = None
        self.task_id = task_id

    # ---- transport
    def _auth(self):
        if self._key:
            return self._key
        tok = auth.access_token(self.url)
        if not tok:
            raise PriorbitError("Not signed in. Run `priorbit login` (free account) or set PRIORBIT_API_KEY.", 401)
        return tok

    def _post(self, body, notify=False):
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "Authorization": f"Bearer {self._auth()}"}
        if self._session:
            headers["mcp-session-id"] = self._session
        req = urllib.request.Request(self.url, data=json.dumps(body).encode(), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                sid = r.headers.get("mcp-session-id")
                if sid:
                    self._session = sid
                text = r.read().decode()
                ct = r.headers.get("content-type") or ""
        except urllib.error.HTTPError as e:
            text = e.read().decode(errors="replace")
            if e.code in (404, 400) and self._session:
                self._session = None            # stale session: caller re-initialises
            raise PriorbitError(f"Priorbit HTTP {e.code}: {text[:300]}", e.code) from None
        if notify:
            return None
        msg = None
        if "text/event-stream" in ct:
            for line in text.split("\n"):
                if line.startswith("data:"):
                    try:
                        j = json.loads(line[5:])
                    except ValueError:
                        continue
                    if "result" in j or "error" in j:
                        msg = j
        else:
            msg = json.loads(text) if text else None
        if not msg:
            raise PriorbitError("empty response from server")
        if msg.get("error"):
            raise PriorbitError(f"Priorbit: {msg['error'].get('message', 'error')}", payload=msg["error"])
        return msg.get("result")

    def _rpc(self, method, params, notify=False):
        if notify:
            return self._post({"jsonrpc": "2.0", "method": method, "params": params}, notify=True)
        self._id += 1
        return self._post({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params})

    def _ensure(self):
        if self._session:
            return
        self._rpc("initialize", {"protocolVersion": PROTOCOL, "capabilities": {}, "clientInfo": {"name": "priorbit-python", "version": "0.1.0"}})
        self._rpc("notifications/initialized", {}, notify=True)

    # ---- public
    def tools(self):
        """[{name, description, inputSchema}] from the live server (cached for this client)."""
        if self._tools is None:
            self._ensure()
            r = self._rpc("tools/list", {})
            self._tools = r.get("tools", [])
        return self._tools

    def call(self, tool, /, **args):
        """Call a tool and return its JSON as a dict (or the raw text when not JSON). task_id is threaded automatically."""
        if self.task_id and "task_id" not in args:
            args["task_id"] = self.task_id
        for attempt in range(2):
            try:
                self._ensure()
                r = self._rpc("tools/call", {"name": tool, "arguments": args})
                break
            except PriorbitError as e:
                if attempt == 0 and e.status in (404, 400) and not self._session:
                    continue
                raise
        text = "\n".join(c.get("text", "") for c in (r.get("content") or []) if c.get("type") == "text")
        if r.get("isError"):
            raise PriorbitError(text[:500] or "tool error", payload=r)
        try:
            out = json.loads(text)
        except ValueError:
            return text
        if isinstance(out, dict) and out.get("task_id") and not self.task_id:
            self.task_id = out["task_id"]
        return out

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return lambda **kw: self.call(name, **kw)


def ndjson_lines(result):
    """Flatten a tool result into NDJSON lines: one per result item, then a final {"meta": …} line.
    Works for any tool: lists called results/results_* become items, everything else goes to meta."""
    if not isinstance(result, dict):
        return [json.dumps({"text": result}, ensure_ascii=False)]
    items, meta = [], {}
    for k, v in result.items():
        if k == "results" and isinstance(v, list):
            items.extend(v)
        elif isinstance(v, dict) and isinstance(v.get("results"), list) and k not in ("coverage",):
            for it in v["results"]:
                items.append({"_group": k, **it} if isinstance(it, dict) else {"_group": k, "value": it})
            meta[k] = {kk: vv for kk, vv in v.items() if kk != "results"}
        else:
            meta[k] = v
    return [json.dumps(it, ensure_ascii=False) for it in items] + [json.dumps({"meta": meta}, ensure_ascii=False)]
