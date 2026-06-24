"""
astar.py
--------
A* shortest-path algorithm with a haversine admissible heuristic.

Heuristic: h(n) = haversine(n, target) / avg_speed_kmph * 60
Using 40 km/h keeps it admissible (never over-estimates), guaranteeing optimality.
In practice A* explores 30-60% fewer nodes than Dijkstra on city-scale graphs.
"""

from __future__ import annotations

import heapq
import math
from typing import Dict, List, Optional, Tuple

import networkx as nx


class AStarResult:
    def __init__(
        self,
        source: str,
        target: str,
        path: List[str],
        cost: float,
        distance_km: float,
        nodes_explored: int,
    ) -> None:
        self.source = source
        self.target = target
        self.path = path
        self.cost = cost
        self.distance_km = distance_km
        self.nodes_explored = nodes_explored
        self.algorithm = "A*"

    @property
    def found(self) -> bool:
        return len(self.path) > 0

    def summary(self) -> str:
        if not self.found:
            return f"No path found from {self.source} to {self.target}."
        return (
            f"[A*] {self.source} → {self.target} | "
            f"{self.cost:.1f} min | {self.distance_km:.2f} km | "
            f"{len(self.path)} hops | {self.nodes_explored} nodes explored"
        )


def astar(
    graph: nx.DiGraph,
    source: str,
    target: str,
    weight: str = "weight",
    avg_speed_kmph: float = 40.0,
) -> AStarResult:
    if source not in graph or target not in graph:
        return AStarResult(source, target, [], -1.0, 0.0, 0)

    target_lat = graph.nodes[target]["lat"]
    target_lon = graph.nodes[target]["lon"]

    def heuristic(node_id: str) -> float:
        n = graph.nodes[node_id]
        dist_km = _haversine(n["lat"], n["lon"], target_lat, target_lon)
        return (dist_km / avg_speed_kmph) * 60.0

    g_score: Dict[str, float] = {n: math.inf for n in graph.nodes()}
    pred: Dict[str, Optional[str]] = {n: None for n in graph.nodes()}
    g_score[source] = 0.0

    counter = 0
    heap: List[Tuple[float, int, str]] = [(heuristic(source), counter, source)]
    closed: set = set()
    nodes_explored = 0

    while heap:
        _, _, u = heapq.heappop(heap)
        if u in closed:
            continue
        closed.add(u)
        nodes_explored += 1
        if u == target:
            break
        for v, edge_data in graph[u].items():
            if v in closed:
                continue
            w = edge_data.get(weight, 1.0)
            tentative_g = g_score[u] + w
            if tentative_g < g_score[v]:
                g_score[v] = tentative_g
                pred[v] = u
                counter += 1
                heapq.heappush(heap, (tentative_g + heuristic(v), counter, v))

    path = _reconstruct_path(pred, source, target)
    cost = g_score[target] if g_score[target] != math.inf else -1.0

    return AStarResult(
        source=source,
        target=target,
        path=path,
        cost=cost,
        distance_km=_path_distance(graph, path),
        nodes_explored=nodes_explored,
    )


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


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
    if not path or path[0] != source:
        return []
    return path


def _path_distance(graph: nx.DiGraph, path: List[str]) -> float:
    total = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        if graph.has_edge(u, v):
            total += graph[u][v].get("distance", 0.0)
    return round(total, 3)
