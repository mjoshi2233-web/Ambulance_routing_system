import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import networkx as nx
import pytest
from src.algorithms.astar import astar
from src.algorithms.dijkstra import dijkstra

@pytest.fixture
def simple_graph():
    g = nx.DiGraph()
    for nid, lat, lon in [("A",0.0,0.0),("B",0.01,0.0),("C",0.02,0.0)]:
        g.add_node(nid, lat=lat, lon=lon, name=nid, location_type="junction")
    g.add_edge("A","B", weight=1.0, distance=1.0, speed_limit=60, congestion=0.0)
    g.add_edge("B","C", weight=2.0, distance=2.0, speed_limit=60, congestion=0.0)
    g.add_edge("A","C", weight=5.0, distance=5.0, speed_limit=60, congestion=0.0)
    return g

@pytest.fixture
def grid_graph():
    g = nx.DiGraph()
    N = 4
    for r in range(N):
        for c in range(N):
            nid = f"R{r}C{c}"
            g.add_node(nid, lat=float(r)*0.01, lon=float(c)*0.01, name=nid, location_type="junction")
    for r in range(N):
        for c in range(N):
            nid = f"R{r}C{c}"
            if c+1<N:
                right=f"R{r}C{c+1}"
                g.add_edge(nid,right,weight=1.0,distance=1.0,speed_limit=60,congestion=0.0)
                g.add_edge(right,nid,weight=1.0,distance=1.0,speed_limit=60,congestion=0.0)
            if r+1<N:
                down=f"R{r+1}C{c}"
                g.add_edge(nid,down,weight=1.0,distance=1.0,speed_limit=60,congestion=0.0)
                g.add_edge(down,nid,weight=1.0,distance=1.0,speed_limit=60,congestion=0.0)
    return g

class TestAStar:
    def test_cost_matches_dijkstra(self, simple_graph):
        d = dijkstra(simple_graph,"A","C")
        a = astar(simple_graph,"A","C")
        assert a.found and abs(a.cost-d.cost)<1e-6

    def test_path_matches_dijkstra(self, simple_graph):
        assert astar(simple_graph,"A","C").path == dijkstra(simple_graph,"A","C").path

    def test_source_equals_target(self, simple_graph):
        a = astar(simple_graph,"A","A")
        assert a.path==["A"] and a.cost==0.0

    def test_unreachable(self):
        g = nx.DiGraph()
        g.add_node("X",lat=0.0,lon=0.0,name="X",location_type="junction")
        g.add_node("Y",lat=1.0,lon=1.0,name="Y",location_type="junction")
        assert not astar(g,"X","Y").found

    def test_grid_path_length(self, grid_graph):
        a = astar(grid_graph,"R0C0","R3C3")
        assert a.found and len(a.path)==7

    def test_fewer_nodes_than_dijkstra(self, grid_graph):
        d = dijkstra(grid_graph,"R0C0","R3C3")
        a = astar(grid_graph,"R0C0","R3C3")
        assert a.nodes_explored <= d.nodes_explored

    def test_algorithm_label(self, simple_graph):
        assert astar(simple_graph,"A","C").algorithm == "A*"
