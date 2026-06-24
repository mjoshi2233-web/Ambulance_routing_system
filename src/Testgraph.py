import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
from src.models.city_graph import CityGraph, Hospital, Location

@pytest.fixture
def tiny_city():
    city = CityGraph()
    city.add_hospital(Hospital("H1","City Hospital",10.0,20.0,100,50,1))
    city.add_hospital(Hospital("H2","District Hospital",10.1,20.1,80,0,2))
    city.add_location(Location("J1","Main Junction",10.05,20.05,"junction"))
    city.add_road("J1","H1",distance_km=1.0,speed_limit_kmph=50)
    city.add_road("J1","H2",distance_km=1.5,speed_limit_kmph=50)
    return city

class TestCityGraph:
    def test_node_count(self, tiny_city):
        assert tiny_city.node_count() == 3

    def test_edge_count_bidirectional(self, tiny_city):
        assert tiny_city.edge_count() == 4

    def test_available_hospitals(self, tiny_city):
        available = tiny_city.available_hospitals()
        assert len(available)==1 and available[0].node_id=="H1"

    def test_congestion_update(self, tiny_city):
        tiny_city.update_congestion("J1","H1",0.9)
        assert tiny_city.graph["J1"]["H1"]["congestion"] == 0.9

    def test_haversine_self(self):
        assert CityGraph.haversine(30.0,78.0,30.0,78.0) == pytest.approx(0.0,abs=1e-9)

    def test_nearest_node(self, tiny_city):
        assert tiny_city.nearest_node(10.001,20.001) == "H1"

    def test_simulate_traffic(self, tiny_city):
        old = {(u,v):d["weight"] for u,v,d in tiny_city.graph.edges(data=True)}
        tiny_city.simulate_traffic(seed=99)
        changed = any(abs(d["weight"]-old[(u,v)])>1e-6 for u,v,d in tiny_city.graph.edges(data=True))
        assert changed

class TestHospital:
    def test_occupancy(self):
        assert Hospital("H","T",0,0,100,40,1).occupancy_pct() == 60.0

    def test_not_available_when_full(self):
        assert not Hospital("H","T",0,0,100,0,2).is_available

    def test_available_with_beds(self):
        assert Hospital("H","T",0,0,100,1,2).is_available
