import { SERVER_DOMAIN, CLIENT_DOMAIN } from "./envVariables";
import {
  APICartItemResponse,
  APIError,
  APIProfileInfoResponse,
  APIReviewResponse,
} from "./interfaces/APIResponse";
import { Order } from "./interfaces/Order";
import { APIOrderResponse } from "./interfaces/APIResponse";
import { Location } from "./interfaces/Location";
import { DeliveryDate } from "./interfaces/DeliveryDate";
import { showErrorToast } from "./customToast";
import { Review } from "./interfaces/Review";
import { APIItemResponse } from "./interfaces/APIResponse";

//TODO: how to improve this solution?
export const ENDPOINT_LOGIN: string = `auth/token`;
export const ENDPOINT_SINGUP: string = `auth/singup`;
export const ENDPOINT_REFRESH_TOKEN: string = `auth/refresh_token`;
export const ENDPOINT_LOGIN_OUT: string = `auth/logout`;
export const ENDPOINT_ITEMS_ALL: string = `items/all`;
export const ENDPOINT_SOME_ITEMS: string = `items/some`;
export const ENDPOINT_ALL_TAGS: string = `items/uniqueTags`;
export const ENDPOINT_ALL_ITEM_NAMES: string = `items/item_names`;
export const ENDPOINT_ALL_EFFECT_NAMES: string = `items/unique_effects`;
export const ENDPOINT_ALL_LOCATIONS: string = `locations/all`;
export const ENDPOINT_ORDER: string = `orders/order`;
export const ENDPOINT_ORDER_HISTORY: string = `orders/order_history`;
export const ENDPOINT_ORDER_CANCEL: string = `orders/cancel_order`;
export const ENDPOINT_PROFILE_CURRENT_GOLD: string = `profile/current_gold`;
export const ENDPOINT_PROFILE_INFO: string = `profile/info`;
export const ENDPOINT_CART_ADD_ITEM: string = `cart/add_item`;
export const ENDPOINT_CART_ADDED_CART_ITEMS: string = `cart/added_cart_items`;
export const ENDPOINT_CART_DELETE_ITEM: string = `cart/delete_cart_item`;
export const ENDPOINT_UPDATE_ITEMS: string = `/updateItems`;
export const ENDPOINT_USER_LOCATION: string = `locations/user`;
export const ENDPOINT_DELIVERY_DATES: string = `delivery_dates/dates`;
export const ENDPOINT_REVIEW: string = `review/add`;
export const ENDPOINT_UPDATE_REVIEW: string = `review/update`;
export const ENDPOINT_USER_REVIEWS: string = `review/user`;
export const ENDPOINT_ITEM_REVIEWS: string = `review/item`;
export const ENDPOINT_CHAMPION_ICONS: string = `api/icons`;

export enum FromValues {
  CLIENT = "CLIENT",
  SERVER = "SERVER",
}

function makeUrl(from: FromValues, endpoint: string): string {
  let url: string;
  if (from === FromValues.SERVER) {
    url = SERVER_DOMAIN + endpoint;
  } else {
    url = CLIENT_DOMAIN + endpoint;
  }
  return url;
}

export async function createAPIError(response: Response): Promise<APIError> {
  if (response.status == 401) {
    return new APIError("Unauthorized", 401);
  } else {
    const data = await response.json();
    return new APIError(data?.message || "Error", response.status, data);
  }
}

async function throwAPIError(response: Response, from: FromValues) {
  const apiError: APIError = await createAPIError(response);
  if (from === FromValues.CLIENT) showErrorToast(apiError.message);
  throw apiError;
}

async function checkResponse(
  response: Response,
  from: FromValues,
): Promise<void> {
  if (!response.ok) {
    await throwAPIError(response, from);
  }
}

export async function logInRequest(
  userName: string,
  password: string,
  from: FromValues,
) {
  const url: string = makeUrl(from, ENDPOINT_LOGIN);
  const formData = new URLSearchParams();
  formData.append("username", userName);
  formData.append("password", password);
  return await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    credentials: "include",
    body: formData.toString(),
  });
}

