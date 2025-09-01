import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.tools import Tool, StructuredTool
from datetime import datetime
import googlemaps
import json


# Load API keys
load_dotenv()
gkey = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=gkey)

class RouteTrafficSchema(BaseModel):
    origin: str = Field(..., description="Starting location (address or place name)")
    destination: str = Field(..., description="Ending location (address or place name)")

"""
    Input: Takes an address or place name as string.
    Output: Returns lat/lng and formatted address in JSON format.
    Functionality: Uses Geocoding API from GCP to acquire lat/lng & formatted address.
"""
def geocode_location(address: str):

    results = gmaps.geocode(address)
    if not results:
        return {"ERROR": f"Location '{address}' not found."}
    loc = results[0]['geometry']['location']
    return {
        "lat": loc['lat'],
        "lng": loc['lng'],
        "formatted_address": results[0]['formatted_address']
    }


"""
    Input: Takes start (origin) and end (destination) location from user as strings.
    Output: Returns start/end addresses, normal duration, live duration, traffic color in JSON format.
    Functionality: Uses Directions API from GCP to get normal and live travel time for a route.
    
"""
def get_route_traffic(origin: str, destination: str):

    print(f"[DEBUG] RouteTraffic called with: origin={origin}, destination={destination}")
    time_now = datetime.now()
    # Use Directions API via gmaps.directions() to get live travel data
    directions = gmaps.directions(
        origin,
        destination,
        mode="driving",
        departure_time=time_now
    )

    if not directions:
        return {"ERROR": f"Route from '{origin}' to '{destination}' not found."}

    leg = directions[0]['legs'][0]
    duration = leg['duration']['text']
    duration_val = leg['duration']['value']
    duration_traffic = leg.get('duration_in_traffic', leg['duration'])
    duration_traffic_text = duration_traffic['text']
    duration_traffic_val = duration_traffic['value']

    # Calculate increase in travel duration to determine traffic levels
    increase = (duration_traffic_val - duration_val) / duration_val if duration_val > 0 else 0
    if increase < 0.1:
        color = "Blue"
    elif increase < 0.3:
        color = "Yellow"
    elif increase < 0.7:
        color = "Red"
    else:
        color = "Dark Red"

    return {
        "origin": leg['start_address'],
        "destination": leg['end_address'],
        "duration": duration,
        "duration_in_traffic": duration_traffic_text,
        "traffic_level": color,
        "percent_increase": f"{increase*100:.1f}%",
        "timestamp": datetime.now().isoformat()
    }


"""
    Input: Takes incoming traffic data from get_route_traffic() tool with location to store logs.
    Output: Stores input data as a JSON log at specified path.
    Functionality: Appends traffic check result to a local JSON log.
"""
def store_result(data: dict, filename: str = "data/traffic_log.json"):

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    try:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                existing = json.load(f)
        else:
            existing = []
        
        existing.append(data)
        with open(filename, "w") as f:
            json.dump(existing, f, indent=2)
        return {"success": True}

    except Exception as e:
        return {"error": str(e)}
    
tools = [
    Tool(name="GeocodeLocation",
         func=geocode_location,
         description="Uses Geocoding API from GCP to acquire lat/lng & formatted address."),
    StructuredTool.from_function(name="RouteTraffic",
         func=get_route_traffic,
         description="Uses Directions API from GCP to get normal and live travel time for a route i.e., traffic info.",
         args_schema=RouteTrafficSchema,),
    Tool(name="StoreResult",
         func=store_result,
         description="Appends traffic check result to a local JSON log."),
]