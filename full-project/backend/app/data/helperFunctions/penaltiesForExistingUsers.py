
import json
import os

baseDir = os.path.dirname(__file__)
path = os.path.join(baseDir, "users.json")

with open(path, "r", encoding="utf-8") as f:
    users = json.load(f)

modified = False
for u in users:
    if "penaltyCount" not in u:
        u["penaltyCount"] = 0
        modified = True
    if "isBanned" not in u:
        u["isBanned"] = False
        modified = True

if modified:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)
    print("users.json updated with penaltyCount and isBanned")
else:
    print("No migration needed")
