"""PNW Weather Tides: California stations for the STOFS-free Conditional sidecars (2026-11-15).

Coordinates and SHEF ids from CO-OPS mdapi. In-situ water temperature is used ONLY at the gauge itself and only
at the 12 stations with >= 60 days of CO-OPS water_temperature in the last 90 days (guide section 15.3). The other six
are satellite only. No neighbor sensor (CO-OPS or NDBC) is ever borrowed for a California station.
"""
CA = {
    "9414750": {"name": "Alameda, CA", "lat": 37.771954, "lon": -122.30026, "sound": True, "shef": "AAMC1"},
    "9416841": {"name": "Arena Cove, CA", "lat": 38.914555, "lon": -123.71108, "sound": False, "shef": "ANVC1"},
    "9419750": {"name": "Crescent City, CA", "lat": 41.74561, "lon": -124.18439, "sound": False, "shef": "CECC1"},
    "9410230": {"name": "La Jolla, CA", "lat": 32.86689, "lon": -117.25714, "sound": False, "shef": "LJAC1"},
    "9410678": {"name": "Long Beach Fire Boat Pier, CA", "lat": 33.7478, "lon": -118.2158, "sound": True, "shef": "LBFC1"},
    "9410660": {"name": "Los Angeles, CA", "lat": 33.72, "lon": -118.272, "sound": True, "shef": "OHBC1"},
    "9415102": {"name": "Martinez-Amorco Pier, CA", "lat": 38.0346, "lon": -122.1252, "sound": True, "shef": "MZXC1"},
    "9413450": {"name": "Monterey, CA", "lat": 36.60889, "lon": -121.89139, "sound": False, "shef": "MEYC1"},
    "9418767": {"name": "North Spit, CA", "lat": 40.766907, "lon": -124.21735, "sound": True, "shef": "HBYC1"},
    "9415020": {"name": "Point Reyes, CA", "lat": 37.994167, "lon": -122.97361, "sound": False, "shef": "PRYC1"},
    "9415144": {"name": "Port Chicago, CA", "lat": 38.056, "lon": -122.0395, "sound": True, "shef": "PCOC1"},
    "9412110": {"name": "Port San Luis, CA", "lat": 35.168888, "lon": -120.754166, "sound": False, "shef": "PSLC1"},
    "9414523": {"name": "Redwood City, CA", "lat": 37.506813, "lon": -122.21191, "sound": True, "shef": "RTYC1"},
    "9414863": {"name": "Richmond, CA", "lat": 37.9283, "lon": -122.4, "sound": True, "shef": "RCMC1"},
    "9410170": {"name": "San Diego, CA", "lat": 32.715557, "lon": -117.17667, "sound": True, "shef": "SDBC1"},
    "9414290": {"name": "San Francisco, CA", "lat": 37.806305, "lon": -122.46589, "sound": True, "shef": "FTPC1"},
    "9411340": {"name": "Santa Barbara, CA", "lat": 34.40459, "lon": -119.6925, "sound": False, "shef": "NTBC1"},
    "9410840": {"name": "Santa Monica, CA", "lat": 34.0083, "lon": -118.5, "sound": False, "shef": "ICAC1"},
}
CA_INSITU = ["9414750", "9416841", "9419750", "9410230", "9413450", "9418767", "9415020", "9415144", "9412110", "9414863", "9410170", "9410840"]
CA_SAT_ONLY = ["9414290", "9410660", "9410678", "9414523", "9411340", "9415102"]
assert not set(CA_INSITU) & set(CA_SAT_ONLY) and set(CA_INSITU) | set(CA_SAT_ONLY) == set(CA)
