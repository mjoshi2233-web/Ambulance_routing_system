"""
sample_city.py
--------------
Builds a synthetic city graph modelled on Dehradun, Uttarakhand.
40 nodes, 8 hospitals, 110+ bidirectional road edges.
Coordinates are real Dehradun locations.
"""

from __future__ import annotations
import random
from src.models.city_graph import CityGraph, Hospital, Location


def build_sample_city(seed: int = 42, simulate_traffic: bool = True) -> CityGraph:
    city = CityGraph()

    hospital_data = [
        ("H1", "Doon Medical College & Hospital",       30.3240, 78.0410, 500, 85, 1, "Nehru Colony, Dehradun"),
        ("H2", "Synergy Institute of Medical Sciences", 30.2985, 78.0210, 300, 42, 2, "Ballupur Chowk, Dehradun"),
        ("H3", "Max Super Speciality Hospital",         30.3350, 78.0550, 400, 60, 1, "Mussoorie Diversion Rd"),
        ("H4", "Shri Mahant Indiresh Hospital",         30.3080, 78.0170, 600, 120, 1, "Patel Nagar, Dehradun"),
        ("H5", "Pacific Medical College",               30.2870, 78.0620, 200, 30, 2, "Sahastradhara Rd"),
        ("H6", "Himalayan Institute Hospital",          30.3610, 78.0740, 450, 75, 1, "Swami Ram Nagar, Dehradun"),
        ("H7", "Graphic Era Hospital",                  30.2770, 78.0280, 150, 20, 3, "Clement Town, Dehradun"),
        ("H8", "GRD Hospital",                         30.3190, 78.0490, 180, 12, 3, "Race Course, Dehradun"),
    ]
    for hid, name, lat, lon, cap, beds, trauma, addr in hospital_data:
        city.add_hospital(Hospital(hid, name, lat, lon, cap, beds, trauma, addr))

    junction_data = [
        ("J01", "Clock Tower",             30.3244, 78.0393),
        ("J02", "ISBT Dehradun",           30.2940, 78.0534),
        ("J03", "Rajpur Road Junction",    30.3350, 78.0430),
        ("J04", "Ballupur Chowk",          30.3002, 78.0199),
        ("J05", "Patel Nagar Chowk",       30.3090, 78.0200),
        ("J06", "Sahastradhara Chowk",     30.2882, 78.0630),
        ("J07", "Parade Ground",           30.3180, 78.0350),
        ("J08", "Survey Chowk",            30.3155, 78.0330),
        ("J09", "Connaught Place Ddn",     30.3210, 78.0370),
        ("J10", "Chakrata Road Jct",       30.3270, 78.0260),
        ("J11", "Mussoorie Road Jct",      30.3440, 78.0540),
        ("J12", "Selaqui Junction",        30.3520, 77.9980),
        ("J13", "Premnagar Chowk",         30.3380, 78.0190),
        ("J14", "Kaonli Chowk",            30.2850, 78.0390),
        ("J15", "Haridwar Road Jct",       30.2750, 78.0500),
        ("J16", "Clement Town Jct",        30.2790, 78.0290),
        ("J17", "Raipur Jct",              30.3110, 78.0680),
        ("J18", "GMS Road Jct",            30.3020, 78.0420),
        ("J19", "Turner Road Jct",         30.3300, 78.0350),
        ("J20", "Nathanpur Chowk",         30.3570, 78.0480),
        ("J21", "Doiwala Chowk",           30.2680, 78.1080),
        ("J22", "Rishikesh Road Jct",      30.3800, 78.0650),
        ("J23", "Jakhan Chowk",            30.3390, 78.0590),
        ("J24", "Vasant Vihar",            30.3050, 78.0470),
        ("J25", "EC Road Jct",             30.3200, 78.0455),
        ("J26", "Mothrowala Jct",          30.2950, 78.0145),
        ("J27", "Bhaniawala Jct",          30.2620, 77.9960),
        ("J28", "Rispana Bridge",          30.3130, 78.0220),
        ("J29", "Bindal Bridge",           30.3260, 78.0640),
        ("J30", "Pacific Hills Jct",       30.2875, 78.0700),
        ("J31", "Tapkeshwar Jct",          30.3460, 78.0215),
        ("J32", "FRI Gate",                30.3380, 78.0420),
        ("J33", "Araghar Chowk",           30.3070, 78.0580),
        ("J34", "Sewla Kalan",             30.3000, 77.9960),
        ("J35", "Kanwali Road Jct",        30.3080, 78.0510),
        ("J36", "Arcadia Grant",           30.3610, 78.0580),
        ("J37", "Defence Colony Jct",      30.3155, 78.0600),
        ("J38", "Tyagi Road Jct",          30.3240, 78.0480),
        ("J39", "Niranjanpur Jct",         30.2930, 78.0360),
        ("J40", "Rajeshwar Nagar",         30.2800, 78.0120),
    ]
    for jid, jname, jlat, jlon in junction_data:
        city.add_location(Location(jid, jname, jlat, jlon, "junction"))

    roads = [
        ("J01", "J09", 0.4, 40, "Clock Tower – Connaught Pl"),
        ("J09", "J07", 0.5, 40, "Connaught Pl – Parade Grd"),
        ("J07", "J08", 0.3, 35, "Parade Grd – Survey Chowk"),
        ("J08", "J10", 1.2, 50, "Survey Chowk – Chakrata Rd"),
        ("J01", "J03", 1.3, 50, "Clock Tower – Rajpur Rd"),
        ("J03", "J11", 1.1, 50, "Rajpur Rd – Mussoorie Jct"),
        ("J11", "J23", 0.9, 45, "Mussoorie Jct – Jakhan"),
        ("J23", "J29", 0.7, 45, "Jakhan – Bindal Bridge"),
        ("J03", "J32", 0.6, 40, "Rajpur Rd – FRI Gate"),
        ("J32", "J19", 0.5, 40, "FRI Gate – Turner Rd"),
        ("J19", "J13", 1.5, 50, "Turner Rd – Premnagar"),
        ("J13", "J10", 1.0, 45, "Premnagar – Chakrata Rd"),
        ("J10", "J31", 1.2, 45, "Chakrata Rd – Tapkeshwar"),
        ("J31", "J12", 4.0, 60, "Tapkeshwar – Selaqui"),
        ("J01", "H1", 0.8, 35, "Clock Tower – Doon MCH"),
        ("J09", "H1", 0.5, 35, "Connaught Pl – Doon MCH"),
        ("J04", "H2", 0.3, 30, "Ballupur – Synergy"),
        ("J11", "H3", 1.0, 40, "Mussoorie Jct – Max Hospital"),
        ("J23", "H3", 0.6, 40, "Jakhan – Max Hospital"),
        ("J05", "H4", 0.4, 35, "Patel Nagar – Indiresh"),
        ("J28", "H4", 0.5, 35, "Rispana Bridge – Indiresh"),
        ("J06", "H5", 0.5, 30, "Sahastradhara – Pacific"),
        ("J30", "H5", 0.4, 30, "Pacific Hills – Pacific Hosp"),
        ("J22", "H6", 1.5, 50, "Rishikesh Rd – Himalayan"),
        ("J36", "H6", 0.8, 40, "Arcadia – Himalayan"),
        ("J16", "H7", 0.5, 30, "Clement Town – Graphic Era"),
        ("J25", "H8", 0.4, 35, "EC Road – GRD Hospital"),
        ("J38", "H8", 0.5, 35, "Tyagi Rd – GRD Hospital"),
        ("J07", "J25", 0.9, 40, "Parade Grd – EC Road"),
        ("J25", "J38", 0.6, 40, "EC Road – Tyagi Rd"),
        ("J38", "J29", 0.8, 40, "Tyagi Rd – Bindal Bridge"),
        ("J25", "J33", 0.7, 35, "EC Road – Araghar"),
        ("J33", "J35", 0.5, 35, "Araghar – Kanwali"),
        ("J35", "J24", 0.6, 35, "Kanwali – Vasant Vihar"),
        ("J24", "J18", 0.5, 35, "Vasant Vihar – GMS Rd"),
        ("J18", "J39", 0.9, 40, "GMS Rd – Niranjanpur"),
        ("J39", "J14", 0.7, 35, "Niranjanpur – Kaonli"),
        ("J14", "J02", 0.8, 40, "Kaonli – ISBT"),
        ("J02", "J15", 1.8, 60, "ISBT – Haridwar Rd"),
        ("J15", "J27", 3.5, 60, "Haridwar Rd – Bhaniawala"),
        ("J14", "J16", 1.2, 40, "Kaonli – Clement Town"),
        ("J16", "J40", 1.4, 40, "Clement Town – Rajeshwar"),
        ("J40", "J26", 1.0, 40, "Rajeshwar – Mothrowala"),
        ("J26", "J34", 1.8, 50, "Mothrowala – Sewla Kalan"),
        ("J34", "J12", 3.0, 60, "Sewla Kalan – Selaqui"),
        ("J29", "J37", 0.6, 40, "Bindal Bridge – Defence Col"),
        ("J37", "J17", 0.8, 40, "Defence Col – Raipur"),
        ("J17", "J06", 1.5, 45, "Raipur – Sahastradhara"),
        ("J06", "J30", 0.6, 35, "Sahastradhara – Pacific Hills"),
        ("J20", "J36", 1.0, 45, "Nathanpur – Arcadia"),
        ("J36", "J22", 2.5, 60, "Arcadia – Rishikesh Rd"),
        ("J20", "J13", 1.5, 45, "Nathanpur – Premnagar"),
        ("J19", "J32", 0.5, 40, "Turner Rd – FRI Gate"),
        ("J32", "J03", 0.6, 40, "FRI Gate – Rajpur Rd"),
        ("J08", "J28", 0.8, 35, "Survey Chowk – Rispana Br"),
        ("J28", "J05", 0.6, 35, "Rispana Br – Patel Nagar"),
        ("J05", "J04", 0.5, 30, "Patel Nagar – Ballupur"),
        ("J04", "J26", 1.0, 40, "Ballupur – Mothrowala"),
        ("J18", "J24", 0.5, 35, "GMS Rd – Vasant Vihar"),
        ("J07", "J01", 0.6, 35, "Parade Grd – Clock Tower"),
        ("J09", "J38", 0.8, 40, "Connaught Pl – Tyagi Rd"),
        ("J09", "J25", 0.5, 40, "Connaught Pl – EC Road"),
        ("J01", "J08", 0.4, 35, "Clock Tower – Survey Chowk"),
        ("J21", "J15", 2.0, 60, "Doiwala – Haridwar Rd"),
        ("J21", "J02", 2.5, 60, "Doiwala – ISBT"),
        ("J29", "J23", 0.7, 40, "Bindal Br – Jakhan"),
        ("J11", "J20", 1.2, 50, "Mussoorie Jct – Nathanpur"),
        ("J31", "J10", 0.8, 40, "Tapkeshwar – Chakrata"),
        ("J13", "J31", 1.0, 45, "Premnagar – Tapkeshwar"),
        ("J39", "J18", 0.9, 40, "Niranjanpur – GMS Rd"),
        ("J35", "J37", 0.7, 40, "Kanwali – Defence Col"),
        ("J24", "J33", 0.6, 35, "Vasant Vihar – Araghar"),
        ("J17", "J33", 0.9, 35, "Raipur – Araghar"),
        ("J17", "J35", 0.8, 40, "Raipur – Kanwali"),
        ("J22", "J20", 1.8, 50, "Rishikesh Rd – Nathanpur"),
    ]
    for from_id, to_id, dist, speed, rname in roads:
        city.add_road(from_id, to_id, dist, speed, bidirectional=True, road_name=rname)

    if simulate_traffic:
        city.simulate_traffic(seed=seed)

    return city
