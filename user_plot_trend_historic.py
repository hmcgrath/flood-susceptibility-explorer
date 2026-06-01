import matplotlib
matplotlib.use("Agg")

import numpy as np
from rasterio.warp import transform
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
import requests

import rasterio
from rasterio.session import AWSSession
import matplotlib.colors as mcolors
import textwrap

# ---------------------------
# USER SETTINGS
# ---------------------------

YEARS = list(range(2000, 2024))

RASTER_TEMPLATE = "https://datacube-prod-data-public.s3.ca-central-1.amazonaws.com/store/water/flood-susceptibility/fs-historic/fsm-{}-historic-mc.tif"
SLOPE_RASTER = "https://datacube-prod-data-public.s3.ca-central-1.amazonaws.com/store/water/flood-susceptibility/fs-trends/fs-2000-2023-slope.tif"
CURRENT_RASTER = "https://datacube-prod-data-public.s3.ca-central-1.amazonaws.com/store/water/flood-susceptibility/fs-trends/fs-2000-2023-current.tif"

# Trend thresholds
# ---------------------------
# CLASSIFICATION THRESHOLDS
# ---------------------------
#Strong shift  → slope > 5000 or < -5000  
#Weak shift    → slope between 2000–5000  
#No change     → -2000 to +2000  
X = 5000     # strong change
XA = 2000    # weak change

##Helper function

def clean_address(address):
    if not address:
        return ""

    parts = [p.strip() for p in address.split(",")]

    cleaned = []
    for p in parts:
        # remove country
        if p.lower() == "canada":
            continue

        # remove postal codes ONLY (better rule)
        if len(p) <= 10 and any(c.isdigit() for c in p) and any(c.isalpha() for c in p.upper()):
            # crude postal code check
            continue

        cleaned.append(p)

    return ", ".join(cleaned[:6])


# ---------------------------
# GEOCODING (Nominatim)
# ---------------------------

