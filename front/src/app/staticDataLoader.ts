import {
  allTagsRequet,
  FromValues,
  getAllEffectNamesRequest,
  getAllLocationsRequest,
  someItemsRequest,
} from "./request";
import { mapAPIItemResponseToItem } from "./mappers";
import { checkIfHDImageAvailable, getHDItemImages } from "./serverFunctions";
import { Item } from "./interfaces/Item";
import { Location } from "./interfaces/Location";

export async function loadStaticData() {
  let items: Item[] = [];
  let tags: string[] = [];
  let effects: string[] = [];
  let locations: Location[] = [];
  try {
    items = (await someItemsRequest(FromValues.SERVER)).map(
      mapAPIItemResponseToItem,
    );
    tags = await allTagsRequet(FromValues.SERVER);
    effects = await getAllEffectNamesRequest(FromValues.SERVER);
    locations = await getAllLocationsRequest(FromValues.SERVER);

    try {
      const itemNames: string[] = items.map((item: Item) => item.name);
      await getHDItemImages(itemNames);
      items.forEach((item: Item) => {
        item.img = checkIfHDImageAvailable(item.name, item.img);
      });
    } catch (error) {
      console.error("Error updating HD images for items:", error);
    }
  } catch (error) {
    throw new Error("Data fetching error in loadStaticData");
  }
  return { items, tags, effects, locations };
} 