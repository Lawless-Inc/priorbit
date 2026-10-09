"""Priorbit — the IP database for agents (US patents, applications, trademarks over MCP).

    from priorbit import Priorbit
    p = Priorbit()                      # PRIORBIT_API_KEY, or `priorbit login` once (OAuth, free account)
    p.search_patents(queries=["door security bar"], patent_type="design", k=10)
    p.tools()                           # every tool with its input schema, straight from the server
"""
from .client import Priorbit, PriorbitError, DEFAULT_URL   # noqa: F401

__version__ = "0.1.0"
