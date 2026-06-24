"""
routing_engine.py
-----------------
High-level routing façade consumed by the Streamlit dashboard.

1. Maps incident (lat, lon) to nearest graph node
2. Filters hospitals by bed availability
3. Runs pathfinding to each hospital
4. Returns candidates ranked by travel time
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from src.algorithms.astar import AStarResult, astar
from src.algorithms.dijkstra import DijkstraResult, dijkstra, multi_source_dijkstra
from src.models.city_graph import CityGraph, Hospital


@dataclass
class RouteCandidate:
    hospital: Hospital
    path: List[str]
    travel_time_min: float
    distance_km: float
    nodes_explored: int
    algorithm: str
    congestion_on_path: float = 0.0

    @property
    def eta_label(self) -> str:
        mins = int(self.travel_time_min)
        secs = int((self.travel_time_min - mins) * 60)
        return f"{mins}m {secs:02d}s"


@dataclass
class RoutingResponse:
    incident_lat: float
    incident_lon: float
    incident_node: str
    candidates: List[RouteCandidate] = field(default_factory=list)
    algorithm_used: str = "Dijkstra"

    @property
    def best(self) -> Optional[RouteCandidate]:
        if not self.candidates:
            return None
        return self.candidates[0]

    def has_route(self) -> bool:
        return len(self.candidates) > 0


class RoutingEngine:
    def __init__(self, city_graph: CityGraph) -> None:
        self.city = city_graph

    def find_routes(
        self,
        incident_lat: float,
        incident_lon: float,
        algorithm: str = "A*",
        top_k: int = 3,
    ) -> RoutingResponse:
        source = self.city.nearest_node(incident_lat, incident_lon)
        response = RoutingResponse(
            incident_lat=incident_lat,
            incident_lon=incident_lon,
            incident_node=source,
            algorithm_used=algorithm,
        )

        available = self.city.available_hospitals()
        if not available:
            return response

        hospital_node_ids = [h.node_id for h in available]

        if algorithm == "Dijkstra":
            results = multi_source_dijkstra(self.city.graph, source, hospital_node_ids)
            candidates = []
            for hosp in available:
                r = results.get(hosp.node_id)
                if r and r.found:
                    candidates.append(RouteCandidate(
                        hospital=hosp,
                        path=r.path,
                        travel_time_min=r.cost,
                        distance_km=r.distance_km,
                        nodes_explored=r.nodes_explored,
                        algorithm="Dijkstra",
                        congestion_on_path=self._avg_congestion(r.path),
                    ))
        else:
            candidates = []
            for hosp in available:
                r = astar(self.city.graph, source, hosp.node_id)
                if r.found:
                    candidates.append(RouteCandidate(
                        hospital=hosp,
                        path=r.path,
                        travel_time_min=r.cost,
                        distance_km=r.distance_km,
                        nodes_explored=r.nodes_explored,
                        algorithm="A*",
                        congestion_on_path=self._avg_congestion(r.path),
                    ))

        candidates.sort(key=lambda c: c.travel_time_min)
        response.candidates = candidates[:top_k]
        return response

    def compare_algorithms(
        self,
        incident_lat: float,
        incident_lon: float,
        hospital_node_id: str,
    ) -> dict:
        source = self.city.nearest_node(incident_lat, incident_lon)
        d_result = dijkstra(self.city.graph, source, hospital_node_id)
        a_result = astar(self.city.graph, source, hospital_node_id)
        return {
            "dijkstra": {
                "path": d_result.path,
                "cost_min": d_result.cost,
                "distance_km": d_result.distance_km,
                "nodes_explored": d_result.nodes_explored,
            },
            "astar": {
                "path": a_result.path,
                "cost_min": a_result.cost,
                "distance_km": a_result.distance_km,
                "nodes_explored": a_result.nodes_explored,
            },
        }

    def _avg_congestion(self, path: List[str]) -> float:
        if len(path) < 2:
            return 0.0
        total, count = 0.0, 0
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if self.city.graph.has_edge(u, v):
                total += self.city.graph[u][v].get("congestion", 0.0)
                count += 1
        return round(total / count, 3) if count else 0.0
