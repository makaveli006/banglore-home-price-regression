# server/util.py
import json
import dill
import numpy as np
from pathlib import Path

__data_columns = None
__locations = None
__model = None

# ✅ Always resolve artifacts relative to this util.py file
_ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"

def load_saved_artifacts():
    """
    Load:
      • columns.json   → column order + locations
      • trained model  → banglore_home_prices_model.dill
    """
    global __data_columns, __locations, __model

    print("\nloading saved artifacts...start")

    with open(_ARTIFACTS_DIR / "columns.json", "r") as f:
        __data_columns = json.load(f)["data_columns"]

    __locations = __data_columns[3:]

    with open(_ARTIFACTS_DIR / "banglore_home_prices_model.dill", "rb") as f:
        __model = dill.load(f)

    print("loading saved artifacts...done\n")


def get_location_names():
    return __locations


def get_data_columns():
    return __data_columns


def get_estimated_price(location, sqft, bhk, bath):
    if __model is None or __data_columns is None:
        raise Exception("Model or columns not loaded. Call load_saved_artifacts() first.")

    x = np.zeros(len(__data_columns))
    x[0] = sqft
    x[1] = bath
    x[2] = bhk

    location = location.lower().strip()

    if location in __data_columns:
        loc_index = __data_columns.index(location)
        x[loc_index] = 1

    price = __model.predict([x])[0]
    return round(price, 2)


if __name__ == "__main__":
    load_saved_artifacts()
    print("Locations loaded =", len(get_location_names()))
    print(get_location_names()[:10])
    print(get_estimated_price("1st Phase JP Nagar", 1000, 3, 3))
    print(get_estimated_price("Not Present TEST", 1000, 2, 2))
