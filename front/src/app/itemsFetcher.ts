import { GetStaticProps } from "next";
import { Gold, Item } from "./interfaces/Item";
import { BACKEND_PORT, BACKEND_HOST } from "./envVariables";

function parseGoldNodeIntoGold(goldNode: Record<string, any>): Gold {
  const isBaseNumber: boolean = typeof goldNode.base === "number"
  const isPurchaseableBoolean: boolean = typeof goldNode.purchaseable === "boolean"
  const isTotalNumber: boolean = typeof goldNode.total === "number"
  const isSellNumber: boolean = typeof goldNode.sell === "number"
  return {
    base: goldNode.base,
    purchaseable: goldNode.boolean,
    total: goldNode.total,
    sell: goldNode.sell
  }
}

function parseItemNodeIntoItem(itemNode: Record<string, any>): Item {
  if ("gold" in itemNode === false) {
  }
  const tags: string[] = itemNode.tags ?? [];
  const gold: Gold = parseGoldNodeIntoGold(itemNode.gold)

}

export async function fetchItems() {
  const res = await fetch(`http://${BACKEND_HOST}:${BACKEND_PORT}/items/all`);
  const itemsJson = await res.json();
  if ("items" in itemsJson) {
    const itemsNode = itemsJson.items
    let items: Item[] = [];
    for (const item in items) {
    }
    return itemsJson
  }
  else {
    // error
  }
}
