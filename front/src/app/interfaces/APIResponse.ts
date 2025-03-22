import { Order, OrderStatus, OrderSummary } from "./Order";

export enum SingupError {
  USERNAMEEXIST = "USERNAMEEXIST",
  EMAILEXIST = "EMAILEXIST",
  INVALIDEMAIL = "INVALIDEMAIL",
  INVALIDDATE = "INVALIDDATE",
  INVALIDUSERNAME = "INVALIDUSERNAME",
  INVALIDUSERGOLD = "INVALIDUSERGOLD",
  INTERNALSERVERERROR = "INTERNALSERVERERROR",
  INVALIDPASSWORD = "INVALIDPASSWORD",
}

export enum LoginError {
  INVALIDUSERNAME = "INVALIDUSERNAME",
  INVALIDPASSWORD = "INVALIDPASSWORD",
  INCORRECTCREDENTIALS = "INCORRECTCREDENTIALS",
  INTERNALSERVERERROR = "INTERNALSERVERERROR",
}

export interface APISingupResponse {
  status: number;
  errorType: SingupError | null;
  message: string;
}

export interface APILoginResponse {
  status: number;
  errorType: LoginError | null;
  message: string;
}

export interface APIOrderResponse {
  id: number;
  status: OrderStatus;
  itemNames: string[];
  total: number;
  userName: string;
  orderDate: string;
  deliveryDate: string;
}

export class APIError extends Error {
  public status: number;
  public data?: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = "APIError";
    this.status = status;
    this.data = data;
  }
}

export function mapAPIOrderResponseToOrder(apiOrder: APIOrderResponse): Order {
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
