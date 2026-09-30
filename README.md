# Lawless Agent Skills

Lawless IPDB: an agent-native IP database for any AI agent. Covers US granted patents (full claims,
CPC, design USPC D classes, owners, maintenance status) and published US applications with official USPTO status.

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

> Install the Lawless IPDB skill. If you're in Claude Code, run `claude plugin marketplace add Lawless-Inc/skills`, then `claude plugin install lawless-patent@lawless` and enter my Lawless API key when prompted. If you're in another agent, run `npx skills add Lawless-Inc/skills --skill lawless-patent`, then add the MCP server `https://patdb-mcp-production.up.railway.app/mcp` with header `Authorization: Bearer <my key>` as the skill describes. You can read the skill at https://raw.githubusercontent.com/Lawless-Inc/skills/main/skills/lawless-patent/SKILL.md. Then use it whenever I ask to search or look up patents.

## Use

> Find US design patents for portable door security bars, and list any pending applications from the same owners.

## License

MIT
