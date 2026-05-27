from flask import Flask, request, jsonify, send_file
import os
from user_plot_trend_historic import run_analysis  # your script

app = Flask(__name__)

OUTPUT_FILE = "flood_report.png"


@app.route("/")
def home():
    return send_file("index.html")


@app.route("/run", methods=["POST"])
def run():

    data = request.json

    address = data.get("address")
    lat = data.get("lat")
    lon = data.get("lon")

    try:
        # Run your analysis
        run_analysis(address=address, lat=lat, lon=lon)

        # Save output as a fixed file name
        if os.path.exists("flood_susceptibility_report.png"):
            return jsonify({"status": "ok", "image": "/image"})

        else:
            return jsonify({"status": "error", "message": "No output generated"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

from flask import request, send_file
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform
import tempfile

RASTER_PATH = "https://datacube-prod-data-public.s3.ca-central-1.amazonaws.com/store/water/flood-susceptibility/fs-trends/fs-2000-2023-current.tif"


@app.route("/subset", methods=["POST"])
def subset():

    data = request.json
    lat = data["lat"]
    lon = data["lon"]

    # buffer distance (meters)
    buffer_m = 2000

    # convert lat/lon → EPSG:3979
    x, y = transform("EPSG:4326", "EPSG:3979", [lon], [lat])
    x = x[0]
    y = y[0]

    bounds = (
        x - buffer_m,
        y - buffer_m,
        x + buffer_m,
        y + buffer_m
    )

    with rasterio.open(RASTER_PATH) as src:

        window = from_bounds(*bounds, transform=src.transform)
        data = src.read(1, window=window)

        profile = src.profile
        profile.update({
            "height": data.shape[0],
            "width": data.shape[1],
            "transform": rasterio.windows.transform(window, src.transform)
        })

        tmp = tempfile.NamedTemporaryFile(suffix=".tif", delete=False)

        with rasterio.open(tmp.name, "w", **profile) as dst:
            dst.write(data, 1)

    return send_file(tmp.name, mimetype="image/tiff")


@app.route("/image")
def image():
    return send_file("flood_susceptibility_report.png", mimetype="image/png")


if __name__ == "__main__":
    app.run(debug=True)
