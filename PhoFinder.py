#!/usr/bin/env python3
"""
Pho Finder - Robust version that works for any city (including Chicago)
"""

import argparse
import requests

# ============================================================
# 🔑 PASTE YOUR GEOAPIFY API KEY HERE
# ============================================================
GEOAPIFY_API_KEY = "YOUR_GEOAPIFY_API_KEY"   # <-- Replace this
# ============================================================

def find_pho_restaurants(location, radius_meters=10000, limit=15):
    """Find Vietnamese restaurants using Geoapify Places API."""
    
    # Step 1: Geocode the location
    geocode_url = "https://api.geoapify.com/v1/geocode/search"
    geo_params = {
        "text": location,
        "apiKey": GEOAPIFY_API_KEY,
        "format": "json",
        "limit": 1,
    }
    try:
        print(f"🌍 Geocoding '{location}'...")
        resp = requests.get(geocode_url, params=geo_params)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("results"):
            print(f"❌ Could not find location '{location}'")
            return []
        lat = data["results"][0]["lat"]
        lon = data["results"][0]["lon"]
        print(f"📍 Coordinates: {lat:.4f}, {lon:.4f}")
    except Exception as e:
        print(f"Geocoding error: {e}")
        return []
    
    # Step 2: Search for restaurants (broad category)
    places_url = "https://api.geoapify.com/v2/places"
    place_params = {
        "categories": "catering.restaurant",
        "filter": f"circle:{lon},{lat},{radius_meters}",
        "bias": f"proximity:{lon},{lat}",
        "limit": limit * 3,  # get extra to allow filtering
        "apiKey": GEOAPIFY_API_KEY,
    }
    try:
        print(f"🍜 Searching for restaurants within {radius_meters/1000} km...")
        resp = requests.get(places_url, params=place_params)
        resp.raise_for_status()
        places = resp.json()
    except Exception as e:
        print(f"Places API error: {e}")
        return []
    
    # Step 3: Filter for Vietnamese/pho
    keywords = ["pho", "viet", "vietnamese", "saigon", "noodle", "com", "banh"]
    results = []
    raw_names = []  # for debugging
    
    for feature in places.get("features", []):
        props = feature.get("properties", {})
        name = props.get("name", "")
        if not name:
            continue
        raw_names.append(name)
        
        name_lower = name.lower()
        categories = str(props.get("categories", [])).lower()
        
        # Match if any keyword in name or categories
        if any(k in name_lower for k in keywords) or "vietnamese" in categories:
            results.append({
                "name": name,
                "address": props.get("formatted", "N/A"),
                "phone": props.get("contact", {}).get("phone", "N/A"),
                "rating": props.get("rating", "N/A"),
            })
            if len(results) >= limit:
                break
    
    # Debug: show what we found
    print(f"\n🔎 Raw restaurant names sampled (first 10):")
    for i, n in enumerate(raw_names[:10], 1):
        print(f"   {i}. {n}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Find pho restaurants anywhere")
    parser.add_argument("location", help="City, state, or country")
    parser.add_argument("--radius", type=int, default=10000, help="Radius in meters (default 10000 = 10km)")
    parser.add_argument("--limit", type=int, default=15, help="Max results")
    args = parser.parse_args()
    
    if GEOAPIFY_API_KEY == "YOUR_GEOAPIFY_API_KEY":
        print("❌ Please edit the script and paste your Geoapify API key.")
        return
    
    restaurants = find_pho_restaurants(args.location, args.radius, args.limit)
    
    if not restaurants:
        print(f"\n🍜 No Vietnamese restaurants found near '{args.location}'.")
        print("   Try increasing radius: --radius 20000")
    else:
        print(f"\n✅ Found {len(restaurants)} Vietnamese/pho restaurant(s):\n")
        for i, r in enumerate(restaurants, 1):
            print(f"{i}. {r['name']}")
            print(f"   📍 {r['address']}")
            if r['phone'] != "N/A":
                print(f"   📞 {r['phone']}")
            if r['rating'] != "N/A":
                print(f"   ⭐ Rating: {r['rating']}")
            print()

if __name__ == "__main__":
    main()
  
