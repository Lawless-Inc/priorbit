# priorbit — CLI + Python SDK for the Priorbit IP database

Priorbit is the IP database built for agents: US granted patents (full claims), published applications, trademarks in every status, owners and inventors linked, live USPTO records. This package is a thin layer over its MCP server — no server logic here, every command is generated from the server's own tool list, so it is always in sync.

```bash
pip install priorbit
priorbit login                                   # free uselawless.com account, opens a browser once
priorbit tools                                   # what the server offers, with argument names
priorbit search_patents --queries "door security bar" --patent_type design --k 10
priorbit get_patents --patent_numbers 7532200,D949612
priorbit search_trademarks --text "WOBBLY LIFE" --k 5 | jq -r '.serial? // empty'
priorbit call resolve_owner --json '{"name":"SharkNinja"}' --pretty
```

Output is NDJSON: one line per result, then a final `{"meta": …}` line with coverage, filters, task_id and notes. `--raw` prints the whole JSON. Exit codes: 2 not signed in, 3 server unreachable, 4 tool error.

Auth: `--key` / `PRIORBIT_API_KEY`, else the stored sign-in from `priorbit login` (`~/.config/priorbit/credentials.json`, refreshed automatically; `priorbit logout` forgets it).

```python
from priorbit import Priorbit
p = Priorbit()                                   # same auth order as the CLI
hits = p.search_patents(queries=["door security bar"], patent_type="design", k=10)
p.get_patents(patent_numbers=[h["pn"] for h in hits["results"]])
p.task_id                                        # set from the first call; passed on every later call
```

Results are research leads with sources and as-of dates, not legal opinions. Docs: https://uselawless.com/docs
