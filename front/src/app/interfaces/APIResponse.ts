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

export interface APIOrderSummaryResponse {
  itemName: string;
  basePrice: number;
  timesOrdered: number;
  totalSpend: number;
  orderDates: string[];
}

export interface APIUserInfoResponse {
  userName: string;
  email: string;
  created: string;
  lastSingIn: string;
  goldSpend: number;
  currentGold: number;
  birthDate: string;
}

export interface APIProfileInfoResponse {
  user: APIUserInfoResponse;
  ordersInfo: APIOrderSummaryResponse[];
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

