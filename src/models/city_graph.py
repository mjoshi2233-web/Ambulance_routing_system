"""
city_graph.py
-------------
Constructs and manages the weighted directed graph representing the city road network.

Nodes  → intersections / locations (hospitals, incident points, road junctions)
Edges  → road segments with: base_distance, speed_limit, current_congestion

Travel time for an edge:
    congestion_factor = max(0.1, 1.0 - congestion * 0.8)
    travel_time = (distance / (speed_limit * congestion_factor)) * 60  # minutes
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import networkx as nx


@dataclass
class Location:
    node_id: str
    name: str
    lat: float
    lon: float
    location_type: str
    is_available: bool = True

    def coords(self) -> Tuple[float, float]:
        return (self.lat, self.lon)


@dataclass
class Hospital:
    node_id: str
    name: str
    lat: float
    lon: float
    capacity: int
    available_beds: int
    trauma_level: int
    address: str = ""

    @property
    def is_available(self) -> bool:
        return self.available_beds > 0

    def occupancy_pct(self) -> float:
        if self.capacity == 0:
            return 100.0
        return round((1 - self.available_beds / self.capacity) * 100, 1)


class CityGraph:
    """Wraps a NetworkX DiGraph and exposes helpers for routing and congestion."""

    def __init__(self) -> None:
        self.graph: nx.DiGraph = nx.DiGraph()
        self.locations: Dict[str, Location] = {}
        self.hospitals: Dict[str, Hospital] = {}

    def add_location(self, loc: Location) -> None:
        self.locations[loc.node_id] = loc
        self.graph.add_node(
            loc.node_id,
            name=loc.name,
            lat=loc.lat,
            lon=loc.lon,
            location_type=loc.location_type,
        )

    def add_hospital(self, hosp: Hospital) -> None:
        self.hospitals[hosp.node_id] = hosp
        loc = Location(
            node_id=hosp.node_id,
            name=hosp.name,
            lat=hosp.lat,
            lon=hosp.lon,
            location_type="hospital",
            is_available=hosp.is_available,
        )
        self.add_location(loc)

    def add_road(
        self,
        from_id: str,
        to_id: str,
        distance_km: float,
        speed_limit_kmph: float = 50.0,
        bidirectional: bool = True,
        congestion: float = 0.0,
        road_name: str = "",
    ) -> None:
        weight = self._travel_time(distance_km, speed_limit_kmph, congestion)
        attrs = dict(
            distance=distance_km,
            speed_limit=speed_limit_kmph,
            congestion=congestion,
            weight=weight,
            road_name=road_name,
        )
        self.graph.add_edge(from_id, to_id, **attrs)
        if bidirectional:
            self.graph.add_edge(to_id, from_id, **attrs)

    @staticmethod
    def _travel_time(distance_km: float, speed_kmph: float, congestion: float) -> float:
        congestion_factor = max(0.1, 1.0 - congestion * 0.8)
        effective_speed = speed_kmph * congestion_factor
        return (distance_km / effective_speed) * 60.0

    def update_congestion(self, from_id: str, to_id: str, congestion: float) -> None:
        if not self.graph.has_edge(from_id, to_id):
            return
        congestion = max(0.0, min(1.0, congestion))
        edge = self.graph[from_id][to_id]
        edge["congestion"] = congestion
        edge["weight"] = self._travel_time(edge["distance"], edge["speed_limit"], congestion)
        if self.graph.has_edge(to_id, from_id):
            rev = self.graph[to_id][from_id]
            rev["congestion"] = congestion
            rev["weight"] = self._travel_time(rev["distance"], rev["speed_limit"], congestion)

    def simulate_traffic(self, seed: Optional[int] = None) -> None:
        rng = random.Random(seed)
        for u, v in self.graph.edges():
            c = rng.triangular(0.0, 0.85, 0.2)
            self.update_congestion(u, v, round(c, 2))

    @staticmethod
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
        return R * 2 * math.asin(math.sqrt(a))

    def nearest_node(self, lat: float, lon: float) -> Optional[str]:
        best_id, best_dist = None, float("inf")
        for nid, data in self.graph.nodes(data=True):
            d = self.haversine(lat, lon, data["lat"], data["lon"])
            if d < best_dist:
                best_dist = d
                best_id = nid
        return best_id

    def available_hospitals(self) -> List[Hospital]:
        return [h for h in self.hospitals.values() if h.is_available]

    def edge_count(self) -> int:
        return self.graph.number_of_edges()

    def node_count(self) -> int:
        return self.graph.number_of_nodes()

    def summary(self) -> str:
        return (
            f"CityGraph — {self.node_count()} nodes, {self.edge_count()} edges, "
            f"{len(self.hospitals)} hospitals"
                         )
