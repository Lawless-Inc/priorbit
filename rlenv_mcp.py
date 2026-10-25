#!/usr/bin/env python3
"""Priorbit RL environment as a local MCP server (stdio), so any MCP-capable agent (Claude Code, Codex, Cowork) can
play an episode with its own model: env_reset → env_step (repeat) → env_submit.

  claude --strict-mcp-config --mcp-config '{"mcpServers":{"rlenv":{"type":"stdio","command":"python3","args":["services/ipdb/rlenv_mcp.py"]}}}' \
         -p "Play one episode of the Priorbit environment: call env_reset, work the task with env_step, then env_submit."

Environment base URL: PRIORBIT_ENV_URL (default https://patdb-mcp-production.up.railway.app). No sign-in needed.
Only the standard library plus the `mcp` package are used.
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.types import Image

BASE = os.environ.get("PRIORBIT_ENV_URL", "https://patdb-mcp-production.up.railway.app").rstrip("/")
AGENT = os.environ.get("PRIORBIT_ENV_AGENT", "mcp-agent")
mcp = FastMCP("priorbit-rlenv", instructions=(
    "Priorbit RL environment. One episode = one IP task under a time snapshot (as_of). Call env_reset to get the task, "
    "work it with env_step (tools: search_patents, get_patents, search_trademarks, get_marks, resolve_owner, lookup_classes, "
    "get_drawings, get_playbook; same arguments as the Priorbit MCP tools), then env_submit with the final answer in the "
    "format the task asks for. Only the final answer is rewarded. Never look up lawsuits, dockets or plaintiffs: that scores 0."))

_STATE = {"episode_id": None}


def _post(path, body):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(), headers={"content-type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            return json.load(e)
        except Exception:  # noqa: BLE001
            return {"error": f"HTTP {e.code}"}


@mcp.tool()
def env_reset(family: str = "", task_id: str = "", seed: int | None = None, config: dict | None = None) -> str:
    """Start a new episode. family: tro_product2patent | brand2patents | prosecution | '' (random). task_id picks one task
    (see env_tasks). config (optional): {"as_of": "YYYY-MM-DD" | "knowable" | "knowable+30d", "snapshot": "on"|"off",
    "max_steps": 1..200, "tools": [...subset...], "reward": "strict"|"recall"|{...}}. Returns the task (prompt, images,
    as_of) and the episode id (kept for you; env_step / env_submit use it automatically)."""
    body = {"agent": AGENT}
    if family:
        body["family"] = family
    if task_id:
        body["task_id"] = task_id
    if seed is not None:
        body["seed"] = seed
    if config:
        body["config"] = config
    r = _post("/env/reset", body)
    if r.get("episode_id"):
        _STATE["episode_id"] = r["episode_id"]
    return json.dumps({k: r.get(k) for k in ("episode_id", "task_id", "family", "as_of", "as_of_basis", "max_steps", "config", "task", "error")}, ensure_ascii=False, indent=1)


@mcp.tool()
def env_tools() -> str:
    """The environment's tools with argument JSON Schemas, which arguments matter first, which the environment overrides,
    and ready-made example calls per tool (placeholders {product} {product_short} {entity} = fill from the task). Read
    this once before env_step."""
    with urllib.request.urlopen(urllib.request.Request(BASE + "/env/tools"), timeout=60) as r:
        return r.read().decode()


@mcp.tool()
def env_tasks(family: str = "") -> str:
    """List the task catalogue (ids, family, default as_of, label; no answers) so a fixed set can be replayed."""
    req = urllib.request.Request(BASE + "/env/tasks" + (f"?family={family}" if family else ""))
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode()


@mcp.tool()
def env_step(tool: str, args: dict, episode_id: str = ""):
    """One action: call a Priorbit tool inside the episode. tool = search_patents | get_patents | search_trademarks |
    get_marks | resolve_owner | lookup_classes | get_drawings | get_playbook; args = that tool's arguments.
    Examples: search_patents {"queries": ["magnetic phone mount"], "k": 30} · search_patents {"queries": ["phone mount"],
    "patent_type": "design"} · get_patents {"patent_numbers": ["D853642", "10308005"], "parts": ["summary", "claims"]} ·
    resolve_owner {"name": "Dyson Technology Limited"} · lookup_classes {"query": "door security bar"} · get_drawings
    {"patent_number": "D853642"}. env_tools() lists every argument and more examples. The observation is filtered to the
    task's as_of date (unless the episode config turned the snapshot off)."""
    eid = episode_id or _STATE["episode_id"]
    if not eid:
        return json.dumps({"error": "call env_reset first"})
    r = _post("/env/step", {"episode_id": eid, "tool": tool, "args": args or {}})
    obs = r.get("observation")
    img = obs.pop("image_jpeg", None) if isinstance(obs, dict) else None
    text = json.dumps({"step": r.get("step"), "steps_left": r.get("steps_left"), "observation": obs, "error": r.get("error")}, ensure_ascii=False, default=str)
    if img and img.startswith("data:image/jpeg;base64,"):
        return [text, Image(data=base64.b64decode(img.split(",", 1)[1]), format="jpeg")]
    return text


@mcp.tool()
def env_submit(answer: str, episode_id: str = "") -> str:
    """Finish the episode with the final answer (the exact format the task prompt asks for). Returns the reward in [0, 1],
    the breakdown and the ground truth."""
    eid = episode_id or _STATE["episode_id"]
    if not eid:
        return json.dumps({"error": "call env_reset first"})
    r = _post("/env/submit", {"episode_id": eid, "answer": answer})
    return json.dumps(r, ensure_ascii=False, indent=1, default=str)


if __name__ == "__main__":
    mcp.run()
