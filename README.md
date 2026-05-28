
***

# 🌊 Flood Susceptibility Explorer

An interactive web-based tool for exploring flood susceptibility across Canada.

This application combines **time-series analysis, trend interpretation, and dynamic geospatial visualization** to help users understand how flood risk has changed at a specific location over time.

***

## 🚀 Features

* 🗺️ **Interactive Map**
  * Click anywhere on the map to analyze a location
  * Automatically reverse geocode to a readable address

* 🔍 **Address Search with Autocomplete**
  * Start typing to get real address suggestions
  * Restricted to Canadian locations

* 📈 **Flood Susceptibility Analysis**
  * Extracts annual flood susceptibility values (2000–2023)
  * Displays historical values as coloured points (0–100 scale)
  * Shows current flood susceptibility

* 📊 **Trend Interpretation**
  * Detects:
    * No clear change
    * Increase / decrease
    * Higher or lower in recent years
  * Uses a combination of:
    * slope
    * variability
    * level change detection

* 🧭 **Dynamic Raster Overlay**
  * Toggle map layer showing flood susceptibility surface
  * Uses a **custom subset API** to load only a small region (fast!)
  * Adjustable transparency

* 🖼️ **Export**
  * Download the generated plot as a PNG

***

## 🧠 How It Works

### 1. User input

* Map click OR address search

### 2. Backend processing

* Extract raster values (2000–2023)
* Compute trend
* Generate plot
* *** The rules and class results are prelimnary and can be modified by users. 

### 3. Dynamic raster subset

* Instead of loading the full dataset (\~233 MB),
* A small subset is extracted on demand via Flask

### 4. Visualization

* Plot displayed in browser
* Raster overlay rendered using `georaster-layer-for-leaflet`

***

## 🧱 Tech Stack

**Frontend**

* Leaflet.js (map)
* Georaster + GeoTIFF.js
* Vanilla JavaScript (no framework)

**Backend**

* Flask
* Rasterio
* NumPy / SciPy
* Matplotlib

**Data**

* Cloud Optimized GeoTIFFs (COGs)
* Flood Susceptibility dataset (2000–2023)

***

## ⚙️ Installation

### 1. Create environment

```bash
conda create -n flood_app -c conda-forge python=3.11
conda activate flood_app
```

***

### 2. Install dependencies

```bash
pip install flask numpy matplotlib rasterio scipy requests scikit-learn
```

***

### 3. Run the app

```bash
python app.py
```

***

### 4. Open in browser

```
http://127.0.0.1:5000
```

***

## 🗂️ Project Structure

```
flood-susceptibility-explorer/
│
├── app.py                         # Flask backend
├── user_plot_trend_historic.py    # Analysis + plotting logic
├── index.html                     # Frontend UI
├── static/                        # (optional assets)
├── templates/                     # (if using Flask templating)
└── README.md
```

***

## 🧪 API Endpoints

### `/run`

Runs full analysis and generates plot

```json
POST /run
{
  "lat": 45.45,
  "lon": -75.51,
  "address": "Ottawa, ON"
}
```

***

### `/subset`

Returns a small raster subset around location

```json
POST /subset
{
  "lat": 45.45,
  "lon": -75.51
}
```

***

## 🎛️ Controls

* ✅ Map click: select location
* ✅ Address input: search
* ✅ Toggle raster: show flood surface
* ✅ Slider: adjust transparency
* ✅ Clear button: reset

***

## 🧩 Key Design Decisions

* **Dynamic subset API**
  * Avoids loading full 200+ MB raster
  * Dramatically improves performance

* **Client-side rendering**
  * Uses georaster for flexibility
  * Enables custom styling (matches plot)

* **Simplified trend messaging**
  * Designed to be understandable (Grade 8–9 level)
  * Avoids exposing raw statistical metrics

***

## ⚠️ Limitations

* Raster rendering uses client-side processing  
  → performance may vary on large view extents

* CRS mismatch (EPSG:3979 vs Web Mercator)  
  → minor alignment differences possible

* Trend classification is heuristic-based  
  → designed for interpretability over strict statistical inference

***

## 🔮 Future Improvements

* ✅ Tile-based raster serving (Terracotta / TiTiler)
* ✅ Hover → show pixel value
* ✅ Legend synchronized with raster
* ✅ PDF report export
* ✅ Authentication / deployment (cloud)

***

## 📄 License

This project is licensed under the MIT License — see the LICENSE file for details.

***

## 🙌 Acknowledgements

* OpenStreetMap / Nominatim (geocoding)
* Rasterio & GDAL ecosystem
* Leaflet.js community

***

## 📬 Contact

Heather McGrath

***

# ⭐ Summary

This project demonstrates how to combine:

* geospatial data pipelines
* statistical interpretation
* interactive web mapping

into a **usable decision-support tool**.

***
