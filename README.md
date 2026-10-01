# Lawless Patent — Priorbit IP database for your agent

An IP database built for agents: US granted patents (full claims), published applications (official status),
US trademarks in every status, owners and inventors linked across both, live USPTO documents and drawing images,
and e-commerce product pages. One plugin gives your agent the MCP tools **and** a skill that tells it to use them
for patent and trademark work — no API key needed to start.

Read the skill: [SKILL.md](skills/lawless-patent/SKILL.md)

## Install

### Codex

```bash
codex plugin marketplace add Lawless-Inc/skills
codex plugin add lawless-patent@lawless
```

### Claude Code

```bash
claude plugin marketplace add Lawless-Inc/skills
claude plugin install lawless-patent@lawless
```

Restart the client (Codex desktop: quit with ⌘Q and reopen), then start a new conversation.

### Other clients (Cursor, Claude.ai, Windsurf, …)

Add a remote MCP server with this URL — no key, no header:

```
https://patdb-mcp-production.up.railway.app/mcp
```

Then copy [SKILL.md](skills/lawless-patent/SKILL.md) into your client's rules or skills so the agent knows when to use it.

## Free use and keys

Without a key each network gets a daily free quota (about five full FTO screenings a day). A key raises the
limits (including product-page fetching, 10 a day per network without a key): use `https://patdb-mcp-production.up.railway.app/mcp?key=YOUR_KEY`.
Ask Lawless at https://uselawless.com.

## Try

> Do a US FTO screening for https://www.amazon.com/dp/B0GSYWD5RT

> Who owns the patents behind the SECURADOOR brand?

> Is US 10,435,928 still in force, when does it expire, and who owns it now?

Results are research leads for an attorney, not legal opinions.

## License

MIT
