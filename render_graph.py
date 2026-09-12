from pathlib import Path
from app.graph import graph

path = Path("GRAPH_SCHEMA.md")
path.write_text(f"# Схема графа\n\n```mermaid\n{graph.get_graph().draw_mermaid()}\n```\n", encoding="utf-8")