export async function singupRequest(
  userName: string,
  password: string,
  email: string,
  birthDate: Date,
  location_id: number,
  from: FromValues,
) {
  const url: string = makeUrl(from, ENDPOINT_SINGUP);
  const formData = new URLSearchParams();
  formData.append("username", userName);
  formData.append("password", password);
  formData.append("email", email);
  formData.append("birthDate", birthDate.toISOString().substring(0, 10));
  formData.append("location_id", location_id.toString());
  return await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData.toString(),
  });
}

export async function refreshTokenRequest(from: FromValues) {
  const url: string = makeUrl(from, ENDPOINT_REFRESH_TOKEN);
  return await fetch(url, {
    credentials: "include",
  });
}

export async function logoutRequest(from: FromValues) {
  const url: string = makeUrl(from, ENDPOINT_LOGIN_OUT);
  return await fetch(url, {
    method: "GET",
    credentials: "include",
  });
}

export async function someItemsRequest(
  from: FromValues,
): Promise<APIItemResponse[]> {
  const url: string = makeUrl(from, ENDPOINT_SOME_ITEMS);
  const response = await fetch(url);
  checkResponse(response, from);
  return await response.json();
}

export async function allTagsRequet(from: FromValues): Promise<string[]> {
  const url: string = makeUrl(from, ENDPOINT_ALL_TAGS);
  const response = await fetch(url);
  checkResponse(response, from);
  return await response.json();
}

export async function allItemsRequest(
  from: FromValues,
): Promise<APIItemResponse[]> {
  const url: string = makeUrl(from, ENDPOINT_ITEMS_ALL);
  const response = await fetch(url);
  checkResponse(response, from);
  return await response.json();
}

export async function orderRequest(
  order: Order,
  from: FromValues,
): Promise<number> {
  const url: string = makeUrl(from, ENDPOINT_ORDER);
  const response = await fetch(url, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(order),
  });
  checkResponse(response, from);
  return await response.json();
}

export async function getOrderHistoryWithCredentialsRequest(
  from: FromValues,
): Promise<APIOrderResponse[]> {
  const url = `${makeUrl(from, ENDPOINT_ORDER_HISTORY)}`;
  const response = await fetch(url, {
    credentials: "include",
  });
  checkResponse(response, from);
  return await response.json();
}

export async function getProfileInfoRequest(
  from: FromValues,
): Promise<APIProfileInfoResponse> {
  const url: string = makeUrl(from, ENDPOINT_PROFILE_INFO);
  const response = await fetch(url, {
    credentials: "include",
  });
  checkResponse(response, from);
  return await response.json();
}

export async function addToCarRequest(
  from: FromValues,
  apiCartItem: APICartItemResponse,
): Promise<APICartItemResponse> {
  const url: string = makeUrl(from, ENDPOINT_CART_ADD_ITEM);
  const response = await fetch(url, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(apiCartItem),
  });

  checkResponse(response, from);
  return await response.json();
}

export async function cancelOrderRequest(
  orderId: number,
  from: FromValues,
): Promise<void> {
  const url: string = makeUrl(from, `${ENDPOINT_ORDER_CANCEL}/${orderId}`);
  const response = await fetch(url, {
    method: "PUT",
    credentials: "include",
  });
  checkResponse(response, from);
}

export async function getCurrentUserGoldRequest(
  from: FromValues,
): Promise<number> {
  const url: string = makeUrl(from, ENDPOINT_PROFILE_CURRENT_GOLD);
  const response = await fetch(url, {
    credentials: "include",
  });
  checkResponse(response, from);
  return await response.json();
}

export async function getAddedCartItemsRequest(
  from: FromValues,
): Promise<APICartItemResponse[]> {
  const url: string = makeUrl(from, ENDPOINT_CART_ADDED_CART_ITEMS);
  const response = await fetch(url, {
    credentials: "include",
  });
  checkResponse(response, from);
  return await response.json();
}

