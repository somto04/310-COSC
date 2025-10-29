import json, os

DATA_PATH = "app/data/replies.json"

def loadAll():

    #load all replies from the JSON file
    if not os.path.exists(DATA_PATH):
        return []       
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
    
def saveAll(replies):
    #save all replies to the JSON file
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(replies, f, indent=2,)