def geocode_address_cda(address):
    url = "https://geolocator.api.geo.ca/"
    params = {
        "q": address,
        "lang": "en"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    if not data:
        raise ValueError("No results found")

    result = data[0]

    return float(result["lat"]), float(result["lng"])
    
def geocode_address(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}

    try:
        response = requests.get(
            url,
            params=params,
            headers={"User-Agent": "flood-tool"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.SSLError:
        raise RuntimeError("SSL error: try installing pip-system-certs")

    if not data:
        raise ValueError("Address not found")

    return float(data[0]["lat"]), float(data[0]["lon"])

# ---------------------------
# COORDINATE TRANSFORM
# ---------------------------

def to_epsg3979(lat, lon):
    x, y = transform("EPSG:4326", "EPSG:3979", [lon], [lat])
    return x[0], y[0]


# ---------------------------
# SAMPLE RASTER VALUE
# ---------------------------

def sample_raster(url, x, y):
    try:
        with rasterio.open(url) as src:
            for val in src.sample([(x, y)]):
                v = val[0]

                if src.nodata is not None and v == src.nodata:
                    return np.nan

                return float(v)

    except Exception:
        return np.nan



# ---------------------------
# CLASSIFY SUSCEPTIBILITY
# ---------------------------

def classify_fs(val):
    if np.isnan(val):
        return "No data"
    elif val < 50:
        return "Low (flooding is unlikely)"
    elif val > 80:
        return "Moderate (flooding is possible)"
    else:
        return "High (flooding is more likely)"


# ---------------------------
# TREND ANALYSIS
# ---------------------------

import numpy as np

def compute_trend_from_slope(slope_value):

    # ---------------------------
    # CLEAN INPUT
    # ---------------------------
    if slope_value is None or np.isnan(slope_value):
        return np.nan, "No data", np.nan

    # ---------------------------
    # DECODE SLOPE
    # ---------------------------
    slope = slope_value - 10000  # center at zero


    # ---------------------------
    # CLASSIFICATION
    # ---------------------------

    # ✅ No change zone
    if -XA <= slope <= XA:
        label = "No clear change"

    # ✅ decreases
    elif slope < -X:
        label = "Clear decrease"
    elif slope < -XA:
        label = "Slight decrease"

    # ✅ increases
    elif slope <= X:
        label = "Slight increase"
    else:
        label = "Clear increase"

    return slope, label, np.nan


# ---------------------------
# MAIN WORKFLOW
# ---------------------------

def run_analysis(address=None, lat=None, lon=None, geocode=True):

    # ---------------------------
    # INPUT HANDLING
    # ---------------------------
    if address is None or address == "":
        address = f"{lat:.4f}, {lon:.4f}"

    location_str = address if address else f"Lat: {lat}, Lon: {lon}"
    
    if geocode == True and address is not None:
        print(f"Geocoding address: {address}")
    
        try:
            lat, lon = geocode_address(address)
        except Exception as e:
            print(f"Primary geocoder failed: {e}")
            lat, lon = geocode_address_cda(address)
    
    elif lat is not None and lon is not None:
        print(f"Using provided coordinates: lat={lat}, lon={lon}")
    
    else:
        raise ValueError("You must provide either an address or lat/lon coordinates")

    # ---------------------------
    # TRANSFORM TO EPSG:3979
    # ---------------------------

    x, y = to_epsg3979(lat, lon)

    values = []

    # ---------------------------
    # SAMPLE HISTORICAL RASTERS
    # ---------------------------

    print("Sampling historical rasters...")
    for year in YEARS:
        url = RASTER_TEMPLATE.format(year)
        val = sample_raster(url, x, y)
        values.append(val)

    # ---------------------------
    # CURRENT VALUE
    # ---------------------------

    current_val = sample_raster(CURRENT_RASTER, x, y)

    # ---------------------------
    # TREND
    # ---------------------------

    x, y = to_epsg3979(lat, lon)

    slope_val = sample_raster(SLOPE_RASTER, x, y)

    slope, trend_label, _ = compute_trend_from_slope(slope_val)

    current_label = classify_fs(current_val)

    
    # ---------------------------
    # SUMMARY
    # ---------------------------

    location_str = address if address else f"Lat: {lat}, Lon: {lon}"

    summary = f"""
Flood Susceptibility Report

Location: {location_str}

Current flood susceptibility: {current_label}
Value: {current_val:.1f} out of 100

Trend: {trend_label}

What this means:
- Low: flooding is unlikely
- Moderate: flooding is possible
- High: flooding is more likely

Trend describes how flood risk has changed since 2000.
"""

    print(summary)

    # ---------------------------
    # PLOT
    # ---------------------------

    
    plt.figure(figsize=(6, 4))

    values_array = np.array(values)

    # Normalize color scale FIXED from 0 to 100
    norm = mcolors.Normalize(vmin=0, vmax=100)

    # Colormap: yellow green blue
    cmap = plt.cm.YlGnBu

    # Scatter plot (points only)
    sc = plt.scatter(
        YEARS,
        values_array,
        c=values_array,
        cmap=cmap,
        norm=norm,
        s=75,
        edgecolor='none',         
        label="Historical values"
    )

    # Current value line
    if not np.isnan(current_val):
        plt.axhline(
            current_val,
            linestyle='--',
            linewidth=2,
            color='blue',
            label="Current value"
        )

    # Colorbar (important for interpretation)
    cbar = plt.colorbar(sc)
    cbar.set_label("Flood Susceptibility (0–100)")
    
    #set y limit fixed 0 to 100
    plt.ylim(0, 100)
    # Labels
    plt.xlabel("Year")
    plt.ylabel("Flood Susceptibility (0–100)")
    address = clean_address(address)
    
    wrapped_address = "\n".join(
        textwrap.wrap(address or "", width=40)
    )
    plt.title(f"Flood Susceptibility Over Time\n{wrapped_address}", fontsize=8, pad=10)


    #plt.legend()
    plt.legend(loc='upper left', bbox_to_anchor=(0.02, 0.75))

    # Text box (unchanged)
    text = f"""Current Class: {current_label}
    Present day value: {current_val:.1f}

    Trend: {trend_label}
    
    """

    plt.text(
        0.02, 0.98, text,
        fontsize=8,
        transform=plt.gca().transAxes,
        verticalalignment='top',
        bbox=dict(boxstyle="round", alpha=0.2)
    )

    plt.rcParams.update({
    "font.size": 6,
    "axes.titlesize": 6,
    "axes.labelsize": 6,
    "xtick.labelsize": 5,
    "ytick.labelsize": 5,
    "legend.fontsize": 6
    })

    plt.tight_layout()
    #plt.savefig("flood_susceptibility_report.png", dpi=300)
    plt.savefig("flood_susceptibility_report.png", dpi=300)
    #plt.show()


# ---------------------------
# RUN
# ---------------------------

if __name__ == "__main__":
    #address = input("Enter your address: ")
    #address = "580 Booth St, Ottawa, Ontario, Canada"
    
    run_analysis(
        address="255 2nd St, Dryden, ON P8N 2V5, Canada",
        lat='', 
        lon='',
        geocode = True
    )

####
