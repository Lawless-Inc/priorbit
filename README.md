# Priorbit — the IP database for your agent

> **Coming soon: Priorbit will require a free uselawless.com account.** Every plan is free during the beta.
> Create one now at https://uselawless.com/login?returnTo=%2Faccount&mode=signup . After the change your AI app asks
> you to sign in with it; in Cowork or claude.ai, set the Priorbit connector's Authentication to **Sign in now**.
> Personal API keys keep working.
>
> **即将变更：Priorbit 将需要一个免费的 uselawless.com 账号**，测试期间所有方案都免费。现在就可以在上面的链接注册；
> 切换后 AI 应用会请你用这个账号登录（Cowork / claude.ai 里把 Priorbit 连接器的 Authentication 改成 Sign in now）。个人 API 钥匙照常可用。

An IP database built for agents: US granted patents (full claims), published applications (official status),
US trademarks in every status, owners and inventors linked across both, live USPTO documents and drawing images,
prosecution file wrappers (office actions and responses as page images), PTAB trials, and e-commerce product pages. One plugin gives your agent the MCP tools **and** a skill that tells it to use them
for patent and trademark work — no API key needed to start.

Read the skill: [SKILL.md](skills/priorbit/SKILL.md)

## Install

### Codex

```bash
codex plugin marketplace add Lawless-Inc/priorbit
codex plugin add priorbit@lawless
```

### Claude Code

```bash
claude plugin marketplace add Lawless-Inc/priorbit
claude plugin install priorbit@lawless
```

Restart the client (Codex desktop: quit with ⌘Q and reopen), then start a new conversation.

### Claude desktop (Cowork)

Two steps, about two minutes, no key. Cowork loads a plugin's skill but does not open the plugin's own remote
connection, so the database is added once as a connector:

1. **Plugin (the skill).** Settings → **Plugins** → **Add** → **Add from a repository** → `Lawless-Inc/priorbit`,
   turn on *Sync automatically*, **Sync**, then make sure **priorbit** is enabled.
2. **Connector (the database).** Settings → **Connectors** → **Add** → **Add custom connector**:
   - Name: `Priorbit`
   - MCP server URL: `https://patdb-mcp-production.up.railway.app/mcp` (exactly this — Cowork pairs the
     connector with the plugin by URL)

   **Continue** — no sign-in.
3. Start a **new** Cowork task and ask, e.g. "Who owns the patents behind the SECURADOOR brand?" If the agent
   says it cannot find the tools, check that Priorbit is switched on in the task's connector menu.

### Other clients (Cursor, Claude.ai, Windsurf, …)

Add a remote MCP server with this URL — no key, no header:

```
https://patdb-mcp-production.up.railway.app/mcp
```

Then copy [SKILL.md](skills/priorbit/SKILL.md) into your client's rules or skills so the agent knows when to use it.

## Free use and keys

Without a key each network gets a daily free quota (about five full FTO screenings a day). A key raises the
limits (including product-page fetching, 10 a day per network without a key): use `https://patdb-mcp-production.up.railway.app/mcp?key=YOUR_KEY`.
Ask Lawless at https://uselawless.com.

## Try

> Do a US FTO screening for https://www.amazon.com/dp/B0GSYWD5RT

> Who owns the patents behind the SECURADOOR brand?

> Is US 10,435,928 still in force, when does it expire, and who owns it now?

> Knockout search for the mark VOLTREK in classes 9 and 12 — include marks that sound the same but are spelled differently.

Results are research leads for an attorney, not legal opinions.

## License

MIT
