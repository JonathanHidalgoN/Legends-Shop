import {
  APICartItemResponse,
  APIOrderResponse,
  APIOrderSummaryResponse,
  APIProfileInfoResponse,
  APIUserInfoResponse,
  APICommentResponse,
  APIReviewResponse,
  APIItemResponse,
} from "./interfaces/APIResponse";
import { Item } from "./interfaces/Item";
import { CartItem, Order, OrderSummary } from "./interfaces/Order";
import { ProfileInfo, UserInfo } from "./interfaces/profileInterfaces";
import { Comment, Review } from "./interfaces/Review";
import { StatKind, EffectKind } from "./interfaces/Item";

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
    locationId: apiUser.locationId,
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
    reviewed: apiOrder.reviewed,
    location_id: apiOrder.location_id,
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

export function mapAPICommentResponseToComment(
  apiComment: APICommentResponse,
): Comment {
  return {
    id: apiComment.id,
    reviewId: apiComment.reviewId,
    userId: apiComment.userId,
    content: apiComment.content,
    createdAt: new Date(apiComment.createdAt),
    updatedAt: new Date(apiComment.updatedAt),
  };
}

export function mapAPIReviewResponseToReview(
  apiReview: APIReviewResponse,
): Review {
  return {
    id: apiReview.id,
    orderId: apiReview.orderId,
    itemId: apiReview.itemId,
    rating: apiReview.rating,
    createdAt: new Date(apiReview.createdAt),
    updatedAt: new Date(apiReview.updatedAt),
    comments: apiReview.comments.map(mapAPICommentResponseToComment),
  };
}

export function mapAPIItemResponseToItem(apiItem: APIItemResponse): Item {
  return {
    name: apiItem.name,
    gold: {
      base: apiItem.gold.base,
      purchaseable: apiItem.gold.purchasable,
      total: apiItem.gold.total,
      sell: apiItem.gold.sell,
    },
    description: apiItem.description,
    stats: apiItem.stats.map((stat) => ({
      name: stat.name,
      kind: stat.kind === "flat" ? StatKind.Flat : StatKind.Percentage,
      value: stat.value,
    })),
    tags: apiItem.tags,
    effects: Object.entries(apiItem.effect).map(([name, value]) => ({
      name,
      value,
      kind: EffectKind.effect1,
    })),
    img: apiItem.imageUrl,
    id: apiItem.id,
  };
}
