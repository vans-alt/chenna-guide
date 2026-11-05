from math import ceil
from urllib.parse import quote_plus
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# category: Sights | Beach | Temple | Food | Culture
PLACES = [
    {"id": 1, "name": "Marina Beach", "category": "Beach", "area": "Marina", "hours": 2,
     "desc": "One of the longest urban beaches in the world. Go at sunrise or evening and try sundal."},
    {"id": 2, "name": "Fort St. George", "category": "Sights", "area": "George Town", "hours": 2,
     "desc": "The first English fortress in India, now a museum with colonial-era artefacts."},
    {"id": 3, "name": "Government Museum Egmore", "category": "Sights", "area": "Egmore", "hours": 2,
     "desc": "Famous for its Chola bronzes and a large archaeology collection."},
    {"id": 4, "name": "Kapaleeshwarar Temple", "category": "Temple", "area": "Mylapore", "hours": 1.5,
     "desc": "A Dravidian-style Shiva temple with a colourful gopuram and a lively temple tank."},
    {"id": 5, "name": "Santhome Cathedral Basilica", "category": "Temple", "area": "Mylapore", "hours": 1,
     "desc": "A neo-Gothic church built over the tomb of St. Thomas the Apostle."},
    {"id": 6, "name": "Valluvar Kottam", "category": "Sights", "area": "Nungambakkam", "hours": 1,
     "desc": "A monument shaped like a temple chariot, dedicated to the poet Thiruvalluvar."},
    {"id": 7, "name": "Elliot's Beach (Besant Nagar)", "category": "Beach", "area": "Besant Nagar", "hours": 2,
     "desc": "A calmer beach with cafes nearby. Pair it with Ashtalakshmi Temple."},
    {"id": 8, "name": "Kalakshetra Foundation", "category": "Culture", "area": "Thiruvanmiyur", "hours": 2,
     "desc": "A renowned Bharatanatyam and Carnatic arts institution set in a peaceful campus."},
    {"id": 9, "name": "DakshinaChitra Heritage Museum", "category": "Culture", "area": "ECR", "hours": 3,
     "desc": "A living-history museum of South Indian homes, crafts and performing arts."},
    {"id": 10, "name": "Murugan Idli Shop T Nagar", "category": "Food", "area": "T Nagar", "hours": 1,
     "desc": "Soft idlis with a variety of chutneys and podi. A classic breakfast stop."},
    {"id": 11, "name": "Ratna Cafe Triplicane", "category": "Food", "area": "Triplicane", "hours": 1,
     "desc": "Legendary for its sambar idli, a Chennai institution since 1948."},
    {"id": 12, "name": "Buhari Hotel Anna Salai", "category": "Food", "area": "Anna Salai", "hours": 1,
     "desc": "Famous for Chicken 65, biryani and Chennai-style non-veg meals."},
    {"id": 13, "name": "Mylapore Filter Coffee", "category": "Food", "area": "Mylapore", "hours": 0.5,
     "desc": "Stop at any local tiffin spot in Mylapore for authentic filter kaapi."},
]

CULTURE = [
    {"title": "Margazhi Music & Dance Season", "when": "Mid-Dec to Jan",
     "text": "Hundreds of Carnatic concerts and Bharatanatyam shows across the city."},
    {"title": "Pongal", "when": "January",
     "text": "The harvest festival, with kolam art, sweet pongal and bull-taming traditions."},
    {"title": "Panguni Uthiram / Arupathu Moovar", "when": "March-April",
     "text": "Colourful temple processions at Mylapore's Kapaleeshwarar Temple."},
    {"title": "Chennai Sangamam", "when": "January",
     "text": "A folk arts festival with street performances such as Karagattam and Parai."},
    {"title": "Etiquette tips", "when": "Always",
     "text": "Dress modestly at temples, remove footwear, and eat with your right hand at traditional meals."},
]


def map_link(name):
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(name + ' Chennai')}"


def with_link(p):
    return {**p, "map_url": map_link(p["name"])}


def route_link(stops):
    q = [quote_plus(s["name"] + " Chennai") for s in stops]
    url = f"https://www.google.com/maps/dir/?api=1&origin={q[0]}&destination={q[-1]}"
    if len(q) > 2:
        url += "&waypoints=" + "%7C".join(q[1:-1])
    return url


@app.get("/api/places")
def places():
    cat = request.args.get("category")
    data = [with_link(p) for p in PLACES if not cat or p["category"] == cat]
    return jsonify(data)


@app.get("/api/culture")
def culture():
    return jsonify(CULTURE)


@app.post("/api/itinerary")
def itinerary():
    body = request.get_json(force=True)
    ids = set(body.get("ids", []))
    days = max(1, int(body.get("days", 1)))
    chosen = sorted((p for p in PLACES if p["id"] in ids), key=lambda p: p["area"])
    if not chosen:
        return jsonify([])
    per_day = ceil(len(chosen) / days)  # grouping by area keeps nearby stops together
    plan = []
    for i in range(0, len(chosen), per_day):
        stops = chosen[i:i + per_day]
        plan.append({
            "day": len(plan) + 1,
            "total_hours": sum(s["hours"] for s in stops),
            "stops": [with_link(s) for s in stops],
            "route_url": route_link(stops),
        })
    return jsonify(plan)


if __name__ == "__main__":
    app.run(debug=True, port=5000)