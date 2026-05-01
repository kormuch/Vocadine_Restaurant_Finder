"""
Quick test: dump all fields from a Places API response.
Run: python test_api_fields.py
"""
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GOOGLE_PLACES_KEY")

resp = requests.post(
    "https://places.googleapis.com/v1/places:searchText",
    headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": "*",
    },
    json={"textQuery": "Italian restaurant Berlin", "languageCode": "en"},
    timeout=10,
)

data = resp.json()
places = data.get("places", [])

if not places:
    print("No results.")
else:
    place = places[0]
    print(f"=== Fields for: {place.get('displayName', {}).get('text', '?')} ===\n")
    print(json.dumps(place, indent=2, ensure_ascii=False))

    # Highlight review-related fields specifically
    print("\n=== Review-related keys ===")
    for key in place:
        if "review" in key.lower() or "rating" in key.lower():
            print(f"  {key}: {place[key]}")
