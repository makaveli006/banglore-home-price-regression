import json
import dill
import numpy as np

__data_columns = None
__locations = None
__model = None


def load_saved_artifacts():
    """
    Load:
      • columns.json   → column order + locations
      • trained model  → banglore_home_prices_model.dill
    """
    global __data_columns, __locations, __model

    print("\nloading saved artifacts...start")

    # --- load column metadata ---
    with open("./artifacts/columns.json", "r") as f:
        __data_columns = json.load(f)["data_columns"]

    # first 3 columns are: sqft, bath, bhk
    __locations = __data_columns[3:]

    # --- load trained model (pickled using dill) ---
    with open("./artifacts/banglore_home_prices_model.dill", "rb") as f:
        __model = dill.load(f)

    print("loading saved artifacts...done\n")


def get_location_names():
    return __locations


def get_data_columns():
    return __data_columns


def get_estimated_price(location, sqft, bhk, bath):
    """
    Builds feature vector in SAME order as training dataframe
    Unknown locations are treated as baseline (all-zero location vector)
    """

    if __model is None or __data_columns is None:
        raise Exception("Model or columns not loaded. Call load_saved_artifacts() first.")

    x = np.zeros(len(__data_columns))

    # numeric features
    x[0] = sqft
    x[1] = bath
    x[2] = bhk

    # locations in columns.json are lowercase
    location = location.lower().strip()

    # safe location index lookup
    if location in __data_columns:
        loc_index = __data_columns.index(location)
        x[loc_index] = 1
    else:
        # unknown location → leave all zeros for location fields
        # same behavior as notebook predict_price()
        pass

    price = __model.predict([x])[0]
    return round(price, 2)


if __name__ == "__main__":
    load_saved_artifacts()

    print("Locations loaded =", len(get_location_names()))
    print(get_location_names()[:10])  # sample

    print(get_estimated_price("1st Phase JP Nagar", 1000, 3, 3))
    print(get_estimated_price("Not Present TEST", 1000, 2, 2))
