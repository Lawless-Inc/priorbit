---
name: lawless-patent
description: >
  US patent search and freedom-to-operate (FTO) screening for a physical product, powered by
  the Lawless patent database MCP server (12M+ US granted patents with full claims, CPC,
  assignees and maintenance-fee status). Use when the user wants to know which US patents
  a product might infringe, find patents similar to a product or patent, list a company's
  patents, check whether patents are still in force, or run a prior-art style search.
  Results are candidates for a lawyer's review, not legal conclusions.
---

# Lawless Patent Search

You have (or can connect) an MCP server named `lawless-patent`. It searches US granted patents
and ranks candidates by relevance to *the user's product*. Your job: turn the product into good
queries across several independent lanes, read the candidates, and report the ones worth a
lawyer's time — with patent numbers, why each matters, and what to check next.

## 0. Make sure the server is connected

Check whether tools like `search_titles` / `set_product` are available.
If not, the user needs an API key from Lawless (ask them; never invent one) and the server added
to their client:

- **Claude Code** (preferred: the plugin wires this up automatically):
  `claude plugin marketplace add Lawless-Inc/skills` then `claude plugin install lawless-patent@lawless` (prompts for the key)
  Manual alternative:
  `claude mcp add --transport http lawless-patent https://patdb-mcp-production.up.railway.app/mcp --header "Authorization: Bearer <API_KEY>"`
- **Cursor / Windsurf / VS Code / other MCP clients**: add an HTTP (streamable) MCP server
  - url: `https://patdb-mcp-production.up.railway.app/mcp`
  - header: `Authorization: Bearer <API_KEY>`
- **Codex** (`~/.codex/config.toml`):
  ```toml
  [mcp_servers.lawless-patent]
  url = "https://patdb-mcp-production.up.railway.app/mcp"
  bearer_token_env_var = "LAWLESS_PATENT_API_KEY"
  ```

Store the key in an environment variable or the client's secret store, never in a committed file.
A `401` means the key is missing or wrong; `rate_limited` / `quota_exceeded` mean slow down or wait.

## 1. Set the product first

Call `set_product` once per product. Every search after it is re-ranked for relevance to this product;
without it you only get raw recall order.

- Best: `text` = what the product is, its core structure/mechanism, materials, how it's used.
- `url` (a product page) works only after `bind_oxylabs(username, password)` with the user's own
  Oxylabs account. If they don't have one, write the `text` yourself from what they told you.
- Read back `product_profile` in the response. A wrong profile silently ruins the ranking.

## 2. Search several lanes — no single lane finds everything

Measured on real lawyer-verified cases: titles alone find ~1/3 of relevant patents; combining lanes roughly doubles that.

| Lane | Tool | How to use it well |
|---|---|---|
| Titles | `search_titles(queries=[...])` | Give 4-10 phrasings at once: generic name ("back shaver"), functional name ("shaving apparatus"), patent-style ("device for …"), key components. Results are interleaved per phrasing; `by_query` shows which phrasing worked. |
| Design patents | `search_titles(queries=[...], patent_type="design")` | Article names of 1-3 words ("door security bar", "neck pillow"). Design patents have no CPC in this database, so this is their main lane. |
| Classification | `cpc_describe` → `cpc_browse(symbols, rank_terms=...)` | Guess 2-5 CPC main groups yourself (e.g. `B63H20/`), verify with `cpc_describe`, then browse with `rank_terms` = claim-style component words. `too_broad` → use finer groups. Also consider the *component's* class (a pillow's valve lives in F16K). |
| Owners | `resolve_assignee(name)` → `list_by_assignee(organizations)` | Resolve brand/maker names to exact assignee strings first (a group often has several entities — pick all relevant ones). The product's own brand and its known competitors are high-value. |
| Claims | `search_claims(terms, within_cpc=[...] / within_assignees=[...])` | Best inside a scope. Without a scope it searches all claims: slow and weak — last resort. |
| Expansion | `more_like_these(patent_numbers)` | After you've confirmed 2-5 core patents: same-title, same-owner and co-classified neighbours. |

## 3. Read results correctly

- Each hit has `status`. Default `in_force_only=true` drops patents that are certainly lapsed or expired; `unknown`/`application_unverified` are kept. Pass `in_force_only=false` when you need old art or reference patents.
- `relevance` (0-1) = similarity to the product, not an infringement verdict. Many patents in the same category score alike; read titles/claims to separate them.
- `recall_rank` = position before re-ranking. `rerank.applied=false` + `reason` tells you why no re-ranking happened.
- 0 results only means no match in this lane of this corpus. Coverage: **US granted patents up to 2025-12-30**; no pending applications, no non-US patents, no drawings. Say so in your report; never state "no patents exist".
- `get_patents(numbers)` returns title, owners, CPC, claim count and status with its basis. Status is rule-based — tell the user to verify legal status before relying on it.

## 4. Report

For each patent worth attention: number (link `https://patents.google.com/patent/US<number>`), title,
owner, status, one-line reason tied to the product's features, and which lane found it.
Then list what you could not cover (non-US, pending, design look-alikes that need images) and the
searches you would run next. Keep the user in charge of legal judgment.
