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
        
        if "message" not in data:
            # 🚀 PHASE 4: AI PREDICTION ENGINE (SIMULATION) 🚀
            for feature in data.get("features", []):
                coords = feature.get("geometry", {}).get("coordinates", [])
                
                lon, lat = 0, 0
                # Check if location is Point or Polygon
                if feature["geometry"]["type"] == "Point":
                    lon, lat = coords[0], coords[1]
                elif feature["geometry"]["type"] == "Polygon":
                    lon, lat = coords[0][0][0], coords[0][0][1]

                # Predict Future Path (Moving North-West side automatically)
                # Note: Mapbox/Leaflet uses [Lat, Lon]
                future_path = [
                    [lat, lon],                # Aaj ki location
                    [lat + 1.2, lon - 1.5],    # Kal ki location
                    [lat + 2.5, lon - 2.8],    # Parso ki location
                    [lat + 4.0, lon - 4.2]     # 3 din baad ki location
                ]
                
                # AI Data add karna
                feature["properties"]["ai_future_path"] = future_path
                feature["properties"]["ai_risk_score"] = f"{random.randint(75, 98)}%"
                feature["properties"]["ai_eta"] = "48 Hours"
            
            cyclone_memory = data
            
        return {"status": "Success", "data": data}
    except Exception as e:
        return {"status": "Error", "message": str(e)}

@app.post("/api/chat")
def chat_with_ai(msg: Message):
    user_text = msg.text.lower()
    
    if "kitne" in user_text or "active" in user_text:
        count = len(cyclone_memory.get("features", []))
        return {"reply": f"Abhi current time mein {count} active cyclones hain. Map par check karein!"}
        
    # 🚀 JAB USER FUTURE YA NUKSAAN KE BARE MEIN PUCHE 🚀
    elif "nuksan" in user_text or "risk" in user_text or "kaha" in user_text or "time" in user_text or "predict" in user_text:
        features = cyclone_memory.get("features", [])
        if len(features) > 0:
            name = features[0]["properties"].get("name", "Unknown Cyclone")
            risk = features[0]["properties"].get("ai_risk_score", "80%")
            eta = features[0]["properties"].get("ai_eta", "48 Hours")
            
            reply = f"🚨 AI Prediction ke mutabiq: Sabse kareebi cyclone '{name}' hai. Iska Damage Risk Score <b>{risk}</b> hai! Yeh lagbhag <b>{eta}</b> baad zameen se takrayega. Maine map par iska rasta ek RED DOTTED LINE se bana diya hai!"
        else:
            reply = "Abhi koi cyclone nahi hai, toh risk 0% hai."
        return {"reply": reply}
        
    else:
        return {"reply": "Aap mujhse puch sakte hain: 'Kitna nuksan karega?' ya 'Ye kaha tak aayega aur kitna time lagega?'"}