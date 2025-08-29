import os
import json

# Path to images folder
IMAGE_DIR = "images"
OUTPUT_FILE = "images.json"

images = []

for file in os.listdir(IMAGE_DIR):
    if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
        images.append({
            "url": f"{IMAGE_DIR}/{file}",
            "caption": os.path.splitext(file)[0].replace("_", " ").title()
        })

# Write to JSON file
with open(OUTPUT_FILE, "w") as f:
    json.dump({"images": images}, f, indent=4)

print(f"{OUTPUT_FILE} generated with {len(images)} images.")
