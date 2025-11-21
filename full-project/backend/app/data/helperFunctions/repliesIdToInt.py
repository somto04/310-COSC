import json
import os

# Get the folder where this script is located
baseDir = os.path.dirname(os.path.abspath(__file__))
filePath = os.path.join(baseDir, "replies.json")

print(f"Looking for file at: {filePath}")

# Load existing data
with open(filePath, "r") as f:
    data = json.load(f)

# Convert ID fields to ints
for reply in data:
    try:
        reply["id"] = int(reply["id"])
        reply["reviewId"] = int(reply["reviewId"])
        reply["userId"] = int(reply["userId"])
    except ValueError:
        print(f"Skipped one due to invalid ID format: {reply}")

# Save the updated data
with open(filePath, "w") as f:
    json.dump(data, f, indent=2)

print("IDs updated successfully.")
