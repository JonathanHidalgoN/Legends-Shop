import urllib.request
import json


class ItemsLoader:
    ITEMS_URL: str = (
        "https://ddragon.leagueoflegends.com/cdn/15.2.1/data/en_US/item.json"
    )

    def __init__(self, load: bool = False, updated: bool = False):
        self.load = load
        self.updated = updated

    # This method gets the raw json from the API and updates a flag
    # if no errors
    def getRawJson(self) -> str | None:
        try:
            response = urllib.request.urlopen(self.ITEMS_URL)
            data = json.loads(response.read().decode())
            self.updated = True
            return data
        except json.JSONDecodeError as e:
            self.updated = False
            print(f"JSON Decode Error getting the items json: {e.msg}")
        except Exception as e:
            self.updated = False
            print(f"An error occurred getting the items json: {e}")
        return None
