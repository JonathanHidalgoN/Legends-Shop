import { Item } from "./Item";

export enum OrderStatus {
  SHIPPED = "SHIPPED",
  PENDING = "PENDING",
  DELIVERED = "DELIVERED",
  CANCELED = "CANCELED",
  ALL = "ALL"
}

export enum CartStatus {
  ADDED = "ADDED",
  DELETED = "DELETED",
  ORDERED = "ORDERED",
  PENDING = "PENDING"
}

export interface CartItem {
  id: number | null;
  status: CartStatus;
  item: Item
}

export enum FilterSortField {
  PRICE = "Price",
  ORDERDATE = "Order date",
  DELIVERYDATE = "Deliver date",
  QUANTITY = "Quantity"
}

export enum FilterSortOrder {
  ASC = "asc",
  DESC = "desc"
}

export interface Order {
  id: number;
  status: OrderStatus;
  itemNames: string[];
  total: number;
  userName: string;
  orderDate: Date;
  deliveryDate: Date;
}

export interface OrderSummary {
  itemName: string;
  basePrice: number;
  timesOrdered: number;
  totalSpend: number;
  orderDates: Date[];
}

export interface OptionType {
  value: string;
  label: string;
}
