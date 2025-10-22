import json, os

DATA_PATH = os.path.join(os.path.dirname(__file__), "users.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    users = json.load(f)

# loop through and add missing fields if not present
for user in users:
    user.setdefault("firstName", "")
    user.setdefault("lastName", "")
    user.setdefault("age", None)
    user.setdefault("email", "")
    user.setdefault("pw", "")
    user.setdefault("role", "user")
    # username and id already exist

with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(users, f, indent=2)

print(f"Updated {len(users)} users with new schema fields!")