export async function deleteCartItemRequest(
  from: FromValues,
  cartItemId: number,
): Promise<void> {
  const url: string = makeUrl(
    from,
    `${ENDPOINT_CART_DELETE_ITEM}/${cartItemId}`,
  );
  const response = await fetch(url, {
    method: "DELETE",
    credentials: "include",
  });

  checkResponse(response, from);
  return await response.json();
}

export async function updateItemsRequest(from: FromValues): Promise<void> {
  const url: string = makeUrl(from, ENDPOINT_UPDATE_ITEMS);
  const response = await fetch(url, {
    method: "PUT",
  });
  checkResponse(response, from);
}

export async function specialDownloadImagesRequest(
  itemNames: string[],
): Promise<void> {
  const response = await fetch("/api/scrapeImages", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ itemNames }),
  });

  checkResponse(response, FromValues.CLIENT);
}

export async function getAllItemNamesRequest(
  from: FromValues,
): Promise<string[]> {
  const url: string = makeUrl(from, ENDPOINT_ALL_ITEM_NAMES);
  const response = await fetch(url);
  checkResponse(response, from);
  return await response.json();
}

export async function getAllEffectNamesRequest(
  from: FromValues,
): Promise<string[]> {
  const url: string = makeUrl(from, ENDPOINT_ALL_EFFECT_NAMES);
  const response = await fetch(url);
  checkResponse(response, from);
  return await response.json();
}

export async function getAllLocationsRequest(
  from: FromValues,
): Promise<Location[]> {
  const url: string = makeUrl(from, ENDPOINT_ALL_LOCATIONS);
  const response = await fetch(url);
  checkResponse(response, from);
  return await response.json();
}

export async function getUserLocationRequest(
  from: FromValues,
): Promise<Location> {
  const url: string = makeUrl(from, ENDPOINT_USER_LOCATION);
  const response = await fetch(url, {
    credentials: "include",
  });
  checkResponse(response, from);
  return await response.json();
}

export async function getDeliveryDatesRequest(
  locationId: number,
  from: FromValues,
): Promise<DeliveryDate[]> {
  const url: string = makeUrl(from, `${ENDPOINT_DELIVERY_DATES}/${locationId}`);
  const response = await fetch(url, {
    method: "GET",
  });
  checkResponse(response, from);
  return await response.json();
}

export async function addReviewRequest(
  review: Review,
  from: FromValues,
): Promise<void> {
  const url: string = makeUrl(from, ENDPOINT_REVIEW);
  const response = await fetch(url, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(review),
  });

  checkResponse(response, from);
}

export async function getUserReviewsRequest(
  from: FromValues,
): Promise<APIReviewResponse[]> {
  const url: string = makeUrl(from, ENDPOINT_USER_REVIEWS);
  const response = await fetch(url, {
    method: "GET",
    credentials: "include",
  });

  checkResponse(response, from);
  return await response.json();
}

export async function updateReviewRequest(
  review: Review,
  from: FromValues,
): Promise<void> {
  const url: string = makeUrl(from, ENDPOINT_UPDATE_REVIEW);
  const response = await fetch(url, {
    method: "PUT",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(review),
  });

  checkResponse(response, from);
}

export async function getReviewsByItemIdRequest(
  itemId: number,
  from: FromValues,
): Promise<APIReviewResponse[]> {
  const url: string = makeUrl(from, `${ENDPOINT_ITEM_REVIEWS}/${itemId}`);
  const response = await fetch(url, {
    method: "GET",
  });

  checkResponse(response, from);
  return await response.json();
}

export async function getChampionIconsRequest(): Promise<
  { src: string; alt: string }[]
> {
  const response = await fetch(`/${ENDPOINT_CHAMPION_ICONS}`);

  checkResponse(response, FromValues.CLIENT);
  return await response.json();
}
