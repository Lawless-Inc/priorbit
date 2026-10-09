# Priorbit — the IP database for your agent

> **Priorbit needs a free uselawless.com account.** Your AI app asks you to sign in the first time it calls Priorbit;
> create the account at https://uselawless.com/login?returnTo=%2Faccount&mode=signup (Google works). Go is free: 200 credits a month.
>
> **Priorbit 需要一个免费的 uselawless.com 账号。** AI 应用第一次调用 Priorbit 时会请你登录；在上面的链接注册即可（可用 Google）。Go 免费，每月 200 积分。

An IP database built for agents: US granted patents (full claims), published applications (official status),
US trademarks in every status, owners and inventors linked across both, live USPTO documents and drawing images,
prosecution file wrappers (office actions and responses as page images), PTAB trials, and e-commerce product pages. One plugin gives your agent the MCP tools **and** a skill that tells it to use them
for patent and trademark work. Sign in once with a free account.

Read the skill: [SKILL.md](skills/priorbit/SKILL.md)

## Install

### Codex

```bash
codex plugin marketplace add Lawless-Inc/priorbit
codex plugin add priorbit@lawless
```

Both lines can be pasted straight into the Codex chat box; Codex runs them. During the install Codex opens its
own sign-in window: sign in to uselawless.com (Google or email) and click **Allow**. Once per computer.

Only if no sign-in window appeared, run `codex mcp login priorbit` — it opens one browser tab. Do not run it while
a Codex sign-in window is already open; that is how you end up with two login windows at once.

### Claude Code

```bash
claude plugin marketplace add Lawless-Inc/priorbit
claude plugin install priorbit@lawless
```

Then, in a new session, type `/mcp`, pick **priorbit** and choose **Authenticate**: a browser tab opens, sign in to
uselawless.com and click **Allow**.

Restart the client (Codex desktop: quit with ⌘Q and reopen), then start a new conversation.

### Claude desktop (Cowork)

Two steps, about two minutes. Cowork loads a plugin's skill but does not open the plugin's own remote
connection, so the database is added once as a connector:

1. **Plugin (the skill).** Settings → **Plugins** → **Add** → **Add from a repository** → `Lawless-Inc/priorbit`,
   turn on *Sync automatically*, **Sync**, then make sure **priorbit** is enabled.
2. **Connector (the database).** Settings → **Connectors** → **Add** → **Add custom connector**:
   - Name: `Priorbit`
   - MCP server URL: `https://patdb-mcp-production.up.railway.app/mcp` (exactly this — Cowork pairs the
     connector with the plugin by URL)

   - Authentication: **Sign in now** → sign in with your uselawless.com account and click **Allow**, then **Add**.
3. Start a **new** Cowork task and ask, e.g. "Who owns the patents behind the SECURADOOR brand?" If the agent
   says it cannot find the tools, check that Priorbit is switched on in the task's connector menu.

### Other clients (Cursor, Claude.ai, Windsurf, …)

Add a remote MCP server with this URL; the client will ask you to sign in with your uselawless.com account:

```
https://patdb-mcp-production.up.railway.app/mcp
```

Then copy [SKILL.md](skills/priorbit/SKILL.md) into your client's rules or skills so the agent knows when to use it.

## Account and plans

Every call needs a signed-in uselawless.com account. **Go** is free: 200 credits a month (a status check is 1 credit, a search 2, a product page 5,
playbooks free; enough for status checks and a dozen knockout searches, while a full FTO screening needs Plus). Paid plans are one tenth of their standard rate
during the beta: **Plus** $5.90 for 20,000 credits, **Professional** $19.90 for 80,000. Details and billing terms:
https://uselawless.com/pricing . Personal API keys issued by Lawless keep working (`…/mcp?key=YOUR_KEY`).

## Try

> Do a US FTO screening for https://www.amazon.com/dp/B0GSYWD5RT

> Who owns the patents behind the SECURADOOR brand?

> Is US 10,435,928 still in force, when does it expire, and who owns it now?

> Knockout search for the mark VOLTREK in classes 9 and 12 — include marks that sound the same but are spelled differently.

Results are research leads for an attorney, not legal opinions.

## CLI and Python SDK

For scripts and pipelines (Codex, shell, notebooks): a thin package generated from the server's own tool list — NDJSON out, one line per result.

```bash
pip install "git+https://github.com/Lawless-Inc/priorbit#subdirectory=sdk/python"
priorbit login                                   # free account, once
priorbit search_patents --queries "door security bar" --patent_type design --k 10 | jq .pn
priorbit get_patents --patent_numbers 7532200,D949612 --raw
```

```python
from priorbit import Priorbit
p = Priorbit()
p.search_trademarks(text="WOBBLY LIFE", k=5)
```

Details: `sdk/python/README.md`.

## Contact

- Email: zhiyuanren@uselawless.com (English or Chinese) · https://uselawless.com/contact
- Support for signed-in users: the Account page at https://uselawless.com/account
- Security: https://uselawless.com/.well-known/security.txt
- MCP endpoint: `https://patdb-mcp-production.up.railway.app/mcp` · registry name `com.uselawless/priorbit` (see `server.json`)
- Agent setup document: https://uselawless.com/skill.md

## License

MIT
