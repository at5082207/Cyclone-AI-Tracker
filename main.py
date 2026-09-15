from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import random

app = FastAPI()

class Message(BaseModel):
    text: str

cyclone_memory = {}

@app.get("/")
def show_map():
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/api/data")
def get_data():
    global cyclone_memory
    url = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/MAP?eventtype=TC"
    
    try:
        response = requests.get(url)
        data = response.json()
        features = data.get("features", [])
    except Exception:
        data = {"type": "FeatureCollection", "features": []}
        features = []

    # Dummy Cyclones (India ke paas)
    dummy_cyclones = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [88.5, 15.2]},
            "properties": {
                "name": "Cyclone Vayu (Simulated)",
                "alertlevel": "Red",
                "severitydata": {"severitytext": "Severe Cyclonic Storm"}
            }
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [69.2, 18.5]},
            "properties": {
                "name": "Cyclone Agni (Simulated)",
                "alertlevel": "Orange",
                "severitydata": {"severitytext": "Cyclonic Storm"}
            }
        }
    ]
    features.extend(dummy_cyclones)

    # Naya Data Add karna (Wind, Pressure, Exact Location)
    for feature in features:
        coords = feature.get("geometry", {}).get("coordinates", [])
        lon, lat = 0, 0
        if feature["geometry"]["type"] == "Point":
            lon, lat = coords[0], coords[1]
        elif feature["geometry"]["type"] == "Polygon":
            lon, lat = coords[0][0][0], coords[0][0][1]

        future_path = [
            [lat, lon], [lat + 1.5, lon - 1.0], [lat + 3.0, lon - 1.8], [lat + 4.5, lon - 2.5]
        ]
        
        feature["properties"]["ai_lat"] = lat
        feature["properties"]["ai_lon"] = lon
        feature["properties"]["ai_future_path"] = future_path
        feature["properties"]["ai_risk_score"] = f"{random.randint(85, 99)}%"
        feature["properties"]["ai_eta"] = f"{random.randint(24, 48)} Hours"
        
        # New Tech Features: Wind & Pressure
        feature["properties"]["ai_wind"] = f"{random.randint(90, 220)} km/h"
        feature["properties"]["ai_pressure"] = f"{random.randint(940, 1005)} hPa"

    data["features"] = features
    cyclone_memory = data
    return {"status": "Success", "data": data}

@app.post("/api/chat")
def chat_with_ai(msg: Message):
    user_text = msg.text.lower()
    features = cyclone_memory.get("features", [])
    
    if "kitne" in user_text or "active" in user_text:
        return {"reply": f"SYSTEM ALERT: Currently {len(features)} active storm signatures detected on radar."}
    elif "nuksan" in user_text or "risk" in user_text or "kaha" in user_text:
        if len(features) > 0:
            name = features[-1]["properties"].get("name", "Unknown")
            risk = features[-1]["properties"].get("ai_risk_score", "90%")
            return {"reply": f"HIGH THREAT: '{name}' detected. Damage Risk: {risk}. Please check the map for red trajectory."}
        return {"reply": "Radar clear. No active threats."}
    else:
        return {"reply": "AI Core Active. Ask me about threat levels or active cyclones."}
