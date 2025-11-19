import json, os

DATA_PATH = "app/data/replies.json"

def loadAll():

    #load all replies from the JSON file
    if not os.path.exists(DATA_PATH):
        return []       
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
    
def saveAll(replies):
    if not os.path.exists(os.path.dirname(DATA_PATH)):
        
        return False

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(replies, f, indent=2, ensure_ascii=False)

    return True
