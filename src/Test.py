import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import networkx as nx
import pytest
from src.algorithms.dijkstra import dijkstra, multi_source_dijkstra

@pytest.fixture
def simple_graph():
    g = nx.DiGraph()
    for nid, lat, lon in [("A",0.0,0.0),("B",0.01,0.0),("C",0.02,0.0)]:
        g.add_node(nid, lat=lat, lon=lon, name=nid, location_type="junction")
    g.add_edge("A","B", weight=1.0, distance=1.0, speed_limit=60, congestion=0.0)
    g.add_edge("B","C", weight=2.0, distance=2.0, speed_limit=60, congestion=0.0)
    g.add_edge("A","C", weight=5.0, distance=5.0, speed_limit=60, congestion=0.0)
    return g

class TestDijkstra:
    def test_optimal_path(self, simple_graph):
        r = dijkstra(simple_graph, "A", "C")
        assert r.found and r.path == ["A","B","C"] and abs(r.cost-3.0)<1e-9

    def test_single_hop(self, simple_graph):
        r = dijkstra(simple_graph, "A", "B")
        assert r.found and r.path == ["A","B"]

    def test_source_equals_target(self, simple_graph):
        r = dijkstra(simple_graph, "A", "A")
        assert r.path == ["A"] and r.cost == 0.0

    def test_unreachable(self):
        g = nx.DiGraph()
        g.add_node("X", lat=0.0, lon=0.0, name="X", location_type="junction")
        g.add_node("Y", lat=1.0, lon=1.0, name="Y", location_type="junction")
        r = dijkstra(g, "X", "Y")
        assert not r.found and r.cost == -1.0

    def test_distance_calculated(self, simple_graph):
        r = dijkstra(simple_graph, "A", "C")
        assert abs(r.distance_km - 3.0) < 1e-6

class TestMultiSourceDijkstra:
    def test_returns_all_targets(self, simple_graph):
        results = multi_source_dijkstra(simple_graph, "A", ["B","C"])
        assert "B" in results and "C" in results

    def test_correct_costs(self, simple_graph):
        results = multi_source_dijkstra(simple_graph, "A", ["B","C"])
        assert abs(results["B"].cost-1.0)<1e-9 and abs(results["C"].cost-3.0)<1e-9

    def test_empty_targets(self, simple_graph):
        assert multi_source_dijkstra(simple_graph, "A", []) == {}
