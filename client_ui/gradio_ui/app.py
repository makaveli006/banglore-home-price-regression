import gradio as gr
import requests

# Change if your Flask runs on another host/port
FLASK_BASE_URL = "http://127.0.0.1:5000"


def fetch_locations():
    """Fetch locations from Flask. If Flask is down, return empty list."""
    try:
        r = requests.get(f"{FLASK_BASE_URL}/get_location_names", timeout=5)
        r.raise_for_status()
        data = r.json()
        return sorted(data.get("locations", []))
    except Exception:
        return []


def flask_status_text():
    """Human-friendly status."""
    try:
        r = requests.get(f"{FLASK_BASE_URL}/get_location_names", timeout=5)
        r.raise_for_status()
        return f"✅ Flask is running: {FLASK_BASE_URL}"
    except Exception as e:
        return f"❌ Flask server is not reachable.\n\n{e}"


def predict_price(location, total_sqft, bhk, bath):
    """Call Flask /predict_home_price endpoint."""
    payload = {
        "location": location,
        "total_sqft": float(total_sqft),
        "bhk": int(bhk),
        "bath": int(bath),
    }

    r = requests.post(f"{FLASK_BASE_URL}/predict_home_price", json=payload, timeout=10)
    r.raise_for_status()
    data = r.json()

    price = data.get("estimated_price", None)
    if price is None:
        return "Prediction failed: No 'estimated_price' in response."

    return f"Estimated Price: {price} Lakhs\nInputs → Location: {location} | Sqft: {total_sqft} | BHK: {bhk} | Bath: {bath}"


def refresh_locations():
    """Reload dropdown choices and status text."""
    locs = fetch_locations()
    status = flask_status_text()

    # If no locations, show placeholder
    if not locs:
        locs = ["(Flask OFF - no locations)"]

    return gr.Dropdown(choices=locs, value=locs[0]), status


# Initial load
_initial_locations = fetch_locations()
if not _initial_locations:
    _initial_locations = ["(Flask OFF - no locations)"]

with gr.Blocks(title="Bangalore Home Price Predictor") as demo:
    gr.Markdown("# 🏠 Bangalore Home Price Predictor")
    gr.Markdown("This UI calls your **Flask API**. If Flask is OFF, prediction will fail.")

    status_box = gr.Textbox(
        label="Flask Status",
        value=flask_status_text(),
        interactive=False,
        lines=3
    )

    with gr.Row():
        location_dd = gr.Dropdown(
            label="Location",
            choices=_initial_locations,
            value=_initial_locations[0]
        )

    with gr.Row():
        total_sqft_in = gr.Number(label="Total Sqft", value=1000, minimum=100, maximum=20000, precision=0)
        bhk_in = gr.Slider(label="BHK", minimum=1, maximum=7, step=1, value=2)
        bath_in = gr.Slider(label="Bathrooms", minimum=1, maximum=7, step=1, value=2)

    with gr.Row():
        predict_btn = gr.Button("Predict Price", variant="primary")
        refresh_btn = gr.Button("🔄 Refresh Locations")

    output = gr.Textbox(label="Result", lines=3, interactive=False)

    predict_btn.click(
        fn=predict_price,
        inputs=[location_dd, total_sqft_in, bhk_in, bath_in],
        outputs=[output]
    )

    refresh_btn.click(
        fn=refresh_locations,
        inputs=[],
        outputs=[location_dd, status_box]
    )

if __name__ == "__main__":
    # Start Gradio on localhost
    demo.launch(server_name="127.0.0.1", server_port=7860)
