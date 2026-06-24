"""
dijkstra.py
-----------
Dijkstra's single-source shortest-path algorithm on NetworkX DiGraph objects.

Provides both a point-to-point variant and a multi-source variant that
traverses the graph once to reach all hospital targets simultaneously.

Time complexity : O((V + E) log V)
Space complexity: O(V)
"""

from __future__ import annotations

import heapq
import math
from typing import Dict, List, Optional, Tuple

import networkx as nx


class DijkstraResult:
    def __init__(
        self,
        source: str,
        target: str,
        path: List[str],
        cost: float,
        distance_km: float,
        nodes_explored: int,
        predecessor: Dict[str, Optional[str]],
        dist: Dict[str, float],
    ) -> None:
        self.source = source
        self.target = target
        self.path = path
        self.cost = cost
        self.distance_km = distance_km
        self.nodes_explored = nodes_explored
        self.predecessor = predecessor
        self.dist = dist
        self.algorithm = "Dijkstra"

    @property
    def found(self) -> bool:
        return len(self.path) > 0

    def summary(self) -> str:
        if not self.found:
            return f"No path found from {self.source} to {self.target}."
        return (
            f"[Dijkstra] {self.source} → {self.target} | "
            f"{self.cost:.1f} min | {self.distance_km:.2f} km | "
            f"{len(self.path)} hops | {self.nodes_explored} nodes explored"
        )


def dijkstra(
    graph: nx.DiGraph,
    source: str,
    target: str,
    weight: str = "weight",
) -> DijkstraResult:
    dist: Dict[str, float] = {n: math.inf for n in graph.nodes()}
    pred: Dict[str, Optional[str]] = {n: None for n in graph.nodes()}
    dist[source] = 0.0

    heap: List[Tuple[float, str]] = [(0.0, source)]
    visited: set = set()
    nodes_explored = 0

    while heap:
        current_cost, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        nodes_explored += 1
        if u == target:
            break
        for v, edge_data in graph[u].items():
            w = edge_data.get(weight, 1.0)
            new_cost = current_cost + w
            if new_cost < dist[v]:
                dist[v] = new_cost
                pred[v] = u
                heapq.heappush(heap, (new_cost, v))

    path = _reconstruct_path(pred, source, target)
    total_distance = _path_distance(graph, path)

    return DijkstraResult(
        source=source,
        target=target,
        path=path,
        cost=dist[target] if dist[target] != math.inf else -1.0,
        distance_km=total_distance,
        nodes_explored=nodes_explored,
        predecessor=pred,
        dist=dist,
    )


def multi_source_dijkstra(
    graph: nx.DiGraph,
    source: str,
    targets: List[str],
    weight: str = "weight",
) -> Dict[str, DijkstraResult]:
    """Run Dijkstra once from source and extract results to every target."""
    if not targets:
        return {}

    dist: Dict[str, float] = {n: math.inf for n in graph.nodes()}
    pred: Dict[str, Optional[str]] = {n: None for n in graph.nodes()}
    dist[source] = 0.0

    heap: List[Tuple[float, str]] = [(0.0, source)]
    visited: set = set()
    nodes_explored = 0
    targets_remaining = set(targets)

    while heap and targets_remaining:
        current_cost, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        nodes_explored += 1
        targets_remaining.discard(u)
        for v, edge_data in graph[u].items():
            w = edge_data.get(weight, 1.0)
            new_cost = current_cost + w
            if new_cost < dist[v]:
                dist[v] = new_cost
                pred[v] = u
                heapq.heappush(heap, (new_cost, v))

    results: Dict[str, DijkstraResult] = {}
    for t in targets:
        path = _reconstruct_path(pred, source, t)
        results[t] = DijkstraResult(
            source=source,
            target=t,
            path=path,
            cost=dist[t] if dist[t] != math.inf else -1.0,
            distance_km=_path_distance(graph, path),
            nodes_explored=nodes_explored,
            predecessor=pred,
            dist=dist,
        )
    return results


def _reconstruct_path(
    pred: Dict[str, Optional[str]], source: str, target: str
) -> List[str]:
    if pred.get(target) is None and target != source:
        return []
    path = []
    node: Optional[str] = target
    while node is not None:
        path.append(node)
        node = pred[node]
    path.reverse()
    if path[0] != source:
        return []
    return path


def _path_distance(graph: nx.DiGraph, path: List[str]) -> float:
    total = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        if graph.has_edge(u, v):
            total += graph[u][v].get("distance", 0.0)
    return round(total, 3)
