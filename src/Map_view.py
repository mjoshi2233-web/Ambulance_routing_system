"""
map_view.py
-----------
Folium map rendering for the Streamlit dashboard.
Produces interactive Leaflet maps with congestion-coloured road network,
hospital markers, incident pin, and route overlays.
"""

from __future__ import annotations
from typing import List, Optional

import folium

from src.models.city_graph import CityGraph, Hospital
from src.algorithms.routing_engine import RouteCandidate


def _congestion_colour(congestion: float) -> str:
    if congestion < 0.25:
        return "#2ecc71"
    elif congestion < 0.55:
        return "#f39c12"
    elif congestion < 0.80:
        return "#e67e22"
    else:
        return "#e74c3c"


def _trauma_badge(level: int) -> str:
    labels = {1: "Level I – Trauma Centre", 2: "Level II", 3: "Level III"}
    return labels.get(level, "Unknown")


def build_base_map(city: CityGraph, show_all_edges: bool = True) -> folium.Map:
    lats = [d["lat"] for _, d in city.graph.nodes(data=True)]
    lons = [d["lon"] for _, d in city.graph.nodes(data=True)]
    centre = (sum(lats) / len(lats), sum(lons) / len(lons))

    fmap = folium.Map(location=centre, zoom_start=13, tiles="CartoDB positron", prefer_canvas=True)

    if show_all_edges:
        drawn: set = set()
        for u, v, data in city.graph.edges(data=True):
            edge_key = tuple(sorted([u, v]))
            if edge_key in drawn:
                continue
            drawn.add(edge_key)
            u_data = city.graph.nodes[u]
            v_data = city.graph.nodes[v]
            cong = data.get("congestion", 0.0)
            tooltip = (
                f"{data.get('road_name', 'Road')}<br>"
                f"Distance: {data.get('distance', 0):.1f} km | "
                f"Speed: {data.get('speed_limit', 50)} km/h<br>"
                f"Congestion: {int(cong * 100)}%"
            )
            folium.PolyLine(
                locations=[(u_data["lat"], u_data["lon"]), (v_data["lat"], v_data["lon"])],
                color=_congestion_colour(cong),
                weight=2,
                opacity=0.6,
                tooltip=tooltip,
            ).add_to(fmap)

    for nid, data in city.graph.nodes(data=True):
        if data.get("location_type") == "junction":
            folium.CircleMarker(
                location=(data["lat"], data["lon"]),
                radius=3,
                color="#95a5a6",
                fill=True,
                fill_color="#95a5a6",
                fill_opacity=0.7,
                tooltip=data.get("name", nid),
            ).add_to(fmap)

    for hosp in city.hospitals.values():
        icon = folium.Icon(
            color="green" if hosp.is_available else "red",
            icon="plus-sign",
            prefix="glyphicon",
        )
        popup_html = (
            f"<b>{hosp.name}</b><br>"
            f"{hosp.address}<br><br>"
            f"<b>Trauma:</b> {_trauma_badge(hosp.trauma_level)}<br>"
            f"<b>Capacity:</b> {hosp.capacity} beds<br>"
            f"<b>Available:</b> {hosp.available_beds} beds "
            f"({100 - hosp.occupancy_pct():.0f}% free)<br>"
            f"<b>Status:</b> {'✅ Available' if hosp.is_available else '🔴 Full'}"
        )
        folium.Marker(
            location=(hosp.lat, hosp.lon),
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=hosp.name,
            icon=icon,
        ).add_to(fmap)

    return fmap


def add_incident_marker(fmap: folium.Map, lat: float, lon: float) -> None:
    folium.Marker(
        location=(lat, lon),
        popup="<b>🚨 Incident Location</b>",
        tooltip="Incident",
        icon=folium.Icon(color="red", icon="fire", prefix="glyphicon"),
    ).add_to(fmap)
    folium.CircleMarker(
        location=(lat, lon),
        radius=18,
        color="#e74c3c",
        fill=False,
        weight=2,
        opacity=0.5,
    ).add_to(fmap)


def add_route_overlay(
    fmap: folium.Map,
    city: CityGraph,
    candidate: RouteCandidate,
    colour: str = "#2980b9",
    label: str = "Route",
) -> None:
    coords = []
    for nid in candidate.path:
        if nid in city.graph.nodes:
            d = city.graph.nodes[nid]
            coords.append((d["lat"], d["lon"]))
    if len(coords) < 2:
        return
    folium.PolyLine(
        locations=coords,
        color=colour,
        weight=6,
        opacity=0.85,
        tooltip=(
            f"{label}<br>"
            f"ETA: {candidate.eta_label}<br>"
            f"Distance: {candidate.distance_km:.2f} km<br>"
            f"Avg Congestion: {int(candidate.congestion_on_path * 100)}%"
        ),
    ).add_to(fmap)
    src = city.graph.nodes[candidate.path[0]]
    folium.Marker(
        location=(src["lat"], src["lon"]),
        tooltip="🚑 Ambulance dispatched from here",
        icon=folium.Icon(color="blue", icon="ambulance", prefix="fa"),
    ).add_to(fmap)
