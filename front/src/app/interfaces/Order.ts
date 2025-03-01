import { Item } from "./Item";

export interface OrderItem {
  name: string,
  cost: number
}

export interface Order {
  id: number,
  status: string
  items: OrderItem[],
  total: number,
  userName: string,
  date: Date
}

export default function mapItemToOrderItem(item: Item): OrderItem {
  return {
    name: item.name,
    cost: item.gold.base
  };
}
