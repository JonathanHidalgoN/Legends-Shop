import { CartStatus, Order, OrderStatus, OrderSummary } from "./Order";
import { Comment, Review } from "./Review";

export enum SingupError {
  USERNAMEEXIST = "USERNAMEEXIST",
  EMAILEXIST = "EMAILEXIST",
  INVALIDEMAIL = "INVALIDEMAIL",
  INVALIDDATE = "INVALIDDATE",
  INVALIDUSERNAME = "INVALIDUSERNAME",
  INVALIDUSERGOLD = "INVALIDUSERGOLD",
  INTERNALSERVERERROR = "INTERNALSERVERERROR",
  INVALIDPASSWORD = "INVALIDPASSWORD",
  INVALIDLOCATION = "INVALIDLOCATION",
}

export enum LoginError {
  INVALIDUSERNAME = "INVALIDUSERNAME",
  INVALIDPASSWORD = "INVALIDPASSWORD",
  INCORRECTCREDENTIALS = "INCORRECTCREDENTIALS",
  INTERNALSERVERERROR = "INTERNALSERVERERROR",
  CURRENTGOLDERROR = "CURRENTGOLDERROR",
  CURRENTCARTITEMSERROR = "CURRENTCARTITEMSERROR",
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
  reviewed: boolean;
  location_id: number;
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
  locationId: number;
}

export interface APICartItemResponse {
  id: number | null;
  status: CartStatus;
  itemId: number;
}

export interface APIProfileInfoResponse {
  user: APIUserInfoResponse;
  ordersInfo: APIOrderSummaryResponse[];
}

export interface APICommentResponse {
  id: number;
  reviewId: number;
  userId: number;
  content: string;
  createdAt: string;
  updatedAt: string;
}

export interface APIReviewResponse {
  id: number;
  orderId: number;
  itemId: number;
  rating: number;
  createdAt: string;
  updatedAt: string;
  comments: APICommentResponse[];
}

export interface APIItemResponse {
  name: string;
  plaintext: string;
  image: string;
  imageUrl: string;
  gold: {
    base: number;
    purchasable: boolean;
    total: number;
    sell: number;
  };
  tags: string[];
  stats: {
    name: string;
    kind: "flat" | "percentage";
    value: number;
  }[];
  effect: Record<string, number>;
  id: number;
  description: string;
}

export class APIError extends Error {
  public status: number;
  public data?: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    // When you inline the error-handling in getUserReviewsRequest, you’re throwing an error that’s immediately caught by SWR and available in your custom hook. When you extract that logic into a separate function (checkResponse), the thrown error is essentially the same. But if the custom error isn’t recognized as an instance of APIError due to the prototype issue, then your redirect logic (or any conditional handling in your effect) might not work as expected.
    Object.setPrototypeOf(this, APIError.prototype); // Ensures proper prototype chain
    this.name = "APIError";
    this.status = status;
    this.data = data;
  }
}
