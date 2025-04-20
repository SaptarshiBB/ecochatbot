from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
import logging
from datetime import datetime
import json
import os
import uuid

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configure Gemini API key (replace with your actual key)
genai.configure(api_key="enter your api key")

# Initialize the Gemini 1.5 model
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Chat session storage (consider using a database for production)
chat_sessions = {
    "default": {
        "created_at": datetime.now().isoformat(),
        "title": "Community Clean-Up Help",
        "messages": [
            {
                "sender": "bot",
                "message": "Hello! I'm here to help with community clean-up initiatives. Ask me about:\n- Recycling programs ♻️\n- Volunteer opportunities 👥\n- Waste reduction strategies 🗑️\n- Clean-up event planning 📅",
                "timestamp": datetime.now().isoformat()
            }
        ],
        "is_topic_validated": False
    }
}

# Load or initialize chats JSON file
CHATS_FILE = "chats.json"
if os.path.exists(CHATS_FILE):
    try:
        with open(CHATS_FILE, 'r') as f:
            chats = json.load(f)
    except json.JSONDecodeError:
        logging.error("Corrupted chats.json file, initializing empty chats")
        chats = []
else:
    chats = []
    with open(CHATS_FILE, 'w') as f:
        json.dump(chats, f, indent=2)
# Allowed topics
ALLOWED_TOPICS = {
    # Core Cleanup Terms (50+)
    "clean","cleanup", "clean-up", "community cleanup", "neighborhood cleanup", "beach cleanup", 
    "river cleanup", "park cleanup", "street cleaning", "highway cleanup", "lake cleanup",
    "forest cleanup", "underwater cleanup", "mountain cleanup", "desert cleanup", 
    "urban cleanup", "rural cleanup", "school cleanup", "playground cleanup",
    "shoreline cleanup", "wetland cleanup", "trail cleanup", "vacant lot cleanup",
    "litter picking", "plogging", "trash collection", "debris removal", "waste pickup",
    "illegal dumping cleanup", "hazardous waste removal", "post-storm cleanup",
    "post-event cleanup", "neighborhood beautification", "graffiti removal",
    "public space maintenance", "adopt-a-road", "adopt-a-park", "adopt-a-spot",
    "community stewardship", "litter patrol", "trash tag", "clean sweep",
    "spruce up", "tidy up", "spring cleaning", "deep clean", "sanitation drive",
    "environmental sanitation", "neighborhood revitalization", "blight removal",
    "brownfield restoration", "ecosystem restoration", "habitat cleanup",
 "clean-up", "community cleanup", "neighborhood cleanup", "beach cleanup",
"river cleanup", "park cleanup", "street cleanup", "highway cleanup", "lake cleanup",
"forest cleanup", "underwater cleanup", "mountain cleanup", "desert cleanup",
"urban cleanup", "rural cleanup", "school cleanup", "playground cleanup",
"shoreline cleanup", "wetland cleanup", "trail cleanup", "vacant lot cleanup",
"litter picking", "plogging", "trash collection", "debris removal", "waste pickup",
"illegal dumping cleanup", "hazardous waste removal", "post-storm cleanup",
"post-event cleanup", "neighborhood beautification", "graffiti removal",
"public space maintenance", "adopt-a-road", "adopt-a-park", "adopt-a-spot",
"community stewardship", "litter patrol", "trash tag", "clean sweep",
"spruce up", "tidy up", "spring cleaning", "deep clean", "sanitation drive",
"environmental sanitation", "neighborhood revitalization", "blight removal",
"brownfield restoration", "ecosystem restoration", "habitat cleanup",
"coastal cleanup", "creek cleanup", "canal cleanup", "estuary cleanup",
"watershed cleanup", "drain cleanup", "gutter cleanup", "alley cleanup",
"lot cleanup", "industrial cleanup", "construction cleanup", "post-fire cleanup",
"flood debris cleanup", "hurricane cleanup", "tornado debris cleanup",
"earthquake debris removal", "tsunami cleanup", "volunteer cleanup",
"corporate cleanup", "youth cleanup", "scout cleanup", "schoolyard cleanup",
"campus cleanup", "parking lot cleanup", "market cleanup", "festival cleanup",
"stadium cleanup", "concert cleanup", "event cleanup", "marina cleanup",
"harbor cleanup", "pier cleanup", "bridge cleanup", "railroad cleanup",
"trailhead cleanup", "campground cleanup", "picnic area cleanup",
"dog park cleanup", "skatepark cleanup", "play area cleanup", "pool cleanup",
"fountain cleanup", "statue cleanup", "monument cleanup", "cemetery cleanup",
"historic site cleanup", "archaeological site cleanup", "battlefield cleanup",
"nature reserve cleanup", "wildlife refuge cleanup", "bird sanctuary cleanup",
"wetland restoration", "dune restoration", "marsh cleanup", "swamp cleanup",
"bog cleanup", "fen cleanup", "spring cleanup", "well cleanup", "cistern cleanup",
"reservoir cleanup", "aquifer cleanup", "watershed restoration",
"riparian zone cleanup", "floodplain cleanup", "levee cleanup", "dam cleanup",
"locks cleanup", "canal bank cleanup", "irrigation ditch cleanup",
"farm cleanup", "orchard cleanup", "vineyard cleanup", "ranch cleanup",
"pasture cleanup", "stable cleanup", "barn cleanup", "greenhouse cleanup",
"garden cleanup", "allotment cleanup", "community garden cleanup",
"urban farm cleanup", "rooftop garden cleanup", "vertical garden cleanup",
"hydroponic farm cleanup", "aquaponic system cleanup", "compost site cleanup",
"recycling center cleanup", "transfer station cleanup", "landfill cleanup",
"dump site cleanup", "incinerator cleanup", "waste facility cleanup",
"hazardous waste site cleanup", "superfund site cleanup", "brownfield cleanup",
"industrial site cleanup", "factory cleanup", "mill cleanup", "plant cleanup",
"refinery cleanup", "shipyard cleanup", "dockyard cleanup", "rail yard cleanup",
"junkyard cleanup", "scrapyard cleanup", "auto yard cleanup", "salvage yard cleanup",
"recycling yard cleanup", "compost yard cleanup", "mulch yard cleanup",
"wood yard cleanup", "lumber yard cleanup", "construction yard cleanup",
"storage yard cleanup", "parking yard cleanup", "depot cleanup", "terminal cleanup",
"port cleanup", "airport cleanup", "train station cleanup", "bus station cleanup",
"transit center cleanup", "subway cleanup", "metro cleanup", "light rail cleanup",
"tram cleanup", "trolley cleanup", "cable car cleanup", "funicular cleanup",
"gondola cleanup", "ski lift cleanup", "chairlift cleanup", "aerial tram cleanup",
"zip line cleanup", "ropeway cleanup", "people mover cleanup", "monorail cleanup",
"maglev cleanup", "bullet train cleanup", "high-speed rail cleanup",
"commuter rail cleanup", "freight rail cleanup", "heritage rail cleanup",
"streetcar cleanup", "interurban cleanup", "trolleybus cleanup", "bus cleanup",
"coach cleanup", "minibus cleanup", "shuttle cleanup", "taxi cleanup",
"limousine cleanup", "rickshaw cleanup", "cycle rickshaw cleanup",
"pedicab cleanup", "horse-drawn carriage cleanup", "dog sled cleanup",
"snowmobile cleanup", "ATV cleanup", "UTV cleanup", "dirt bike cleanup",
"motorcycle cleanup", "scooter cleanup", "moped cleanup", "electric bike cleanup",
"hoverboard cleanup", "segway cleanup", "electric scooter cleanup",
"electric skateboard cleanup", "electric unicycle cleanup", "electric wheelchair cleanup",
"mobility scooter cleanup", "golf cart cleanup", "utility vehicle cleanup",
"forklift cleanup", "tractor cleanup", "backhoe cleanup", "bulldozer cleanup",
"excavator cleanup", "crane cleanup", "loader cleanup", "grader cleanup",
"roller cleanup", "paver cleanup", "compactor cleanup", "dump truck cleanup",
"concrete mixer cleanup", "cement truck cleanup", "tanker cleanup",
"flatbed cleanup", "box truck cleanup", "refrigerated truck cleanup",
"tow truck cleanup", "wrecker cleanup", "fire truck cleanup", "ambulance cleanup",
"police car cleanup", "squad car cleanup", "patrol car cleanup", "cruiser cleanup",
"undercover car cleanup", "detective car cleanup", "swat vehicle cleanup",
"armored vehicle cleanup", "tank cleanup", "military vehicle cleanup",
"humvee cleanup", "jeep cleanup", "armored personnel carrier cleanup",
"mine-resistant vehicle cleanup", "riot control vehicle cleanup",
"prison transport cleanup", "paddy wagon cleanup", "hearse cleanup",
"limo cleanup", "party bus cleanup", "tour bus cleanup", "double decker cleanup",
"articulated bus cleanup", "trolleybus cleanup", "trackless tram cleanup",
"guided bus cleanup", "bus rapid transit cleanup", "light rail cleanup",
"streetcar cleanup", "cable car cleanup", "funicular cleanup", "gondola cleanup",
"aerial tram cleanup", "chairlift cleanup", "ski lift cleanup", "ropeway cleanup",
"zip line cleanup", "people mover cleanup", "monorail cleanup", "maglev cleanup",
"bullet train cleanup", "high-speed rail cleanup", "commuter rail cleanup",
"freight rail cleanup", "heritage rail cleanup", "streetcar cleanup",
"interurban cleanup", "trolleybus cleanup", "bus cleanup", "coach cleanup",
"minibus cleanup", "shuttle cleanup", "taxi cleanup", "limousine cleanup",
"rickshaw cleanup", "cycle rickshaw cleanup", "pedicab cleanup",
"horse-drawn carriage cleanup", "dog sled cleanup", "snowmobile cleanup",
"ATV cleanup", "UTV cleanup", "dirt bike cleanup", "motorcycle cleanup",
"scooter cleanup", "moped cleanup", "electric bike cleanup", "hoverboard cleanup",
"segway cleanup", "electric scooter cleanup", "electric skateboard cleanup",
"electric unicycle cleanup", "electric wheelchair cleanup", "mobility scooter cleanup",
"golf cart cleanup", "utility vehicle cleanup", "forklift cleanup", "tractor cleanup",
"backhoe cleanup", "bulldozer cleanup", "excavator cleanup", "crane cleanup",
"loader cleanup", "grader cleanup", "roller cleanup", "paver cleanup",
"compactor cleanup", "dump truck cleanup", "concrete mixer cleanup",
"cement truck cleanup", "tanker cleanup", "flatbed cleanup", "box truck cleanup",
"refrigerated truck cleanup", "tow truck cleanup", "wrecker cleanup",
"fire truck cleanup", "ambulance cleanup", "police car cleanup",
"squad car cleanup", "patrol car cleanup", "cruiser cleanup",
"undercover car cleanup", "detective car cleanup", "swat vehicle cleanup",
"armored vehicle cleanup", "tank cleanup", "military vehicle cleanup",
"humvee cleanup", "jeep cleanup", "armored personnel carrier cleanup",
"mine-resistant vehicle cleanup", "riot control vehicle cleanup",
"prison transport cleanup", "paddy wagon cleanup", "hearse cleanup",
"limo cleanup", "party bus cleanup", "tour bus cleanup", "double decker cleanup",
"articulated bus cleanup", "trolleybus cleanup", "trackless tram cleanup",
"guided bus cleanup", "bus rapid transit cleanup", "light rail cleanup",
"streetcar cleanup", "cable car cleanup", "funicular cleanup", "gondola cleanup",
"aerial tram cleanup", "chairlift cleanup", "ski lift cleanup", "ropeway cleanup",
"zip line cleanup", "people mover cleanup", "monorail cleanup", "maglev cleanup",
"bullet train cleanup", "high-speed rail cleanup", "commuter rail cleanup",
"freight rail cleanup", "heritage rail cleanup", "streetcar cleanup",
"interurban cleanup", "trolleybus cleanup", "bus cleanup", "coach cleanup",
"minibus cleanup", "shuttle cleanup", "taxi cleanup", "limousine cleanup",
"rickshaw cleanup", "cycle rickshaw cleanup", "pedicab cleanup",
"horse-drawn carriage cleanup", "dog sled cleanup", "snowmobile cleanup",
"ATV cleanup", "UTV cleanup", "dirt bike cleanup", "motorcycle cleanup",
"scooter cleanup", "moped cleanup", "electric bike cleanup", "hoverboard cleanup",
"segway cleanup", "electric scooter cleanup", "electric skateboard cleanup",
"electric unicycle cleanup", "electric wheelchair cleanup", "mobility scooter cleanup",
"golf cart cleanup", "utility vehicle cleanup", "forklift cleanup", "tractor cleanup",
"backhoe cleanup", "bulldozer cleanup", "excavator cleanup", "crane cleanup",
"loader cleanup", "grader cleanup", "roller cleanup", "paver cleanup",
"compactor cleanup", "dump truck cleanup", "concrete mixer cleanup",
"cement truck cleanup", "tanker cleanup", "flatbed cleanup", "box truck cleanup",
"refrigerated truck cleanup", "tow truck cleanup", "wrecker cleanup",
"fire truck cleanup", "ambulance cleanup", "police car cleanup",
"squad car cleanup", "patrol car cleanup", "cruiser cleanup",
"undercover car cleanup", "detective car cleanup", "swat vehicle cleanup",
"armored vehicle cleanup", "tank cleanup", "military vehicle cleanup",
"humvee cleanup", "jeep cleanup", "armored personnel carrier cleanup",
"mine-resistant vehicle cleanup", "riot control vehicle cleanup",
"prison transport cleanup", "paddy wagon cleanup", "hearse cleanup",
"limo cleanup", "party bus cleanup", "tour bus cleanup", "double decker cleanup",
"articulated bus cleanup", "trolleybus cleanup", "trackless tram cleanup",
"guided bus cleanup", "bus rapid transit cleanup", "light rail cleanup",
"streetcar cleanup", "cable car cleanup", "funicular cleanup", "gondola cleanup",
"aerial tram cleanup", "chairlift cleanup", "ski lift cleanup", "ropeway cleanup",
"zip line cleanup", "people mover cleanup", "monorail cleanup", "maglev cleanup",
"bullet train cleanup", "high-speed rail cleanup", "commuter rail cleanup",
"freight rail cleanup", "heritage rail cleanup", "streetcar cleanup",
"interurban cleanup", "trolleybus cleanup", "bus cleanup", "coach cleanup",
"minibus cleanup", "shuttle cleanup", "taxi cleanup", "limousine cleanup",
"rickshaw cleanup", "cycle rickshaw cleanup", "pedicab cleanup",
"horse-drawn carriage cleanup", "dog sled cleanup", "snowmobile cleanup",
"ATV cleanup", "UTV cleanup", "dirt bike cleanup", "motorcycle cleanup",
"scooter cleanup", "moped cleanup", "electric bike cleanup", "hoverboard cleanup",
"segway cleanup", "electric scooter cleanup", "electric skateboard cleanup",
"electric unicycle cleanup", "electric wheelchair cleanup", "mobility scooter cleanup",
"golf cart cleanup", "utility vehicle cleanup", "forklift cleanup", "tractor cleanup",
"backhoe cleanup", "bulldozer cleanup", "excavator cleanup", "crane cleanup",
"loader cleanup", "grader cleanup", "roller cleanup", "paver cleanup",
"compactor cleanup", "dump truck cleanup", "concrete mixer cleanup",
"cement truck cleanup", "tanker cleanup", "flatbed cleanup", "box truck cleanup",
"refrigerated truck cleanup", "tow truck cleanup", "wrecker cleanup",
"fire truck cleanup", "ambulance cleanup", "police car cleanup",
"squad car cleanup", "patrol car cleanup", "cruiser cleanup",
"undercover car cleanup", "detective car cleanup", "swat vehicle cleanup",
"armored vehicle cleanup", "tank cleanup", "military vehicle cleanup",
"humvee cleanup", "jeep cleanup", "armored personnel carrier cleanup",
"mine-resistant vehicle cleanup", "riot control vehicle cleanup",
"prison transport cleanup", "paddy wagon cleanup", "hearse cleanup",
"limo cleanup", "party bus cleanup", "tour bus cleanup", "double decker cleanup",
"articulated bus cleanup", "trolleybus cleanup", "trackless tram cleanup",
"guided bus cleanup", "bus rapid transit cleanup", "light rail cleanup",
"streetcar cleanup", "cable car cleanup", "funicular cleanup", "gondola cleanup",
"aerial tram cleanup", "chairlift cleanup", "ski lift cleanup", "ropeway cleanup",
"zip line cleanup", "people mover cleanup", "monorail cleanup", "maglev cleanup",
"bullet train cleanup", "high-speed rail cleanup", "commuter rail cleanup",
"freight rail cleanup", "heritage rail cleanup", "streetcar cleanup",
"interurban cleanup", "trolleybus cleanup", "bus cleanup", "coach cleanup",
"minibus cleanup", "shuttle cleanup", "taxi cleanup", "limousine cleanup",
"rickshaw cleanup", "cycle rickshaw cleanup", "pedicab cleanup",
"horse-drawn carriage cleanup", "dog sled cleanup", "snowmobile cleanup",
"ATV cleanup", "UTV cleanup", "dirt bike cleanup", "motorcycle cleanup",
"scooter cleanup", "moped cleanup", "electric bike cleanup", "hoverboard cleanup",
"segway cleanup", "electric scooter cleanup", "electric skateboard cleanup",
"electric unicycle cleanup", "electric wheelchair cleanup", "mobility scooter cleanup",
"golf cart cleanup", "utility vehicle cleanup", "forklift cleanup", "tractor cleanup",
"backhoe cleanup", "bulldozer cleanup", "excavator cleanup", "crane cleanup",
"loader cleanup", "grader cleanup", "roller cleanup", "paver cleanup",
"compactor cleanup", "dump truck cleanup", "concrete mixer cleanup",
"cement truck cleanup", "tanker cleanup", "flatbed cleanup", "box truck cleanup",
"refrigerated truck cleanup", "tow truck cleanup", "wrecker cleanup",
"fire truck cleanup", "ambulance cleanup", "police car cleanup",
"squad car cleanup", "patrol car cleanup", "cruiser cleanup",
"undercover car cleanup", "detective car cleanup", "swat vehicle cleanup",
"armored vehicle cleanup", "tank cleanup", "military vehicle cleanup",
"humvee cleanup", "jeep cleanup", "armored personnel carrier cleanup",
"mine-resistant vehicle cleanup", "riot control vehicle cleanup",
"prison transport cleanup", "paddy wagon cleanup", "hearse cleanup",
"limo cleanup", "party bus cleanup", "tour bus cleanup", "double decker cleanup",
"articulated bus cleanup", "trolleybus cleanup", "trackless tram cleanup",
"guided bus cleanup", "bus rapid transit cleanup", "light rail cleanup",
"streetcar cleanup", "cable car cleanup", "funicular cleanup", "gondola cleanup",
"aerial tram cleanup", "chairlift cleanup", "ski lift cleanup", "ropeway cleanup",
"zip line cleanup", "people mover cleanup", "monorail cleanup", "maglev cleanup",
"bullet train cleanup", "high-speed rail cleanup", "commuter rail cleanup",
"freight rail cleanup", "heritage rail cleanup", "streetcar cleanup",
"interurban cleanup", "trolleybus cleanup", "bus cleanup", "coach cleanup",
"minibus cleanup", "shuttle cleanup", "taxi cleanup", "limousine cleanup",
"rickshaw cleanup", "cycle rickshaw cleanup", "pedicab cleanup",
"horse-drawn carriage cleanup", "dog sled cleanup", "snowmobile cleanup",
"ATV cleanup", "UTV cleanup", "dirt bike cleanup", "motorcycle cleanup",
"scooter cleanup", "moped cleanup", "electric bike cleanup", "hoverboard cleanup",
"segway cleanup", "electric scooter cleanup", "electric skateboard cleanup",
"electric unicycle cleanup", "electric wheelchair cleanup", "mobility scooter cleanup",
"golf cart cleanup", "utility vehicle cleanup", "forklift cleanup", "tractor cleanup",
"backhoe cleanup", "bulldozer cleanup", "excavator cleanup", "crane cleanup",
"loader cleanup", "grader cleanup", "roller cleanup", "paver cleanup",
"compactor cleanup", "dump truck cleanup", "concrete mixer cleanup",
"cement truck cleanup", "tanker cleanup", "flatbed cleanup", "box truck cleanup",
"refrigerated truck cleanup", "tow truck cleanup", "wrecker cleanup",
"fire truck cleanup", "ambulance cleanup", "police car cleanup",
"squad car cleanup", "patrol car cleanup", "cruiser cleanup",
"undercover car cleanup", "detective car cleanup", "swat vehicle cleanup",
"armored vehicle cleanup", "tank cleanup", "military vehicle cleanup",
"humvee cleanup", "jeep cleanup", "armored personnel carrier cleanup",
"mine-resistant vehicle cleanup", "riot control vehicle cleanup",
"prison transport cleanup", "paddy wagon cleanup", "hearse cleanup",
"limo cleanup", "party bus cleanup", "tour bus cleanup", "double decker cleanup",
"articulated bus cleanup", "trolleybus cleanup", "trackless tram cleanup",
"guided bus cleanup", "bus rapid transit cleanup", "light rail cleanup",
"streetcar cleanup", "cable car cleanup", "funicular cleanup", "gondola cleanup",
"aerial tram cleanup", "chairlift cleanup", "ski lift cleanup", "ropeway cleanup",
"zip line cleanup", "people mover cleanup", "monorail cleanup", "maglev cleanup",
"bullet train cleanup", "high-speed rail cleanup", "commuter rail cleanup",
"freight rail cleanup", "heritage rail cleanup", "streetcar cleanup",
"interurban cleanup", "trolleybus cleanup", "bus cleanup", "coach cleanup",
"minibus cleanup", "shuttle cleanup", "taxi cleanup", "limousine cleanup",
"rickshaw cleanup", "cycle rickshaw cleanup", "pedicab cleanup",
"horse-drawn carriage cleanup", "dog sled cleanup", "snowmobile cleanup",
"ATV cleanup", "UTV cleanup", "dirt bike cleanup", "motorcycle cleanup",
"scooter cleanup", "moped cleanup", "electric bike cleanup", "hoverboard cleanup",
"segway cleanup", "electric scooter cleanup", "electric skateboard cleanup",
"electric unicycle cleanup", "electric wheelchair cleanup", "mobility scooter cleanup",
"golf cart cleanup", "utility vehicle cleanup", "forklift cleanup", "tractor cleanup",
"backhoe cleanup", "bulldozer cleanup", "excavator cleanup", "crane cleanup",
"loader cleanup", "grader cleanup", "roller cleanup", "paver cleanup",
"compactor cleanup", "dump truck cleanup", "concrete mixer cleanup",
"cement truck cleanup", "tanker cleanup", "flatbed cleanup", "box truck cleanup",
"refrigerated truck cleanup", "tow truck cleanup", "wrecker cleanup",
"fire truck cleanup", "ambulance cleanup", "police car cleanup",
"squad car cleanup", "patrol car cleanup", "cruiser cleanup",
"undercover car cleanup", "detective car cleanup", "swat vehicle cleanup",
"armored vehicle cleanup", "tank cleanup", "military vehicle cleanup",
"humvee cleanup", "jeep cleanup", "armored personnel carrier cleanup",
"mine-resistant vehicle cleanup", "riot control vehicle cleanup",
"prison transport cleanup", "paddy wagon cleanup", "hearse cleanup",
"limo cleanup", "party bus cleanup", "tour bus cleanup", "double decker cleanup",
"articulated bus cleanup", "trolleybus cleanup", "trackless tram cleanup",
"guided bus cleanup", "bus rapid transit cleanup", "light rail cleanup",
"streetcar cleanup", "cable car cleanup", "funicular cleanup", "gondola cleanup",
"aerial tram cleanup", "chairlift cleanup", "ski lift cleanup", "ropeway cleanup",
"zip line cleanup", "people mover cleanup", "monorail cleanup", "maglev cleanup",
"bullet train cleanup", "high-speed rail cleanup", "commuter rail cleanup",
"freight rail cleanup", "heritage rail cleanup", "streetcar cleanup",
"interurban cleanup", "trolleybus cleanup", "bus cleanup", "coach cleanup",
"minibus cleanup", "shuttle cleanup", "taxi cleanup", "limousine cleanup",
"rickshaw cleanup", "cycle rickshaw cleanup", "pedicab cleanup",
"horse-drawn carriage cleanup", "dog sled cleanup", "snowmobile cleanup",
"ATV cleanup", "UTV cleanup", "dirt bike cleanup", "motorcycle cleanup",
"scooter cleanup", "moped cleanup", "electric bike cleanup", "hoverboard cleanup",
"segway cleanup", "electric scooter cleanup", "electric skateboard cleanup",
"electric unicycle cleanup", "electric wheelchair cleanup", "mobility scooter cleanup",
"golf cart cleanup", "utility vehicle cleanup", "forklift cleanup", "tractor cleanup",
"backhoe cleanup", "bulldozer cleanup", "excavator cleanup", "crane cleanup",
"loader cleanup", "grader cleanup", "roller cleanup", "paver cleanup",
"compactor cleanup", "dump truck cleanup", "concrete mixer cleanup",
"cement truck cleanup", "tanker cleanup", "flatbed cleanup", "box truck cleanup",
"refrigerated truck cleanup", "tow truck cleanup", "wrecker cleanup",
"fire truck cleanup", "ambulance cleanup", "police car cleanup",
"squad car cleanup", "patrol car cleanup", "cruiser cleanup",
"undercover car cleanup", "detective car cleanup", "swat vehicle cleanup",
"armored vehicle cleanup", "tank cleanup", "military vehicle cleanup",
"humvee cleanup", "jeep cleanup", "armored personnel carrier cleanup",
"mine-resistant vehicle cleanup", "riot control vehicle cleanup",
"prison transport cleanup", "paddy wagon cleanup", "hearse cleanup",
"limo cleanup", "party bus cleanup", "tour bus cleanup", "double decker cleanup",
"articulated bus cleanup", "trolleybus cleanup", "trackless tram cleanup",
"guided bus cleanup", "bus rapid transit cleanup", "light rail cleanup",
"streetcar cleanup", "cable car cleanup", "funicular cleanup", "gondola cleanup",
"aerial tram cleanup", "chairlift cleanup", "ski lift cleanup", "ropeway cleanup",
"zip line cleanup", "people mover cleanup", "monorail cleanup", "maglev cleanup",
"bullet train cleanup", "high-speed rail cleanup", "commuter rail cleanup",
"freight rail cleanup", "heritage rail cleanup", "streetcar cleanup",
"interurban cleanup", "trolleybus cleanup", "bus cleanup", "coach cleanup",
"minibus cleanup", "shuttle cleanup", "taxi cleanup", "limousine cleanup",
"rickshaw cleanup", "cycle rickshaw cleanup", "pedicab cleanup",
"horse-drawn carriage cleanup", "dog sled cleanup", "snowmobile cleanup",
"ATV cleanup", "UTV cleanup", "dirt bike cleanup", "motorcycle cleanup",
"scooter cleanup", "moped cleanup", "electric bike cleanup", "hoverboard cleanup",
"segway cleanup", "electric scooter cleanup", "electric skateboard cleanup",
"electric unicycle cleanup", "electric wheelchair cleanup", "mobility scooter cleanup",
"golf cart cleanup", "utility vehicle cleanup", "forklift cleanup", "tractor cleanup",
"backhoe cleanup", "bulldozer cleanup", "excavator cleanup", "crane cleanup",
"loader cleanup", "grader cleanup", "roller cleanup", "paver cleanup",
"compactor cleanup", "dump truck cleanup", "concrete mixer cleanup",
"cement truck cleanup", "tanker cleanup", "flatbed cleanup", "box truck cleanup",
"refrigerated truck cleanup", "tow truck cleanup", "wrecker cleanup",
"fire truck cleanup", "ambulance cleanup", "police car cleanup",
"squad car cleanup", "patrol car cleanup", "cruiser cleanup",
"undercover car cleanup", "detective car cleanup", "swat vehicle cleanup",
"armored vehicle cleanup", "tank cleanup", "military vehicle cleanup",
"humvee cleanup", "jeep cleanup", "armored personnel carrier cleanup",
"mine-resistant vehicle cleanup", "riot control vehicle cleanup",
"prison transport cleanup", "paddy wagon cleanup", "hearse cleanup",
"limo cleanup", "party bus cleanup", "tour bus cleanup", "double decker cleanup",
"articulated bus cleanup", "trolleybus cleanup", "trackless tram cleanup",
"guided bus cleanup", "bus rapid transit cleanup", "light rail cleanup",
"streetcar cleanup", "cable car cleanup", "funicular cleanup", "gondola cleanup",
"aerial tram cleanup", "chairlift cleanup", "ski lift cleanup", "ropeway cleanup",
"zip line cleanup", "people mover cleanup", "monorail cleanup", "maglev cleanup",
"bullet train cleanup", "high-speed rail cleanup", "commuter rail cleanup",
"freight rail cleanup", "heritage rail cleanup", "streetcar cleanup",
"interurban cleanup", "trolleybus cleanup", "bus cleanup", "coach cleanup",
"minibus cleanup", "shuttle cleanup", "taxi cleanup", "limousine cleanup",
"rickshaw cleanup", "cycle rickshaw cleanup", "pedicab cleanup",
"horse-drawn carriage cleanup", "dog sled cleanup", "snowmobile cleanup",
"ATV cleanup", "UTV cleanup", "dirt bike cleanup", "motorcycle cleanup",
"scooter cleanup", "moped cleanup", "electric bike cleanup", "hoverboard cleanup",
"segway cleanup", "electric scooter cleanup", "electric skateboard cleanup",
"electric unicycle cleanup", "electric wheelchair cleanup", "mobility scooter cleanup",
"golf cart cleanup", "utility vehicle cleanup", "forklift cleanup", "tractor cleanup",
"backhoe cleanup", "bulldozer cleanup", "excavator cleanup", "crane cleanup",
"loader cleanup", "grader cleanup", "roller cleanup", "paver cleanup",
"compactor cleanup", "dump truck cleanup", "concrete mixer cleanup",
"cement truck cleanup", "tanker cleanup", "flatbed cleanup", "box truck cleanup",
"refrigerated truck cleanup", "tow truck cleanup", "wrecker cleanup",
"fire truck cleanup", "ambulance cleanup", "police car cleanup",
"squad car cleanup", "patrol car cleanup", "cruiser cleanup",
"undercover car cleanup", "detective car cleanup", "swat vehicle cleanup",
"armored vehicle cleanup", "tank cleanup", "military vehicle cleanup",
"humvee cleanup", "jeep cleanup", "armored personnel carrier cleanup",
"mine-resistant vehicle cleanup", "riot control vehicle cleanup",
"prison transport cleanup", "paddy wagon cleanup", "hearse cleanup",
"limo cleanup", "party bus cleanup", "tour bus cleanup", "double decker cleanup",
"articulated bus cleanup", "trolleybus cleanup", "trackless tram cleanup",
"guided bus cleanup", "bus rapid transit cleanup", "light rail cleanup",
"streetcar cleanup", "cable car cleanup", "funicular cleanup", "gondola cleanup",
"aerial tram cleanup", "chairlift cleanup", "ski lift cleanup", "ropeway cleanup",
"zip line cleanup", "people mover cleanup", "monorail cleanup", "maglev cleanup",
"bullet train cleanup", "high-speed rail cleanup", "commuter rail cleanup",
"freight rail cleanup", "heritage rail cleanup", "streetcar cleanup",
"interurban cleanup", "trolleybus cleanup", "bus cleanup", "coach cleanup",
"minibus cleanup", "shuttle cleanup", "taxi cleanup", "limousine cleanup",
"rickshaw cleanup", "cycle rickshaw cleanup", "pedicab cleanup",
"horse-drawn carriage cleanup", "dog sled cleanup", "snowmobile cleanup",
"ATV cleanup", "UTV cleanup", "dirt bike cleanup", "motorcycle cleanup",
"scooter cleanup", "moped cleanup", "electric bike cleanup", "hoverboard cleanup",
"segway cleanup", "electric scooter cleanup", "electric skateboard cleanup",
"electric unicycle cleanup", "electric wheelchair cleanup", "mobility scooter cleanup",
"golf cart cleanup", "utility vehicle cleanup", "forklift cleanup", "tractor cleanup",
"backhoe cleanup", "bulldozer cleanup", "excavator cleanup", "crane cleanup",
"loader cleanup", "grader cleanup", "roller cleanup", "paver cleanup",
"compactor cleanup", "dump truck cleanup", "concrete mixer cleanup",
"cement truck cleanup", "tanker cleanup", "flatbed cleanup", "box truck cleanup",
"refrigerated truck cleanup", "tow truck cleanup", "wrecker cleanup",
"fire truck cleanup", "ambulance cleanup", "police car cleanup",
"squad car cleanup", "patrol car cleanup", "cruiser cleanup",
"undercover car cleanup", "detective car cleanup", "swat vehicle cleanup",
"armored vehicle cleanup", "tank cleanup", "military vehicle cleanup",
"humvee cleanup", "jeep cleanup", "armored personnel carrier cleanup",
"mine-resistant vehicle cleanup", "riot control vehicle cleanup",
"prison transport cleanup", "paddy wagon cleanup", "hearse cleanup",
"limo cleanup", "party bus cleanup", "tour bus cleanup", "double decker cleanup",
"articulated bus cleanup", "trolleybus cleanup", "trackless tram cleanup",
"guided bus cleanup", "bus rapid transit cleanup", "light rail cleanup",
"streetcar cleanup", "cable car cleanup", "funicular cleanup", "gondola cleanup",
"aerial tram cleanup", "chairlift cleanup", "ski lift cleanup", "ropeway cleanup",
"zip line cleanup", "people mover cleanup", "monorail cleanup", "maglev cleanup",
"bullet train cleanup", "high-speed rail cleanup", "commuter rail cleanup",
"freight rail cleanup", "heritage rail cleanup", "streetcar cleanup",
"interurban cleanup", "trolleybus cleanup", "bus cleanup", "coach cleanup",
"minibus cleanup", "shuttle cleanup", "taxi cleanup", "limousine cleanup",
"rickshaw cleanup", "cycle rickshaw cleanup", "pedicab cleanup",
"horse-drawn carriage cleanup", "dog sled cleanup", "snowmobile cleanup",
"ATV cleanup", "UTV cleanup", "dirt bike cleanup", "motorcycle cleanup",
"scooter cleanup", "moped cleanup", "electric bike cleanup", "hoverboard cleanup",
"segway cleanup", "electric scooter cleanup", "electric skateboard cleanup",
"electric unicycle cleanup", "electric wheelchair cleanup", "mobility scooter cleanup",
"golf cart cleanup", "utility vehicle cleanup", "forklift cleanup", "tractor cleanup",
"backhoe cleanup", "bulldozer cleanup", "excavator cleanup", "crane cleanup",
"loader cleanup", "grader cleanup", "roller cleanup", "paver cleanup",
"compactor cleanup", "dump truck cleanup", "concrete mixer cleanup",
"cement truck cleanup", "tanker cleanup", "flatbed cleanup", "box truck cleanup",
"refrigerated truck cleanup", "tow truck cleanup", "wrecker cleanup",
"fire truck cleanup", "ambulance cleanup", "police car cleanup",
"squad car cleanup", "patrol car cleanup", "cruiser cleanup",
"undercover car cleanup", "detective car cleanup", "swat vehicle cleanup",
"armored vehicle cleanup", "tank cleanup", "military vehicle cleanup",
"humvee cleanup", "jeep cleanup", "armored personnel carrier cleanup",
"mine-resistant vehicle cleanup", "riot control vehicle cleanup",
"prison transport cleanup", "paddy wagon cleanup", "hearse cleanup",
"limo cleanup", "party bus cleanup", "tour bus cleanup", "double decker cleanup",
"articulated bus cleanup", "trolleybus cleanup", "trackless tram cleanup",
"guided bus cleanup", "bus rapid transit cleanup", "light rail cleanup",
"streetcar cleanup", "cable car cleanup", "funicular cleanup", "gondola cleanup",
"aerial tram cleanup", "chairlift cleanup", "ski lift cleanup", "ropeway cleanup",
"zip line cleanup", "people mover cleanup", "monorail cleanup", "maglev cleanup",
"bullet train cleanup", "high-speed rail cleanup", "commuter rail cleanup",
"freight rail cleanup", "heritage rail cleanup", "streetcar cleanup",
"interurban cleanup", "trolleybus cleanup", "bus cleanup", "coach cleanup",
"minibus cleanup", "shuttle cleanup", "taxi cleanup", "limousine cleanup",
"rickshaw cleanup", "cycle rickshaw cleanup", "pedicab cleanup",
"horse-drawn carriage cleanup", "dog sled cleanup", "snowmobile cleanup",
"ATV cleanup", "UTV cleanup", "dirt bike cleanup", "motorcycle cleanup",
"scooter cleanup", "moped cleanup", "electric bike cleanup", "hoverboard cleanup",
"segway cleanup", "electric scooter cleanup", "electric skateboard cleanup",
"electric unicycle cleanup", "electric wheelchair cleanup", "mobility scooter cleanup",
"golf cart cleanup", "utility vehicle cleanup", "forklift cleanup", "tractor cleanup",
"backhoe cleanup", "bulldozer cleanup", "excavator cleanup", "crane cleanup",
"loader cleanup", "grader cleanup", "roller cleanup", "paver cleanup",
"compactor cleanup", "dump truck cleanup", "concrete mixer cleanup",
"cement truck cleanup", "tanker cleanup", "flatbed cleanup", "box truck cleanup",
"refrigerated truck cleanup", "tow truck cleanup", "wrecker cleanup",
"fire truck cleanup", "ambulance cleanup", "police car cleanup",
"squad car cleanup", "patrol car cleanup", "cruiser cleanup",
"undercover car cleanup", "detective car cleanup", "swat vehicle cleanup",
"armored vehicle cleanup", "tank cleanup", "military vehicle cleanup",
"humvee cleanup", "jeep cleanup", "armored personnel carrier cleanup",
"mine-resistant vehicle cleanup", "riot control vehicle cleanup",
"prison transport cleanup", "paddy wagon cleanup", "hearse cleanup",
"limo cleanup", "party bus cleanup", "tour bus cleanup", "double decker cleanup",
"articulated bus cleanup", "trolleybus cleanup", "trackless tram cleanup",
"guided bus cleanup", "bus rapid transit cleanup", "light rail cleanup",
"streetcar cleanup", "cable car cleanup", "funicular cleanup", "gondola cleanup",
"aerial tram cleanup", "chairlift cleanup", "ski lift cleanup", "ropeway cleanup",
"zip line cleanup", "people mover cleanup", "monorail cleanup", "maglev cleanup",
"bullet train cleanup", "high-speed rail cleanup", "commuter rail cleanup",
"freight rail cleanup", "heritage rail cleanup", "streetcar cleanup",
"interurban cleanup", "trolleybus cleanup", "bus cleanup", "coach cleanup",
"minibus cleanup", "shuttle cleanup", "taxi cleanup", "limousine cleanup",
"rickshaw cleanup", "cycle rickshaw cleanup", "pedicab cleanup",
"horse-drawn carriage cleanup", "dog sled cleanup", "snowmobile cleanup",
"ATV cleanup", "UTV cleanup", "dirt bike cleanup", 

    # Waste Categories (40+)
    "trash", "litter", "garbage", "refuse", "rubbish", "debris", "waste", "junk",
    "plastic waste", "food waste", "organic waste", "yard waste", "construction waste",
    "electronic waste", "hazardous waste", "household waste", "industrial waste",
    "marine debris", "microplastics", "nurdles", "cigarette butts", "chewing gum",
    "fast food packaging", "single-use plastics", "plastic bags", "plastic bottles",
    "plastic straws", "plastic utensils", "styrofoam", "fishing gear", "ghost nets",
    "abandoned boats", "tires", "scrap metal", "glass bottles", "aluminum cans",
    "paper waste", "cardboard", "textile waste", "diapers", "medical waste",
    "hazardous household waste", "paint disposal", "battery recycling",
    "oil disposal", "chemical waste", "asbestos removal","roadside waste","roadside dump",

    # Recycling & Waste Management (50+)
    "recycling", "upcycling", "downcycling", "composting", "vermicomposting",
    "waste management", "waste reduction", "waste audit", "zero waste",
    "circular economy", "source reduction", "reuse", "repair", "refill",
    "donation", "thrift", "swap", "sharing economy", "material recovery",
    "single-stream recycling", "dual-stream recycling", "e-waste recycling",
    "textile recycling", "battery recycling", "oil recycling", "metal recycling",
    "glass recycling", "paper recycling", "plastic recycling", "organic recycling",
    "compostable", "biodegradable", "landfill diversion", "waste-to-energy",
    "incineration", "anaerobic digestion", "pyrolysis", "gasification",
    "extended producer responsibility", "product stewardship", "take-back programs",
    "deposit return schemes", "pay-as-you-throw", "bulky waste", "hazardous waste",
    "waste characterization", "waste composition", "diversion rate", "MRF",
    "transfer station", "sanitary landfill", "leachate", "methane capture",

    # Environmental Issues (40+)
    "pollution", "littering", "illegal dumping", "fly-tipping", "marine pollution",
    "plastic pollution", "water pollution", "air pollution", "soil contamination",
    "noise pollution", "light pollution", "thermal pollution", "nutrient pollution",
    "sediment pollution", "chemical pollution", "oil spills", "sewage overflow",
    "stormwater runoff", "urban runoff", "agricultural runoff", "acid rain",
    "eutrophication", "algal blooms", "dead zones", "bioaccumulation",
    "microplastics in food chain", "great pacific garbage patch", "gyres",
    "climate change", "global warming", "carbon emissions", "methane emissions",
    "deforestation", "desertification", "soil erosion", "habitat destruction",
    "biodiversity loss", "invasive species", "species extinction", "ecosystem collapse",
    "environmental degradation", "resource depletion", "overshoot day",

    # Sustainability (40+)
    "sustainability", "sustainable development", "green living", "eco-friendly",
    "environmentally friendly", "carbon footprint", "ecological footprint",
    "water footprint", "energy conservation", "water conservation", "resource efficiency",
    "green building", "LEED certification", "passive house", "net zero",
    "renewable energy", "solar", "wind", "geothermal", "hydropower", "biomass",
    "energy efficiency", "green technology", "clean technology", "green chemistry",
    "sustainable agriculture", "organic farming", "permaculture", "regenerative agriculture",
    "urban farming", "community gardens", "food security", "local food", "farm to table",
    "slow food", "meatless Monday", "plant-based", "vegan", "vegetarian",
    "sustainable fashion", "ethical consumerism", "minimalism", "simple living",
    "voluntary simplicity", "degrowth", "steady state economy",

    # Community & Policy (40+)
    "community engagement", "civic participation", "volunteerism", "service learning",
    "corporate volunteering", "employee engagement", "team building", "youth programs",
    "school programs", "scouts", "girl scouts", "boy scouts", "4-H", "rotary",
    "lions club", "kiwanis", "environmental education", "public awareness",
    "behavior change", "nudge theory", "community-based social marketing",
    "environmental policy", "litter laws", "plastic bans", "bag bans", "straw bans",
    "extended producer responsibility", "product stewardship", "right to repair",
    "green procurement", "sustainable purchasing", "environmental justice",
    "climate justice", "just transition", "green jobs", "environmental health",
    "public health", "environmental racism", "food justice", "water justice",
    "urban planning", "smart growth", "new urbanism", "complete streets",
    "transit-oriented development", "walkability", "bikeability", "green infrastructure",
    "low impact development", "sponge cities","bot",

    # Tools & Equipment (30+)
    "litter pickers", "grabbers", "gloves", "safety vests", "reflective gear",
    "trash bags", "recycling bins", "compost bins", "wheelbarrows", "rakes",
    "brooms", "shovels", "hoes", "trowels", "pruners", "hedge trimmers",
    "wheelie bins", "dumpsters", "roll-off containers", "trash cans",
    "recycling carts", "compost tumblers", "water bottles", "reusable bags",
    "reusable utensils", "reusable straws", "water stations", "hydration stations",
    "first aid kits", "sunscreen", "bug spray", "safety glasses", "hard hats",
    "work boots", "high-visibility clothing", "weather radios", "trash skimmers",
    "waterway cleanup tools", "beach rakes", "sand sifters","dustbins","hand gloves",

    # Events & Campaigns (30+)
    "Earth Day", "World Cleanup Day", "Coastal Cleanup Day", "Great American Cleanup",
    "Clean Up the World", "Plastic Free July", "World Environment Day",
    "Arbor Day", "World Oceans Day", "World Water Day", "America Recycles Day",
    "Buy Nothing Day", "Car Free Day", "Meatless Monday", "Bike to Work Day",
    "Park(ing) Day", "Jane's Walk", "Love Your Block", "Keep America Beautiful",
    "Surfrider Foundation", "Ocean Conservancy", "Sierra Club", "Nature Conservancy",
    "World Wildlife Fund", "Greenpeace", "350.org", "Extinction Rebellion",
    "Fridays for Future", "Youth Climate Strike", "Sunrise Movement",
    "Citizens' Climate Lobby", "Transition Towns", "Slow Food Movement",
    "Zero Waste Home", "Plastic Pollution Coalition","swach bharat","yamuna cleaning drive","yamuna cleanup","ganga clean","Swachh Bharat Abhiyan",

    #india specific topics
    "Swachh Bharat Mission", "Clean India Mission", "Namami Gange", "Swachh Rail Swachh Bharat",
    "ODF", "ODF+", "ODF++", "Open Defecation Free", "ODF villages", "ODF Plus villages",
    "ODF Plus Aspiring", "ODF Plus Model", "ODF Plus certification", "ODF Plus status",
    "ODF Plus guidelines", "ODF Plus solid waste management", "ODF Plus faecal sludge management",
    "Swachh Iconic Places", "Swachhta Pakhwada", "Swachhata Hi Seva", "Toilet for All",
    "Sanitation workers", "Community toilets", "Public toilets", "Bio-toilets",
    "Smart City cleanliness", "Municipal solid waste rules", "Door-to-door garbage collection",
    "Waste segregation at source", "Green ambassadors", "Swachh survekshan",
    "Waste warriors", "Plastic ban India", "Cleanest cities in India", "Urban local bodies cleanup",
    "Slum area sanitation", "Waste pickers", "Self-help groups waste management",
    "IEC activities sanitation", "India garbage free mission", "Swachh gram yojana",
    "Zila Swachhta committees", "Village cleanliness drive", "Panchayat level sanitation",
    "Eco clubs", "Swachh Vidyalaya", "Behavior change campaign sanitation",
    "Solid Waste Management India", "Liquid Waste Management India", "Community engagement India",
    "Swachhta Action Plan", "Citizen feedback sanitation", "Jan Andolan cleanliness",
    "Sanitation scorecard", "Faecal sludge treatment India", "Compost from waste",
    "MoHUA sanitation", "SBM Gramin", "SBM Urban", "State Swachh Missions",
    "District Swachh Bharat Mission", "Swachhta Darpan", "Sanitation ranking India",
    "Toilet feedback app", "Open defecation tracking", "Clean village award",
    "Clean city award India", "Mera Gaon Mera Gaurav cleanliness", "Village action plan sanitation",
    "Gram Sabha sanitation awareness", "India cleanliness awards", "Clean river project India",
    "Plastic-free village", "Sanitation technology pilot India", "Smart toilets India",
    "Water and sanitation committee India", "Nirmal Gram Puraskar", "Sulabh International",
    "Twin pit toilet system", "Panchayati Raj Sanitation", "Sanitation innovation challenge India",
    "Bio-digester toilets India", "Handwashing awareness India", "Health hygiene drive India",
    "District cleanliness index", "Sanitation entrepreneurship India", "Toilet use behavior change",
    "Menstrual hygiene campaign India", "Solid-liquid resource management India", "Swachh Bharat interns",
    "National Sanitation Day", "Toilet construction subsidy India", "School toilet construction India",
    "CSR in sanitation India", "Youth involvement in cleaning drives", "Swachhata clubs schools",
    "Women-led sanitation campaigns", "Sanitation drives rural India", "Sanitation behavior dashboard",
    "Clean streets initiative India", "Religious site sanitation", "Rural toilet mapping India",
    "Village development sanitation focus", "Waste to wealth India", "Plogging drives India",
    "Clean market initiative India", "Urban sanitation policy India", "Dry waste collection centers",
    "Wet waste composting centers", "City sanitation plan", "State sanitation strategy",
    "Local government sanitation programs", "Urban hygiene promotion", "Drain desilting India",
    "Water logging prevention India", "River bank cleaning India", "Ghat cleaning campaigns",
    "Swachhata mobile app", "ULB sanitation rankings", "Toilet construction targets India",
    "Village sanitation volunteer", "Sarpanch sanitation leadership", "Zila Parishad sanitation initiatives",
    "District Swachhta plan", "Sanitation budget India", "Public awareness sanitation media",
    "IEC campaign SBM", "Waste processing plants India", "Vermi composting India",
    "RDF plants India", "Material recovery facility India", "Waste to energy India",
    "Sanitation dashboard MoHUA", "Toilet tracker India", "Solid waste vehicle tracking",
    "Sanitation data analytics India", "SWM training India", "SLWM training modules India",
    "Decentralized waste management India", "Incineration awareness India", "Sanitation education rural India",
    "Toilet building materials subsidy", "Sanitation inspection mobile app", "Swachhta Senani",
    "Swachh Sarvekshan League", "School sanitation rating", "Sanitation pledge events",
    "Jan Bhagidari sanitation", "Smart solutions for sanitation India", "Public toilet locator app India",
    "Sanitation field verification", "District wise cleanliness score", "Urban-rural sanitation gap",
    "School sanitation clubs", "WaterAid India", "India Water Portal sanitation",
    "Safaigiri awards", "MyCleanIndia campaign", "Clean India Challenge",
    "Sanitation Innovation Hub India", "Community-led sanitation", "Waste minimization circles India",
    "Plastic-free panchayats", "Clean India youth program", "NSS sanitation initiatives",
    "Rural sanitation innovation", "Hand pump sanitation", "Community-led total sanitation India",
    "Ganga rejuvenation projects", "Urban cleanliness indicators India", "Clean India fellowships",
    "SBM monitoring tools", "Village Nigrani Samiti sanitation", "Street vendor hygiene India",
    "Temple town sanitation", "Sanitation stories India", "Best practices in sanitation India",
    "Swachhata startup India", "Swachh Bharat Hackathon", "eToilets India",
    "Urban waste innovation challenge India", "Digital monitoring toilets India", "Plastic waste audit India",
    "India waste tracking app", "Swachhta Sankalp", "Public place hygiene India",
    "India cleanliness timeline", "Gandagi Mukt Bharat", "Clean street food India",
    "Rural sanitation initiatives", "Ganga Action Plan", "Waste-to-energy plants India", 
    "City-level sanitation strategy", "Municipal sanitation guidelines", "Waste management policy India", 
    "Sanitation facilities for differently-abled", "Sanitation during festivals India", "Slum sanitation improvement", 
    "Clean village program India", "Health and hygiene awareness campaigns", "Sanitation education in schools", 
    "Women empowerment through sanitation", "Sustainable urban sanitation", "Plastic waste management India", 
    "E-waste management India", "Awareness about hygiene in schools", "Improved sanitation practices", 
    "Sanitation investment India", "Green waste composting India", "Public private partnerships in sanitation", 
    "Smart city waste management", "Single-use plastic phase-out India", "Clean streets campaign India", 
    "Sanitation in rural schools", "Sanitation workers welfare", "Public toilet maintenance India", 
    "Hygiene and cleanliness outreach programs", "Zero-waste India movement", "Cleanliness drives in temples", 
    "Health impact of sanitation India", "Swachh Bharat ranking India", "Government sanitation support", 
    "Plastic-free festivals", "Curbing open defecation in India", "Mobile sanitation units", "District level sanitation solutions", 
    "Rainwater harvesting in sanitation", "Clean city initiatives India", "Bio-toilets innovation India", 
    "Waste recycling schemes India", "Sanitation facilities in hilly regions", "Plogging events India", 
    "Awareness about menstrual hygiene", "Integrated waste management India", "E-waste collection drives India", 
    "Swachhata Rath India", "Smart sanitation solutions India", "Community-led sanitation campaigns", 
    "Street cleaning tools and equipment India", "Water conservation and sanitation", "Health sanitation advisory India", 
    "Plastic-free schools India", "School cleanliness monitoring India", "Solid waste handling infrastructure", 
    "District-level waste management planning", "E-waste recycling awareness India", "Construction waste management India", 
    "Eco-friendly sanitation technologies", "Women sanitation leadership India", "Community toilet sanitation India", 
    "Village sanitation task forces", "Behavioral change in sanitation practices", "Health and safety regulations sanitation", 
    "Collaborative waste reduction", "Village health sanitation initiatives", "Sanitation in border areas India", 
    "Plastic waste segregation India", "Solid waste management protocols India", "Green waste segregation", 
    "Street vendors sanitation India", "Swachh Bharat guidelines", "Municipal waste transportation systems", 
    "Environmentally friendly waste disposal India", "Awareness on sanitation and hygiene", "Urban sanitation challenges", 
    "Cleanliness awareness programs India", "Sanitation infrastructure development India", "Government incentives for sanitation", 
    "Swachh Bharat Action Plan", "Recycling centers India", "School sanitation programs", "Clean streets and green initiatives", 
    "Clean city competitions India", "Local waste management systems", "Slum area sanitation projects", "Public health and sanitation", 
    "Private sanitation businesses India", "Waste recycling incentives", "Cleaner public spaces India", "Sanitation app usage India", 
    "Odour-free sanitation solutions", "Environmental health and sanitation", "Zero garbage initiatives India", 
    "Hand hygiene campaigns India", "Cleanliness festivals India", "Sewage treatment plants India", "Hygiene campaigns for rural India", 
    "Sanitation outreach programs India", "Non-government sanitation initiatives India", "Sanitation monitoring tools India", 
    "Sanitation reporting apps", "Smart sanitation systems India", "Water pollution prevention campaigns", 
    "Cleanliness benchmarks India", "Toilet usage awareness India", "Solid waste tracking technology", 
    "Sanitation data management India", "Sanitation certification India", "Waste to energy projects India", 
    "Municipal waste treatment solutions", "Recycling initiatives India", "Waste segregation campaign India", 
    "Wetland restoration India", "Clean rivers programs India", "Sustainable waste management systems", 
    "Compostable waste solutions India", "Mobile toilet units India", "Public waste bins India", 
    "Sanitation capacity building India", "Swachh Bharat mobile apps", "Menstrual health sanitation India", 
    "Clean India campaign initiatives", "Plastic-free zones India", "Campaigns against littering", 
    "Local sanitation programs", "Plastic waste bans India", "Plogging drive programs India", "Green waste programs India", 
    "Plastic recycling campaigns", "Community waste management projects", "Sanitation literacy India", 
    "Sanitation leadership training", "Swachh Bharat impact assessment", "Ecosystem-based sanitation approaches", 
    "Water and sanitation partnerships India", "Clean water and sanitation solutions", "Sewer system clean-up India", 
    "Clean environment awareness programs", "Sanitation and public health India", "Sanitation awareness through media", 
    "Decentralized sanitation India", "Urban solid waste management systems", "Sanitation audit India", 
    "Zero plastic movement India", "Clean water initiatives India", "Plastic-free localities India", 
    "Eco-friendly sanitation alternatives", "Sanitation knowledge dissemination", "Clean energy sanitation solutions", 
    "Hygiene sanitation challenges", "Swachh Bharat survey India", "Sewage waste management India", 
    "Swachhata Mission India", "Rural sanitation improvement initiatives", "Smart city waste collection systems", 
    "Sanitation financial management", "Municipal waste management schemes", "Sanitation mapping India", 
    "Urban hygiene practices India", "Pollution control through sanitation", "Open defecation elimination campaigns", 
    "Swachh Bharat leadership India", "Public sanitation innovations India", "Clean-up campaigns in schools", 
    "Recycling technologies India", "Waste collection technologies", "Toilet construction initiatives India", 
    "Swachh Bharat feedback systems", "Sanitation progress monitoring India", "Clean-up movements India", 
    "Toilet usage improvement India", "District-level sanitation education", "Public sanitation volunteers India", 
    "Post-event cleaning India", "Waste management in rural areas", "Village sanitation schemes India", 
    "E-waste disposal systems India", "Toilet training programs India", "Sewage treatment awareness India", 
    "Plastic reduction campaigns India", "Sewage recycling initiatives India", "Local sanitation monitoring systems", 
    "Solid waste management awareness India", "Pollution-free villages India", "Community toilet maintenance India", 
    "Water management sanitation India", "Smart waste bins India", "Waste tracking mobile apps India", 
    "Swachh Bharat guidelines for municipalities", "Pollution control through waste management", "Public health sanitation campaigns", 
    "School sanitation surveys India", "Sanitation leadership programs India", "Decentralized waste management solutions", 
    "Sanitation infrastructure development in rural India", "Swachh Bharat goals India", "Eco-friendly sanitation systems", 
    "Urban waste segregation programs", "Municipal sanitation training India", "Community waste collection India","Swachh Bharat Abhiyan", "Clean India Mission", "Ganga cleanup", "Yamuna rejuvenation","Plastic waste management rules", "Waste to Wealth", "Clean Ganga Fund", "Namami Gange","National Green Corps", "Eco-Clubs", "Har Ghar Jal", "ODF (Open Defecation Free)","Swachh Survekshan", "Swachhata Hi Seva", "Swachh Vidyalaya", "Swachhata Pakhwada","Clean Temple Initiative", "Ghat cleanliness drives", "Railway station cleanup","Metro cleanliness", "Bus stand sanitation", "Market waste management","Slum sanitation", "Manual scavenging prohibition", "Safai Mitra Suraksha","Beach cleanup India", "Mangrove cleanup", "Western Ghats cleanup","Himalayan cleanup", "Desert cleanup Rajasthan", "Backwater cleanup Kerala","Houseboat waste management", "Spiti valley cleanup", "Ladakh plastic-free","Chennai beach cleanup", "Mumbai coastal cleanup", "Goa tourist waste","Varanasi ghat cleanup", "Haridwar cleanliness", "Rishikesh riverfront","Alang shipbreaking yard", "E-waste management Bangalore", "Tanneries cleanup Kanpur","Textile waste Tiruppur", "Leather waste Chennai", "Construction waste Delhi","Festival waste management", "Ganesh idol immersion", "Durga Puja waste","Diwali cleanup", "Holi waste", "Kumbh Mela sanitation", "Pushkar fair cleanup","Temple flower waste", "Banana leaf recycling", "Coconut waste utilization","Areca leaf plate making", "Sacred grove conservation", "Bishnoi community cleanups","Tribal waste initiatives", "Panchayat cleanliness", "Gram Swachhata", "Swachhata App", "CPCB guidelines", "State pollution control boards","ULB sanitation workers", "Paryavaran Mitra", "Green Good Deeds",
"Waste picker integration", "Kabadiwala network", "Raddiwalas recycling",
"Local composting", "Biomedical waste rules", "Hazardous waste management",
"Construction debris recycling", "C&D waste plants", "E-waste dismantling",
"Tetra Pak recycling", "Silicon Valley waste", "IT park e-waste",
"Startup waste solutions", "Wastepreneurs India", "Clean tech innovations",
"Solar waste handling", "Wind turbine recycling", "EV battery disposal",
"Air pollution control", "Stubble burning solutions", "Waste to energy plants",
"Bio-CNG projects", "Plastic roads", "Rail track recycling",
"Waterbody restoration", "Stepwell cleanup", "Lake revival projects",
"Pond rejuvenation", "Well recharge", "Riverfront development",
"Coastal regulation", "CRZ cleanup", "Island cleanup Andaman",
"Lakshadweep plastic ban", "Marine litter control", "Fishing net recycling",
"Shipbreaking waste", "Port waste management", "Inland waterways cleanup",
"National Waterway 1", "Canal cleanup", "Dam debris removal",
"Reservoir desilting", "Tank rehabilitation", "Wetland conservation",
"Ramsar site cleanup", "Bird sanctuary waste", "National park sanitation",
"Tiger reserve cleanup", "Elephant corridor waste", "Wildlife waste",
"Pilgrimage waste", "Char Dham cleanup", "Amarnath yatra waste",
"Vaishno Devi sanitation", "Sabarimala waste", "Ajmer Sharif cleanliness",
"Golden Temple cleanup", "Meenakshi Temple waste", "Tirupati waste management",
"ISKCON food waste", "Gurudwara langar waste", "Dargah cleanliness",
"Church waste", "Mosque sanitation", "Jain temple waste",
"Buddhist site cleanup", "Heritage site conservation", "ASI cleanup",
"UNESCO site maintenance", "Fort cleanup", "Palace waste",
"Haveli sanitation", "Stepwell restoration", "Cave temple cleanliness",
"Monument waste", "Archaeological waste", "Museum waste",
"Art gallery waste", "Cultural site sanitation", "Folk art waste",
"Handicraft waste", "Textile recycling", "Loom waste",
"Pottery waste", "Metal craft waste", "Wood craft waste",
"Stone craft waste", "Bamboo waste", "Jute waste",
"Coir waste", "Silk waste", "Cotton waste",
"Wool waste", "Leather waste", "Paper waste",
"Glass waste", "Ceramic waste", "Terracotta waste",
"Clay waste", "Brass waste", "Copper waste",
"Bronze waste", "Iron waste", "Steel waste",
"Aluminum waste", "Zinc waste", "Lead waste",
"Tin waste", "Nickel waste", "Silver waste",
"Gold waste", "Platinum waste", "Palladium waste",
"Rhodium waste", "Mercury waste", "Cadmium waste",
"Chromium waste", "Arsenic waste", "Cyanide waste",
"Acid waste", "Alkali waste", "Solvent waste",
"Pesticide waste", "Herbicide waste", "Fungicide waste",
"Rodenticide waste", "Insecticide waste", "Fertilizer waste",
"Manure waste", "Compost waste", "Vermicompost waste",
"Biogas waste", "Biofuel waste", "Biodiesel waste",
"Ethanol waste", "Methanol waste", "Butanol waste",
"Propanol waste", "Pentanol waste", "Hexanol waste",
"Heptanol waste", "Octanol waste", "Nonanol waste",
"Decanol waste", "Undecanol waste", "Dodecanol waste",
"Tridecanol waste", "Tetradecanol waste", "Pentadecanol waste",
"Hexadecanol waste", "Heptadecanol waste", "Octadecanol waste",
"Nonadecanol waste", "Eicosanol waste", "Heneicosanol waste",
"Docosanol waste", "Tricosanol waste", "Tetracosanol waste",
"Pentacosanol waste", "Hexacosanol waste", "Heptacosanol waste",
"Octacosanol waste", "Nonacosanol waste", "Triacontanol waste",
"Hentriacontanol waste", "Dotriacontanol waste", "Tritriacontanol waste",
"Tetratriacontanol waste", "Pentatriacontanol waste", "Hexatriacontanol waste",
"Heptatriacontanol waste", "Octatriacontanol waste", "Nonatriacontanol waste",
"Tetracontanol waste", "Hentetracontanol waste", "Dotetracontanol waste",
"Tritetracontanol waste", "Tetratetracontanol waste", "Pentatetracontanol waste",
"Hexatetracontanol waste", "Heptatetracontanol waste", "Octatetracontanol waste",
"Nonatetracontanol waste", "Pentacontanol waste", "Henpentacontanol waste",
"Dopentacontanol waste", "Tripentacontanol waste", "Tetrapentacontanol waste",
"Pentapentacontanol waste", "Hexapentacontanol waste", "Heptapentacontanol waste",
"Octapentacontanol waste", "Nonapentacontanol waste", "Hexacontanol waste",
"Henhexacontanol waste", "Dohexacontanol waste", "Trihexacontanol waste",
"Tetrahexacontanol waste", "Pentahexacontanol waste", "Hexahexacontanol waste",
"Heptahexacontanol waste", "Octahexacontanol waste", "Nonahexacontanol waste",
"Heptacontanol waste", "Henheptacontanol waste", "Doheptacontanol waste",
"Triheptacontanol waste", "Tetraheptacontanol waste", "Pentaheptacontanol waste",
"Hexaheptacontanol waste", "Heptaheptacontanol waste", "Octaheptacontanol waste",
"Nonaheptacontanol waste", "Octacontanol waste", "Henoctacontanol waste",
"Dooctacontanol waste", "Trioctacontanol waste", "Tetraoctacontanol waste",
"Pentaoctacontanol waste", "Hexaoctacontanol waste", "Heptaoctacontanol waste",
"Octaoctacontanol waste", "Nonaoctacontanol waste", "Nonacontanol waste",
"Hennonacontanol waste", "Dononacontanol waste", "Trinonacontanol waste",
"Tetranonacontanol waste", "Pentanonacontanol waste", "Hexanonacontanol waste",
"Heptanonacontanol waste", "Octanonacontanol waste", "Nonanonacontanol waste",
"Hectanol waste", "Henhectanol waste", "Dohectanol waste",
"Trihectanol waste", "Tetrahectanol waste", "Pentahectanol waste",
"Hexahectanol waste", "Heptahectanol waste", "Octahectanol waste",
"Nonahectanol waste", "Kilanol waste", "Henkilanol waste",
"Dokilanol waste", "Trikilanol waste", "Tetrakilanol waste",
"Pentakilanol waste", "Hexakilanol waste", "Heptakilanol waste",
"Octakilanol waste", "Nonakilanol waste", "Methanol waste",
"Ethanol waste", "Propanol waste", "Butanol waste",
"Pentanol waste", "Hexanol waste", "Heptanol waste",
"Octanol waste", "Nonanol waste", "Decanol waste",
"Undecanol waste", "Dodecanol waste", "Tridecanol waste",
"Tetradecanol waste", "Pentadecanol waste", "Hexadecanol waste",
"Heptadecanol waste", "Octadecanol waste", "Nonadecanol waste",
"Eicosanol waste", "Heneicosanol waste", "Docosanol waste",
"Tricosanol waste", "Tetracosanol waste", "Pentacosanol waste",
"Hexacosanol waste", "Heptacosanol waste", "Octacosanol waste",
"Nonacosanol waste", "Triacontanol waste", "Hentriacontanol waste",
"Dotriacontanol waste", "Tritriacontanol waste", "Tetratriacontanol waste",
"Pentatriacontanol waste", "Hexatriacontanol waste", "Heptatriacontanol waste",
"Octatriacontanol waste", "Nonatriacontanol waste", "Tetracontanol waste",
"Hentetracontanol waste", "Dotetracontanol waste", "Tritetracontanol waste",
"Tetratetracontanol waste", "Pentatetracontanol waste", "Hexatetracontanol waste",
"Heptatetracontanol waste", "Octatetracontanol waste", "Nonatetracontanol waste",
"Pentacontanol waste", "Henpentacontanol waste", "Dopentacontanol waste",
"Tripentacontanol waste", "Tetrapentacontanol waste", "Pentapentacontanol waste",
"Hexapentacontanol waste", "Heptapentacontanol waste", "Octapentacontanol waste",
"Nonapentacontanol waste", "Hexacontanol waste", "Henhexacontanol waste",
"Dohexacontanol waste", "Trihexacontanol waste", "Tetrahexacontanol waste",
"Pentahexacontanol waste", "Hexahexacontanol waste", "Heptahexacontanol waste",
"Octahexacontanol waste", "Nonahexacontanol waste", "Heptacontanol waste",
"Henheptacontanol waste", "Doheptacontanol waste", "Triheptacontanol waste",
"Tetraheptacontanol waste", "Pentaheptacontanol waste", "Hexaheptacontanol waste",
"Heptaheptacontanol waste", "Octaheptacontanol waste", "Nonaheptacontanol waste",
"Octacontanol waste", "Henoctacontanol waste", "Dooctacontanol waste",
"Trioctacontanol waste", "Tetraoctacontanol waste", "Pentaoctacontanol waste",
"Hexaoctacontanol waste", "Heptaoctacontanol waste", "Octaoctacontanol waste",
"Nonaoctacontanol waste", "Nonacontanol waste", "Hennonacontanol waste",
"Dononacontanol waste", "Trinonacontanol waste", "Tetranonacontanol waste",
"Pentanonacontanol waste", "Hexanonacontanol waste", "Heptanonacontanol waste",
"Octanonacontanol waste", "Nonanonacontanol waste", "Hectanol waste",
"Henhectanol waste", "Dohectanol waste", "Trihectanol waste",
"Tetrahectanol waste", "Pentahectanol waste", "Hexahectanol waste",
"Heptahectanol waste", "Octahectanol waste", "Nonahectanol waste",
"Kilanol waste", "Henkilanol waste", "Dokilanol waste",
"Trikilanol waste", "Tetrakilanol waste", "Pentakilanol waste",
"Hexakilanol waste", "Heptakilanol waste", "Octakilanol waste",
"Nonakilanol waste","drain cleanup","drain cleaning","drain clean","sewage clean",
"clean rivers","clean locality", "explain"


}
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        message = data.get('message', '').strip()

        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400

        # Initialize session if not exists
        if session_id not in chat_sessions:
            chat_sessions[session_id] = {
                "created_at": datetime.now().isoformat(),
                "title": "New Chat",
                "messages": [],
                "is_topic_validated": False
            }

        session = chat_sessions[session_id]

        # Topic validation for first message
        if not session['is_topic_validated']:
            message_lower = message.lower()
            is_valid_topic = any(topic in message_lower for topic in ALLOWED_TOPICS)
            
            if not is_valid_topic:
                error_msg = "Please ask about community clean-up topics like recycling, volunteering, waste reduction, or event planning."
                session['messages'].append({
                    "sender": "bot",
                    "message": error_msg,
                    "timestamp": datetime.now().isoformat()
                })
                return jsonify({'response': error_msg, 'session_id': session_id}), 200
            
            session['is_topic_validated'] = True
            session['title'] = message[:20] + ("..." if len(message) > 20 else "")

            # Update chats
            chat_summary = {
                "session_id": session_id,
                "title": session['title'],
                "created_at": session['created_at']
            }
            chats[:] = [chat for chat in chats if chat['session_id'] != session_id]
            chats.append(chat_summary)
            chats[:] = chats[-10:]
            
            with open(CHATS_FILE, 'w') as f:
                json.dump(chats, f, indent=2)

        # Store user message
        session['messages'].append({
            "sender": "user",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

        # Prepare conversation history for Gemini
        conversation = [
            {"role": "user", "parts": [msg["message"]]} if msg["sender"] == "user"
            else {"role": "model", "parts": [msg["message"]]}
            for msg in session['messages']
        ]

        # Generate response
        try:
            response = model.generate_content(
                conversation,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_output_tokens": 500
                }
            )
        except Exception as api_error:
            logging.error(f"Gemini API error: {str(api_error)}")
            return jsonify({'error': 'Error generating response from AI model'}), 500

        bot_response = response.text.strip()

        # Store bot response
        session['messages'].append({
            "sender": "bot",
            "message": bot_response,
            "timestamp": datetime.now().isoformat()
        })

        # Update chats
        chat_summary = {
            "session_id": session_id,
            "title": session['title'],
            "created_at": session['created_at']
        }
        chats[:] = [chat for chat in chats if chat['session_id'] != session_id]
        chats.append(chat_summary)
        chats[:] = chats[-10:]
        
        with open(CHATS_FILE, 'w') as f:
            json.dump(chats, f, indent=2)

        return jsonify({
            'response': bot_response,
            'session_id': session_id,
            'messages': session['messages'],
            'title': session['title']
        }), 200

    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/new_chat', methods=['POST'])
def new_chat():
    try:
        session_id = str(uuid.uuid4())
        chat_sessions[session_id] = {
            "created_at": datetime.now().isoformat(),
            "title": "New Chat",
            "messages": [
                {
                    "sender": "bot",
                    "message": "Hello! I'm here to help with community clean-up initiatives. Ask me about:\n- Recycling programs ♻️\n- Volunteer opportunities 👥\n- Waste reduction strategies 🗑️\n- Clean-up event planning 📅",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "is_topic_validated": False
        }
        
        # Add to chats
        chat_summary = {
            "session_id": session_id,
            "title": "New Chat",
            "created_at": chat_sessions[session_id]['created_at']
        }
        chats.append(chat_summary)
        chats[:] = chats[-10:]
        
        with open(CHATS_FILE, 'w') as f:
            json.dump(chats, f, indent=2)

        return jsonify({
            'session_id': session_id,
            'messages': chat_sessions[session_id]['messages'],
            'title': chat_sessions[session_id]['title']
        }), 200
    except Exception as e:
        logging.error(f"Error in new_chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/recent_chats', methods=['GET'])
def get_recent_chats():
    try:
        return jsonify(chats), 200
    except Exception as e:
        logging.error(f"Error in recent_chats endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/chat/<session_id>', methods=['GET'])
def get_chat(session_id):
    try:
        if session_id in chat_sessions:
            return jsonify(chat_sessions[session_id]), 200
        return jsonify({'error': 'Session not found'}), 404
    except Exception as e:
        logging.error(f"Error in get_chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/clear-chats', methods=['DELETE'])
def clear_chats():
    try:
        chat_sessions.clear()
        chat_sessions["default"] = {
            "created_at": datetime.now().isoformat(),
            "title": "Community Clean-Up Help",
            "messages": [
                {
                    "sender": "bot",
                    "message": "Hello! I'm here to help with community clean-up initiatives. Ask me about:\n- Recycling programs ♻️\n- Volunteer opportunities 👥\n- Waste reduction strategies 🗑️\n- Clean-up event planning 📅",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "is_topic_validated": False
        }
        
        chats.clear()
        if os.path.exists(CHATS_FILE):
            os.remove(CHATS_FILE)
        with open(CHATS_FILE, 'w') as f:
            json.dump(chats, f, indent=2)

        return jsonify({'message': 'All chats cleared successfully'}), 200
    except Exception as e:
        logging.error(f"Error clearing chats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
