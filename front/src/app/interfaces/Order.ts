export enum OrderStatus {
  PENDING = "PENDING",
  SHIPPED = "SHIPPED",
  DELIVERED = "DELIVERED",
  CANCELED = "CANCELED",
  ALL = "ALL"
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

export interface APIOrder {
  id: number;
  status: OrderStatus;
  itemNames: string[];
  total: number;
  userName: string;
  orderDate: string;
  deliveryDate: string;
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

export function mapAPIOrderToOrder(apiOrder: APIOrder): Order {
  return {
    id: apiOrder.id,
    status: apiOrder.status,
    itemNames: apiOrder.itemNames,
    total: apiOrder.total,
    userName: apiOrder.userName,
    orderDate: new Date(apiOrder.orderDate),
    deliveryDate: new Date(apiOrder.deliveryDate)
  }
}
