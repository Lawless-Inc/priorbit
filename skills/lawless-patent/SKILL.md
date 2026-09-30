---
name: lawless-patent
description: >
  Lawless IPDB — an agent-native IP database exposed as an MCP server. Covers US granted patents
  (full claims, CPC, design-patent USPC D classes, maintenance-fee status) and ~8.7M published US
  applications with official USPTO status. Use it whenever the user wants to search, list, look up
  or compare US patents and applications — by title wording, classification, owner/applicant,
  claim language, or starting from known patents.
---

# Lawless IPDB

You have (or can connect) an MCP server that searches a US patent and published-application database.
There is no required workflow: combine the tools however fits the user's question.

## Connect

If tools like `search_titles` are missing, the user needs a Lawless API key (ask them; never invent one):

- **Claude Code**: `claude plugin marketplace add Lawless-Inc/skills` then `claude plugin install lawless-patent@lawless` (prompts for the key).
- **Other MCP clients (Cursor, Windsurf, VS Code, …)**: HTTP MCP server `https://patdb-mcp-production.up.railway.app/mcp` with header `Authorization: Bearer <API_KEY>`.
- **Codex** (`~/.codex/config.toml`):
  ```toml
  [mcp_servers.lawless-patent]
  url = "https://patdb-mcp-production.up.railway.app/mcp"
  bearer_token_env_var = "LAWLESS_PATENT_API_KEY"
  ```

`401` = missing/wrong key; `rate_limited` / `quota_exceeded` = slow down or wait.

## Tools

| Tool | What it does |
|---|---|
| `describe_corpus_tool` | What the database covers and each source's cut-off date. Check it once when coverage matters. |
| `search_titles(queries=[...])` | Title search over patents and applications. Give several phrasings at once; results are interleaved per phrasing (`by_query` shows which worked). `patent_type`: `design`, `utility`, or `application`. |
| `cpc_describe` / `cpc_browse` | Check CPC symbols, then list a class (optionally ranked by claim words via `rank_terms`). `too_broad` returns finer symbols. |
| `design_classes` / `design_class_browse` | Design patents use USPC D classes, not CPC. Search class titles by keyword or inspect a class (`D28/`), then list it. About half of the D subclasses have no title, so browse the main class when keyword search misses. |
| `resolve_assignee` / `list_by_assignee` | Resolve a company name to exact owner/applicant strings (counts shown for patents and applications), then list them. |
| `search_claims(terms, within_cpc / within_assignees / within_patents)` | Claim-language search; best inside a scope. |
| `more_like_these(patent_numbers)` | Neighbours of known documents: same title wording, owner, CPC, or D class. |
| `get_patents(numbers)` | Title, dates, owners, CPC / D classes, claim count, status with its basis. |
| `set_product(text)` | Optional: a short description to rank results by relevance to it (`rerank=false` turns it off per call). |
| `explain_terms` / `suggest_terms` | How common each word is; corpus vocabulary to try next. |

## Reading results

- Every hit has a `status` with a `status_basis`. Results are **not filtered by default**; pass `in_force_only=true` to drop lapsed, expired and abandoned documents.
- Application statuses come from USPTO: `pending`, `allowed` (notice of allowance issued), `abandoned`. Granted applications are replaced by their patent (`via_publication` names the original).
- 0 results means no match in that search, not that nothing exists.
- `relevance` (only when a profile is set) is similarity to that description, not a legal judgment.
