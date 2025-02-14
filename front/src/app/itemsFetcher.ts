import { GetStaticProps } from "next";
import { Item } from "./interfaces/Item";
import { BACKEND_PORT, BACKEND_HOST } from "./envVariables";

export async function fetchItems() {
  const res = await fetch(`http://${BACKEND_HOST}:${BACKEND_PORT}/items/all`)
  const itemsJson = await res.json()
  return itemsJson
}
