1. 
install miniconda, if you don't already have it

2. Open Miniconda, create env: 
conda create -n flood_sus_app python=3.11  OR conda create -n flood_app -c conda-forge python=3.11 
conda activate flood_sus_app 
pip install numpy matplotlib rasterio scipy flask requests scikit-learn




3. create env to reuse later: 
pip freeze > requirements.txt

run:
python app.py


in browser:
http://127.0.0.1:5000