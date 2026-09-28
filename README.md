# Lawless Agent Skills

US patent search and freedom-to-operate (FTO) screening for physical products, for any AI agent.
Backed by the Lawless patent database MCP server: 12M+ US granted patents with full claims, CPC
classes, owners and in-force status. Results are candidates for a lawyer's review, not legal advice.

Read the skill: [SKILL.md](skills/lawless-patent/SKILL.md) ·
[raw](https://raw.githubusercontent.com/Lawless-Inc/skills/main/skills/lawless-patent/SKILL.md)

## Install

You need a Lawless API key (`lwp_…`). Ask Lawless for one.

### Claude Code

```bash
claude plugin marketplace add Lawless-Inc/skills
claude plugin install lawless-patent@lawless
```

You'll be asked for your API key; it is stored in your system's secure store. Invoke explicitly with `/lawless-patent:lawless-patent`.

### Other agents (Cursor, Codex, Windsurf, …)

```bash
npx skills add Lawless-Inc/skills --skill lawless-patent
```

Then add the MCP server to your client (the skill explains per-client config):
`https://patdb-mcp-production.up.railway.app/mcp` with header `Authorization: Bearer <your key>`.

## Copy this to your agent

> Install the Lawless patent search skill. If you're in Claude Code, run `claude plugin marketplace add Lawless-Inc/skills`, then `claude plugin install lawless-patent@lawless` and enter my Lawless API key when prompted. If you're in another agent, run `npx skills add Lawless-Inc/skills --skill lawless-patent`, then add the MCP server `https://patdb-mcp-production.up.railway.app/mcp` with header `Authorization: Bearer <my key>` as the skill describes. You can read the skill at https://raw.githubusercontent.com/Lawless-Inc/skills/main/skills/lawless-patent/SKILL.md. Then use it whenever I ask about patents or FTO for a product.

## Use

> Here's my product: a portable steel door security bar that braces under the doorknob. Which US patents should I worry about?

## License

MIT
