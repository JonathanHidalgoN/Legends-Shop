import {
  allItemsRequest,
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

const MAX_RETRIES = 3;
const RETRY_DELAY = 2000; // 2 seconds

async function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function retryOperation<T>(
  operation: () => Promise<T>,
  name: string,
  retries = MAX_RETRIES,
): Promise<T> {
  try {
    return await operation();
  } catch (error) {
    if (retries > 0) {
      console.warn(
        `Failed to fetch ${name}, retrying... (${retries} attempts left)`,
      );
      await delay(RETRY_DELAY);
      return retryOperation(operation, name, retries - 1);
    }
    throw new Error(
      `Failed to fetch ${name} after ${MAX_RETRIES} attempts: ${error}`,
    );
  }
}

export async function loadStaticData(dowloadHDImages: boolean = false) {
  let items: Item[] = [];
  let tags: string[] = [];
  let effects: string[] = [];
  let locations: Location[] = [];

  try {
    // Load all data with retries
    items = (
      await retryOperation(() => allItemsRequest(FromValues.SERVER), "items")
    ).map(mapAPIItemResponseToItem);

    tags = await retryOperation(() => allTagsRequet(FromValues.SERVER), "tags");

    effects = await retryOperation(
      () => getAllEffectNamesRequest(FromValues.SERVER),
      "effects",
    );

    locations = await retryOperation(
      () => getAllLocationsRequest(FromValues.SERVER),
      "locations",
    );

    // Validate required data
    if (!items.length) {
      throw new Error("No items received from server");
    }
    if (!locations.length) {
      throw new Error("No locations received from server");
    }

    if (dowloadHDImages) {
      try {
        const itemNames: string[] = items.map((item: Item) => item.name);
        await getHDItemImages(itemNames);
      } catch (error) {
        console.error("Error updating HD images for items:", error);
        // Don't throw here, as HD images are not critical
      }
    }
    items.forEach((item: Item) => {
      const newImgPath = checkIfHDImageAvailable(item.name, item.img);
      item.img = newImgPath;
      item.hasHdImage = newImgPath.startsWith("/hd_images/");
    });
  } catch (error) {
    console.error("Static data loading failed:", error);
    throw new Error(
      `Failed to load required static data: ${error instanceof Error ? error.message : String(error)}`,
    );
  }

  return { items, tags, effects, locations };
}
