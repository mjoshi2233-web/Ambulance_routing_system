"""
helpers.py
----------
Miscellaneous utilities: logging, formatting, graph validation.
"""

from __future__ import annotations
import logging
import sys
from typing import List
import networkx as nx


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "[%(asctime)s] %(levelname)-8s %(name)s – %(message)s",
            datefmt="%H:%M:%S"
        ))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def minutes_to_label(minutes: float) -> str:
    if minutes < 0:
        return "N/A"
    m = int(minutes)
    s = int((minutes - m) * 60)
    return f"{m}m {s:02d}s"


def congestion_label(value: float) -> str:
    if value < 0.25:
        return "🟢 Free flow"
    elif value < 0.55:
        return "🟡 Moderate"
    elif value < 0.80:
        return "🟠 Heavy"
    else:
        return "🔴 Severe"


def path_to_names(graph: nx.DiGraph, path: List[str]) -> List[str]:
    return [graph.nodes[n].get("name", n) for n in path if n in graph.nodes]


def format_path_description(graph: nx.DiGraph, path: List[str]) -> str:
    names = path_to_names(graph, path)
    if not names:
        return "No path"
    return " → ".join(names)


def validate_graph(graph: nx.DiGraph) -> List[str]:
    warnings = []
    if graph.number_of_nodes() == 0:
        warnings.append("Graph has no nodes.")
        return warnings
    if not nx.is_weakly_connected(graph):
        components = nx.number_weakly_connected_components(graph)
        warnings.append(
            f"Graph is not fully connected ({components} components). "
            f"Some routing queries may fail."
        )
    for u, v, data in graph.edges(data=True):
        w = data.get("weight", None)
        if w is None:
            warnings.append(f"Edge ({u}→{v}) missing 'weight' attribute.")
        elif w <= 0:
            warnings.append(f"Edge ({u}→{v}) has non-positive weight {w:.3f}.")
    return warnings
