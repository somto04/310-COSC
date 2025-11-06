import json
import os

# Get the folder where this script is located
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "replies.json")

print(f"Looking for file at: {file_path}")

# Load existing data
with open(file_path, "r") as f:
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
with open(file_path, "w") as f:
    json.dump(data, f, indent=2)

print("IDs updated successfully.")
