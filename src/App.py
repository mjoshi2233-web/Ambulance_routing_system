"""
app.py
------
Streamlit dashboard — Smart Ambulance Routing & Emergency Response System.

Run with:  streamlit run app.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from streamlit_folium import st_folium

from data.sample_city import build_sample_city
from src.algorithms.routing_engine import RoutingEngine
from src.visualization.map_view import (
    build_base_map, add_incident_marker, add_route_overlay,
)
from src.utils.helpers import (
    minutes_to_label, congestion_label,
    format_path_description, validate_graph, get_logger,
)

logger = get_logger("app")

st.set_page_config(
    page_title="Smart Ambulance Routing System",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "city" not in st.session_state:
    st.session_state.city = build_sample_city(seed=42, simulate_traffic=True)
if "incident_lat" not in st.session_state:
    st.session_state.incident_lat = 30.3155
    st.session_state.incident_lon = 78.0330
if "routing_response" not in st.session_state:
    st.session_state.routing_response = None
if "comparison" not in st.session_state:
    st.session_state.comparison = None

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🚑 Emergency Routing")
    st.caption("Smart Ambulance Routing & Emergency Response System")
    st.divider()

    st.subheader("🚨 Incident Location")
    incident_lat = st.number_input("Latitude",  value=st.session_state.incident_lat, format="%.6f", step=0.001)
    incident_lon = st.number_input("Longitude", value=st.session_state.incident_lon, format="%.6f", step=0.001)
    st.caption("💡 Or click on the map to place the incident pin.")

    st.divider()
    st.subheader("⚙️ Settings")
    algorithm   = st.selectbox("Algorithm", ["A*", "Dijkstra"], index=0)
    top_k       = st.slider("Top hospitals", 1, 5, 3)
    show_network = st.toggle("Show road network", value=True)

    st.divider()
    st.subheader("🚦 Traffic Simulation")
    new_seed = st.number_input("Seed", 0, 9999, 42, step=1)
    if st.button("🔄 Refresh Traffic", use_container_width=True):
        st.session_state.city.simulate_traffic(seed=int(new_seed))
        st.session_state.routing_response = None
        st.session_state.comparison = None
        st.success("Traffic updated.")

    st.divider()
    city = st.session_state.city
    st.caption(f"**Network:** {city.node_count()} nodes · {city.edge_count()} edges · {len(city.hospitals)} hospitals")

    warnings = validate_graph(city.graph)
    for w in warnings:
        st.warning(w)

    dispatch = st.button("🚑  DISPATCH AMBULANCE", use_container_width=True, type="primary")

# ── Dispatch ───────────────────────────────────────────────────────────────
if dispatch:
    st.session_state.incident_lat = incident_lat
    st.session_state.incident_lon = incident_lon
    engine   = RoutingEngine(st.session_state.city)
    response = engine.find_routes(incident_lat, incident_lon, algorithm=algorithm, top_k=top_k)
    st.session_state.routing_response = response
    if response.best:
        st.session_state.comparison = engine.compare_algorithms(
            incident_lat, incident_lon, response.best.hospital.node_id
        )

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown(
    "<h1>🚑 Smart Ambulance Routing System</h1>"
    "<p style='color:#888'>Real-time emergency response · Dijkstra & A* · Dynamic traffic modelling</p>",
    unsafe_allow_html=True,
)
st.divider()

map_col, res_col = st.columns([3, 2], gap="large")

# ── Map ────────────────────────────────────────────────────────────────────
with map_col:
    st.subheader("🗺️ City Road Network")
    city     = st.session_state.city
    response = st.session_state.routing_response

    fmap = build_base_map(city, show_all_edges=show_network)
    add_incident_marker(fmap, st.session_state.incident_lat, st.session_state.incident_lon)

    colours = ["#2980b9", "#8e44ad", "#16a085"]
    if response and response.has_route():
        for i, cand in enumerate(response.candidates):
            add_route_overlay(fmap, city, cand, colour=colours[i % len(colours)],
                              label=f"Route {i+1} → {cand.hospital.name}")

    map_data = st_folium(fmap, width="100%", height=540, returned_objects=["last_clicked"])

    if map_data and map_data.get("last_clicked"):
        clicked = map_data["last_clicked"]
        st.session_state.incident_lat = round(clicked["lat"], 6)
        st.session_state.incident_lon = round(clicked["lng"], 6)
        st.info(f"📍 Pinned at ({st.session_state.incident_lat}, {st.session_state.incident_lon}). "
                f"Press **DISPATCH AMBULANCE**.")

    st.markdown(
        "<div style='font-size:0.78rem;margin-top:6px'>"
        "🟢 Free flow (&lt;25%) &nbsp; 🟡 Moderate (25–55%) &nbsp; "
        "🟠 Heavy (55–80%) &nbsp; 🔴 Severe (&gt;80%)</div>",
        unsafe_allow_html=True,
    )

# ── Results ────────────────────────────────────────────────────────────────
with res_col:
    if response is None:
        st.subheader("Results")
        st.info("Place an incident on the map or enter coordinates, then press **DISPATCH AMBULANCE**.")

        st.subheader("🏥 Hospital Availability")
        for hosp in sorted(city.hospitals.values(), key=lambda h: h.trauma_level):
            status = "✅" if hosp.is_available else "🔴"
            with st.expander(f"{status} {hosp.name}", expanded=False):
                c1, c2 = st.columns(2)
                c1.metric("Available Beds", hosp.available_beds)
                c2.metric("Occupancy", f"{hosp.occupancy_pct():.0f}%")
                st.caption(f"Trauma Level: {hosp.trauma_level} | Capacity: {hosp.capacity}")
                st.caption(f"📍 {hosp.address}")
    else:
        st.subheader(f"🏁 Results ({algorithm})")
        if not response.has_route():
            st.error("No route found. All hospitals may be unreachable or at capacity.")
        else:
            best = response.best
            st.success(f"**Best Route → {best.hospital.name}**")

            m1, m2, m3 = st.columns(3)
            m1.metric("⏱️ ETA",       best.eta_label)
            m2.metric("📏 Distance",  f"{best.distance_km:.2f} km")
            m3.metric("🔍 Nodes",     best.nodes_explored)

            m4, m5 = st.columns(2)
            m4.metric("🛏️ Avail Beds", best.hospital.available_beds)
            m5.metric("🚦 Congestion", f"{int(best.congestion_on_path * 100)}%")

            st.caption(f"Trauma Level: {best.hospital.trauma_level} | {best.hospital.address}")
            st.caption(congestion_label(best.congestion_on_path))

            with st.expander("📋 Route Breakdown", expanded=True):
                st.markdown(f"```\n{format_path_description(city.graph, best.path)}\n```")
                st.caption(f"{len(best.path)} waypoints")

            if len(response.candidates) > 1:
                st.divider()
                st.subheader("Other Hospitals")
                for i, cand in enumerate(response.candidates[1:], start=2):
                    with st.expander(f"#{i} — {cand.hospital.name} ({cand.eta_label})", expanded=False):
                        ca, cb, cc = st.columns(3)
                        ca.metric("ETA",      cand.eta_label)
                        cb.metric("Distance", f"{cand.distance_km:.2f} km")
                        cc.metric("Beds",     cand.hospital.available_beds)
                        st.caption(congestion_label(cand.congestion_on_path))

            comp = st.session_state.comparison
            if comp:
                st.divider()
                st.subheader("⚡ Algorithm Comparison")
                st.caption(f"Same route → {best.hospital.name}")
                d, a = comp["dijkstra"], comp["astar"]
                t1, t2 = st.columns(2)
                with t1:
                    st.markdown("**Dijkstra**")
                    st.metric("ETA",           minutes_to_label(d["cost_min"]))
                    st.metric("Distance",      f"{d['distance_km']:.2f} km")
                    st.metric("Nodes Explored", d["nodes_explored"])
                with t2:
                    st.markdown("**A\***")
                    st.metric("ETA",           minutes_to_label(a["cost_min"]))
                    st.metric("Distance",      f"{a['distance_km']:.2f} km")
                    st.metric("Nodes Explored", a["nodes_explored"])
                if d["nodes_explored"] > 0:
                    eff = (d["nodes_explored"] - a["nodes_explored"]) / d["nodes_explored"] * 100
                    if eff > 0:
                        st.success(f"A* explored {eff:.1f}% fewer nodes than Dijkstra.")
                    else:
                        st.info("Both algorithms performed similarly on this graph.")

st.divider()
st.markdown(
    "<p style='text-align:center;color:#888;font-size:0.8rem'>"
    "Smart Ambulance Routing System · Manish Joshi · "
    "Graph Theory + Dijkstra + A* + Real-time Traffic Modelling"
    "</p>",
    unsafe_allow_html=True,
)
