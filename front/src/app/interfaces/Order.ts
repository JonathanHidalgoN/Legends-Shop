import { Item } from "./Item";

export interface OrderItem {
  name: string,
  cost: number
}

export interface Order {
  id: number,
  status: string
  items: Item[],
  total: number,
  userName: string,
  date: Date
}
