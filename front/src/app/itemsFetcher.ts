//TODO: CHANGE NAME TO ITEMFUNCTIONS
import {
  Effect,
  EffectKind,
  Gold,
  Item,
  Stat,
  StatKind,
} from "./interfaces/Item";
import {
  EffectsNode,
  GoldNode,
  ItemNode,
  StatNode,
} from "./interfaces/ItemRequest";
import { allTagsRequet, someItemsRequest } from "./request";

/**
 * Parses a JSON node into a Gold object.
 *
 * @param goldNode - The JSON object representing gold data.
 * @returns A Gold object containing base, purchaseable, total, and sell values.
 */
function parseGoldNodeIntoGold(goldNode: GoldNode): Gold {
  return {
    base: goldNode.base,
    purchaseable: goldNode.boolean,
    total: goldNode.total,
    sell: goldNode.sell,
  };
}

/**
 * Parses an array of JSON nodes into an array of Stat objects.
 *
 * @param statsNode - The array of JSON objects representing stat data.
 * @returns An array of Stat objects.
 */
function parseStatNodeIntoStats(statsNodes: StatNode[]): Stat[] {
  return statsNodes.map((statNode) => ({
    name: statNode.name,
    kind: statNode.kind === "flat" ? StatKind.Flat : StatKind.Percentage,
    value: statNode.value,
  }));
}

/**
 * Parses a JSON object containing effect properties into an array of Effect objects.
 *
 * @param effectsNode - The JSON object where keys are effect names and values are effect values.
 * @returns An array of Effect objects.
 */
function parseEffectsNodeIntoEffects(effectsNode: EffectsNode): Effect[] {
  const effects: Effect[] = [];
  for (const key in effectsNode) {
    if (Object.prototype.hasOwnProperty.call(effectsNode, key)) {
      effects.push({
        name: key,
        value: effectsNode[key],
        // TODO: change this to take effects
        kind: EffectKind.effect1,
      });
    }
  }
  return effects;
}

/**
 * Parses an item JSON node into an Item object.
 *
 * @param itemNode - The JSON object representing an item.
 * @returns An Item object.
 */
function parseItemNodeIntoItem(itemNode: ItemNode): Item {
  const tags: string[] = itemNode.tags ?? [];
  const gold: Gold = parseGoldNodeIntoGold(itemNode.gold);
  const effects: Effect[] = parseEffectsNodeIntoEffects(itemNode.effect);
  const stats: Stat[] = parseStatNodeIntoStats(itemNode.stats);

  return {
    name: itemNode.name,
    gold: gold,
    description: itemNode.description,
    stats: stats,
    tags: tags,
    effects: effects,
    img: itemNode.imageUrl,
    id: itemNode.id,
  };
}

/**
 * Fetches items from the backend and parses the response into an array of Item objects.
 *
 * @returns A promise that resolves to an array of Item objects.
 * @throws An error if the fetch fails or the response format is invalid.
 */
export async function fetchItems(): Promise<Item[]> {
  const response = await someItemsRequest();
  if (!response.ok) {
    throw new Error(
      `Failed to fetch items: ${response.status} ${response.statusText}`,
    );
  }
  const itemsJson = await response.json();
  if (!("items" in itemsJson) || !Array.isArray(itemsJson.items)) {
    throw new Error("Invalid response format: expected an 'items' array");
  }
  const items: Item[] = itemsJson.items.map(parseItemNodeIntoItem);
  return items;
}

export async function fetchTags(): Promise<string[]> {
  const response = await allTagsRequet();
  if (!response.ok) {
    throw new Error(
      `Failed to fetch unique tags: ${response.status} ${response.statusText}`,
    );
  }
  const tagsJson = await response.json();
  if (!("tagNames" in tagsJson) || !Array.isArray(tagsJson.tagNames)) {
    throw new Error("Invalid response format: expected an 'tagNames' array");
  }
  return tagsJson.tagNames;
}
