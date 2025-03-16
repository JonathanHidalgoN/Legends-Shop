export enum OrderStatus {
  PENDING = "PENDING",
  SHIPPED = "SHIPPED",
  DELIVERED = "DELIVERED",
  CANCELED = "CANCELED",
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
