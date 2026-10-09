"""`priorbit` — every server tool becomes a subcommand, generated from the live tools/list schema.

    priorbit login                                   sign in once (free account)
    priorbit tools                                   list tools and arguments
    priorbit search_patents --queries "door security bar" --patent_type design --k 10
    priorbit get_patents --patent_numbers 7532200,D949612 --parts summary
    priorbit call search_trademarks --json '{"text":"WOBBLY LIFE","k":5}'
Output is NDJSON (one result per line, then a {"meta": …} line) so it pipes into jq / grep / another agent.
"""
import argparse
import json
import os
import sys

from . import auth
from .client import DEFAULT_URL, Priorbit, PriorbitError, ndjson_lines

EPILOG = "Docs: https://uselawless.com/docs · Set PRIORBIT_API_KEY to skip login · --raw prints the whole JSON instead of NDJSON"


def _type_of(schema):
    t = schema.get("type")
    if isinstance(t, list):
        t = next((x for x in t if x != "null"), None)
    if not t and "anyOf" in schema:
        kinds = [s.get("type") for s in schema["anyOf"] if isinstance(s, dict)]
        if "array" in kinds:
            return "array"
        t = next((k for k in kinds if k and k != "null"), "string")
    return t or "string"


def _coerce(v, schema):
    t = _type_of(schema)
    if v is None:
        return None
    if t == "array":
        return [x.strip() for x in str(v).split(",") if x.strip()] if isinstance(v, str) else v
    if t == "integer":
        return int(v)
    if t == "number":
        return float(v)
    if t == "boolean":
        return str(v).lower() in ("1", "true", "yes", "y", "on")
    return v


def _add_tool_args(sub, tool):
    props = (tool.get("inputSchema") or {}).get("properties") or {}
    required = set((tool.get("inputSchema") or {}).get("required") or [])
    for name, schema in props.items():
        desc = (schema.get("description") or "").split("\n")[0]
        t = _type_of(schema)
        hint = {"array": " (comma-separated)", "integer": " (int)", "number": " (number)", "boolean": " (true/false)"}.get(t, "")
        if schema.get("enum"):
            hint += " [" + "|".join(str(x) for x in schema["enum"] if x != "") + "]"
        sub.add_argument(f"--{name}", dest=name, required=name in required, help=(desc[:140] + hint) or None, metavar=t.upper()[:3])
    sub.add_argument("--json", dest="_json", help="extra / full arguments as a JSON object (merged over the flags)")


def build_parser(tools):
    common = argparse.ArgumentParser(add_help=False, allow_abbrev=False)      # accepted before or after the subcommand
    common.add_argument("--server", default=DEFAULT_URL, help="MCP endpoint (default: production)")
    common.add_argument("--key", default=None, help="API key (else PRIORBIT_API_KEY, else stored sign-in)")
    common.add_argument("--task", default=None, help="task_id to continue a piece of work")
    common.add_argument("--raw", action="store_true", help="print the full JSON instead of NDJSON")
    common.add_argument("--pretty", action="store_true", help="indent the raw JSON")
    p = argparse.ArgumentParser(prog="priorbit", description="Priorbit — the IP database for agents (US patents, applications, trademarks).", epilog=EPILOG, parents=[common], allow_abbrev=False)
    sp = p.add_subparsers(dest="cmd")
    sp.add_parser("login", help="sign in with a free uselawless.com account (OAuth, opens a browser)", parents=[common]).add_argument("--no-browser", action="store_true")
    sp.add_parser("logout", help="forget the stored sign-in", parents=[common])
    sp.add_parser("tools", help="list tools and their arguments (from the live server)", parents=[common])
    c = sp.add_parser("call", help="call any tool by name with a JSON object", parents=[common])
    c.add_argument("tool"); c.add_argument("--json", dest="_json", required=True)
    for t in tools or []:
        s = sp.add_parser(t["name"], help=(t.get("description") or "").split("\n")[0][:110], description=t.get("description"), parents=[common], allow_abbrev=False)
        _add_tool_args(s, t)
    return p


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # commands that do not need the live schema
    head = [a for a in argv if not a.startswith("-")]
    pre = argparse.ArgumentParser(add_help=False, allow_abbrev=False)   # no abbreviations: --k must never mean --key
    pre.add_argument("--server", default=DEFAULT_URL); pre.add_argument("--key", default=None)
    known, _ = pre.parse_known_args(argv)
    if head and head[0] == "login":
        try:
            cred = auth.login(known.server, open_browser="--no-browser" not in argv, print_url=lambda s: print(s, file=sys.stderr))
        except auth.AuthError as e:
            print(f"login failed: {e}", file=sys.stderr); return 2
        print(json.dumps({"signed_in": True, "issuer": cred.get("issuer"), "credentials": auth.CRED_PATH})); return 0
    if head and head[0] == "logout":
        print(json.dumps({"signed_out": auth.clear_credentials()})); return 0
    client = Priorbit(key=known.key, url=known.server)
    try:
        tools = client.tools()
    except PriorbitError as e:
        if e.status == 401:
            print("Not signed in. Run `priorbit login` (free account) or set PRIORBIT_API_KEY.", file=sys.stderr); return 2
        print(f"cannot reach Priorbit: {e}", file=sys.stderr); return 3
    parser = build_parser(tools)
    a = parser.parse_args(argv)
    if a.cmd == "tools":
        for t in tools:
            props = (t.get("inputSchema") or {}).get("properties") or {}
            req = set((t.get("inputSchema") or {}).get("required") or [])
            print(json.dumps({"tool": t["name"], "description": (t.get("description") or "").split("\n")[0], "args": [("*" if k in req else "") + k for k in props]}, ensure_ascii=False))
        return 0
    if not a.cmd:
        parser.print_help(); return 1
    if a.task:
        client.task_id = a.task
    if a.cmd == "call":
        name, args = a.tool, json.loads(a._json)
    else:
        name = a.cmd
        tool = next(t for t in tools if t["name"] == name)
        props = (tool.get("inputSchema") or {}).get("properties") or {}
        args = {k: _coerce(getattr(a, k), props[k]) for k in props if getattr(a, k, None) is not None}
        if a._json:
            args.update(json.loads(a._json))
    try:
        out = client.call(name, **args)
    except PriorbitError as e:
        print(json.dumps({"error": str(e), "status": e.status}, ensure_ascii=False), file=sys.stderr); return 4
    if a.raw or a.pretty:
        print(json.dumps(out, ensure_ascii=False, indent=2 if a.pretty else None))
    else:
        for line in ndjson_lines(out):
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
