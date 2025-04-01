import {
  APICartItemResponse,
  APIOrderResponse,
  APIOrderSummaryResponse,
  APIProfileInfoResponse,
  APIUserInfoResponse,
} from "./interfaces/APIResponse";
import { Item } from "./interfaces/Item";
import { CartItem, Order, OrderSummary } from "./interfaces/Order";
import { ProfileInfo, UserInfo } from "./interfaces/profileInterfaces";

export function mapAPIOrderSummaryToOrderSummary(
  apiOrderSummary: APIOrderSummaryResponse,
): OrderSummary {
  return {
    itemName: apiOrderSummary.itemName,
    basePrice: apiOrderSummary.basePrice,
    timesOrdered: apiOrderSummary.timesOrdered,
    totalSpend: apiOrderSummary.totalSpend,
    orderDates: apiOrderSummary.orderDates.map((dateStr) => new Date(dateStr)),
  };
}

export function mapAPIUserInfoToUserInDB(
  apiUser: APIUserInfoResponse,
): UserInfo {
  return {
    userName: apiUser.userName,
    email: apiUser.email,
    created: new Date(apiUser.created),
    lastSingIn: new Date(apiUser.lastSingIn),
    goldSpend: apiUser.goldSpend,
    currentGold: apiUser.currentGold,
    birthDate: new Date(apiUser.birthDate),
    locationId: apiUser.locationId
  };
}

export function mapAPIProfileInfoResponseToProfileInfo(
  apiProfile: APIProfileInfoResponse,
): ProfileInfo {
  return {
    user: mapAPIUserInfoToUserInDB(apiProfile.user),
    ordersInfo: apiProfile.ordersInfo.map((apiOrderSummary) =>
      mapAPIOrderSummaryToOrderSummary(apiOrderSummary),
    ),
  };
}

export function mapAPIOrderResponseToOrder(apiOrder: APIOrderResponse): Order {
  return {
    id: apiOrder.id,
    status: apiOrder.status,
    itemNames: apiOrder.itemNames,
    total: apiOrder.total,
    userName: apiOrder.userName,
    orderDate: new Date(apiOrder.orderDate),
    deliveryDate: new Date(apiOrder.deliveryDate),
  };
}

export function mapAPICartItemResponseToCartItem(
  apiCartItem: APICartItemResponse,
  item: Item,
): CartItem {
  return {
    id: apiCartItem.id,
    status: apiCartItem.status,
    item: item,
  };
}

export function mapCartItemToAPICartItemResponse(
  cartItem: CartItem,
): APICartItemResponse {
  return {
    id: null,
    status: cartItem.status,
    itemId: cartItem.item.id,
  };
}
