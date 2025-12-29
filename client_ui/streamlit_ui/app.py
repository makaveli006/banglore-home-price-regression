import streamlit as st
import requests

st.set_page_config(page_title="Bangalore Home Price Predictor", page_icon="🏠", layout="centered")

# Change if your Flask runs on another host/port
FLASK_BASE_URL = "http://127.0.0.1:5000"

@st.cache_data
def fetch_locations():
    url = f"{FLASK_BASE_URL}/get_location_names"
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    data = r.json()
    return sorted(data.get("locations", []))

def predict_price_via_flask(location, sqft, bhk, bath):
    url = f"{FLASK_BASE_URL}/predict_home_price"
    payload = {
        "location": location,
        "total_sqft": float(sqft),
        "bhk": int(bhk),
        "bath": int(bath),
    }
    r = requests.post(url, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

st.title("🏠 Bangalore Home Price Predictor")
st.caption("This UI calls your Flask API. If Flask is OFF, this will fail.")

# ---- Flask health check ----
try:
    locations = fetch_locations()
    flask_ok = True
    st.success(f"✅ Flask is running: {FLASK_BASE_URL}")
except Exception as e:
    flask_ok = False
    locations = []
    st.error("❌ Flask server is not reachable.")
    st.code(str(e))

with st.form("prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        total_sqft = st.number_input("Total Sqft", min_value=100.0, max_value=20000.0, value=1000.0, step=10.0)
        bhk = st.number_input("BHK", min_value=1, max_value=7, value=2, step=1)

    with col2:
        bath = st.number_input("Bathrooms", min_value=1, max_value=7, value=2, step=1)
        location = st.selectbox("Location", options=locations if locations else ["(Flask OFF - no locations)"])

    submitted = st.form_submit_button("Predict Price", disabled=not flask_ok)

if submitted:
    try:
        result = predict_price_via_flask(location, total_sqft, bhk, bath)
        price = result.get("estimated_price")
        st.success(f"Estimated Price: **{price} Lakhs**")
        st.info(f"Inputs → Location: `{location}` | Sqft: `{total_sqft}` | BHK: `{bhk}` | Bath: `{bath}`")
    except Exception as e:
        st.error("Prediction failed (Flask call error).")
        st.code(str(e))
