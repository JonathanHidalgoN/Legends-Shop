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
export const ENDPOINT_CART_ADD_ITEMS: string = `cart/add_items`;
export const ENDPOINT_CART_ADD_ITEM: string = `cart/add_item`;
export const ENDPOINT_CART_ADDED_CART_ITEMS: string = `cart/added_cart_items`;
export const ENDPOINT_CART_DELETE_ITEM: string = `cart/delete_cart_item`;
export const ENDPOINT_UPDATE_ITEMS: string = `/updateItems`;
export const ENDPOINT_USER_LOCATION: string = `locations/user`;
export const ENDPOINT_DELIVERY_DATES: string = `delivery_dates/dates`;
export const ENDPOINT_REVIEW: string = `review/add`;
export const ENDPOINT_UPDATE_REVIEW: string = `review/update`;
export const ENDPOINT_USER_REVIEWS: string = `review/user`;

function makeUrl(from: string, endpoint: string): string {
  let url: string;
  if (from === "server") {
    url = SERVER_DOMAIN + endpoint;
  } else {
    url = CLIENT_DOMAIN + endpoint;
  }
  return url;
}

export async function createAPIError(
  response: Response,
  errorMsg: string,
): Promise<APIError> {
  if (response.status == 401) {
    return new APIError("Unauthorized", 401);
  } else {
    const data = await response.json();
    return new APIError(data?.message || errorMsg, response.status, data);
  }
}

async function throwAPIError(response: Response, errorMsg: string) {
  const apiError: APIError = await createAPIError(response, errorMsg);
  showErrorToast(errorMsg);
  throw apiError;
}

/**
 * Makes a POST request to the login endpoint with the provided username and password.
 *
 * @param userName - The username of the user attempting to log in.
 * @param password - The password for the user.
 * @returns A Promise that resolves with the response from the login request.
 */
export async function logInRequest(
  userName: string,
  password: string,
  from: string = "server",
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
  from: string = "server",
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

export async function refreshTokenRequest(from: string = "server") {
  const url: string = makeUrl(from, ENDPOINT_REFRESH_TOKEN);
  return await fetch(url, {
    credentials: "include",
  });
}

/**
 * Makes a GET request to fetch a subset of items.
 *
 * @returns A Promise that resolves with the response from the request.
 */
export async function someItemsRequest(from: string = "server") {
  const url: string = makeUrl(from, ENDPOINT_SOME_ITEMS);
  return await fetch(url);
}

/**
 * Makes a GET request to fetch all items.
 *
 * @returns A Promise that resolves with the response from the request.
 */
export async function allItemsRequest(from: string = "server") {
  const url: string = makeUrl(from, ENDPOINT_ITEMS_ALL);
  return await fetch(url);
}

/**
 * Makes a GET request to fetch all unique tags.
 *
 * @returns A Promise that resolves with the response from the request.
 */
export async function allTagsRequet(from: string = "server") {
  const url: string = makeUrl(from, ENDPOINT_ALL_TAGS);
  return await fetch(url);
}

export async function logoutRequest(from: string = "server") {
  const url: string = makeUrl(from, ENDPOINT_LOGIN_OUT);
  return await fetch(url, {
    method: "GET",
    credentials: "include",
  });
}

export async function orderRequest(order: Order, from: string = "server") {
  const url: string = makeUrl(from, ENDPOINT_ORDER);
  return await fetch(url, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(order),
  });
}

/**
 * Makes a GET request to fetch user history.
 */
export async function getOrderHistoryWithCredentialsRequest(
  from: string = "server",
): Promise<APIOrderResponse[]> {
  const url = `${makeUrl(from, ENDPOINT_ORDER_HISTORY)}`;
  const response = await fetch(url, {
    credentials: "include",
  });
  if (!response.ok) {
    await throwAPIError(response, "Failed to fetch the orders");
  }
  return await response.json();
}

export async function getProfileInfoRequest(
  from: string = "server",
): Promise<APIProfileInfoResponse> {
  const url: string = makeUrl(from, ENDPOINT_PROFILE_INFO);
  const response = await fetch(url, {
    credentials: "include",
  });
  if (!response.ok) {
    await throwAPIError(response, "Failed to get the profile info");
  }
  return await response.json();
}

export async function addToCarRequest(
  from: string = "server",
  apiCartItem: APICartItemResponse,
  errorMsg: string,
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

  if (!response.ok) {
    await throwAPIError(response, errorMsg);
  }
  return await response.json();
}

/**
 * Cancel the order requet with id
 */
export async function cancelOrderRequest(
  orderId: number,
  from: string = "server",
) {
  const url: string = makeUrl(from, `${ENDPOINT_ORDER_CANCEL}/${orderId}`);
  return await fetch(url, {
    method: "PUT",
    credentials: "include",
  });
}

export async function getCurrentUserGoldRequest(from: string = "server") {
  const url: string = makeUrl(from, ENDPOINT_PROFILE_CURRENT_GOLD);
  return await fetch(url, {
    credentials: "include",
  });
}

export async function getAddedCartItemsRequest(
  from: string = "server",
): Promise<APICartItemResponse[]> {
  const url: string = makeUrl(from, ENDPOINT_CART_ADDED_CART_ITEMS);
  const response = await fetch(url, {
    credentials: "include",
  });
  if (!response.ok) {
    await throwAPIError(response, "Error getting cart items");
  }
  return await response.json();
}

export async function deleteCartItemRequest(
  from: string = "server",
  cartItemId: number,
  errorMsg: string,
): Promise<void> {
  const url: string = makeUrl(
    from,
    `${ENDPOINT_CART_DELETE_ITEM}/${cartItemId}`,
  );
  const response = await fetch(url, {
    method: "DELETE",
    credentials: "include",
  });

  if (!response.ok) {
    await throwAPIError(response, errorMsg);
  }
  return await response.json();
}

export async function updateItemsRequest(
  from: string = "server",
): Promise<void> {
  const url: string = makeUrl(from, ENDPOINT_UPDATE_ITEMS);
  const response = await fetch(url, {
    method: "PUT",
  });
  if (!response.ok) {
    await throwAPIError(response, "Error updating the items");
  }
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

  if (!response.ok) {
    await throwAPIError(response, "Error updating the hd item images");
  }
}

export async function getAllItemNamesRequest(
  from: string = "server",
): Promise<string[]> {
  const url: string = makeUrl(from, ENDPOINT_ALL_ITEM_NAMES);
  const response = await fetch(url);
  if (!response.ok) {
    await throwAPIError(response, "Error fetching item names");
  }
  return await response.json();
}

export async function getAllEffectNamesRequest(
  from: string = "server",
): Promise<string[]> {
  const url: string = makeUrl(from, ENDPOINT_ALL_EFFECT_NAMES);
  const response = await fetch(url);
  if (!response.ok) {
    await throwAPIError(response, "Error fetching effect names");
  }
  return await response.json();
}

export async function getAllLocationsRequest(
  from: string = "server",
): Promise<Location[]> {
  const url: string = makeUrl(from, ENDPOINT_ALL_LOCATIONS);
  const response = await fetch(url);
  if (!response.ok) {
    await throwAPIError(response, "Error fetching locations");
  }
  return await response.json();
}

export async function getUserLocationRequest(
  from: string = "client",
): Promise<Location> {
  const url: string = makeUrl(from, ENDPOINT_USER_LOCATION);
  const response = await fetch(url, {
    credentials: "include",
  });
  if (!response.ok) {
    await throwAPIError(response, "Error fetching user location");
  }
  return await response.json();
}

export async function getDeliveryDatesRequest(
  locationId: number,
  from: string = "client",
): Promise<DeliveryDate[]> {
  const url: string = makeUrl(from, `${ENDPOINT_DELIVERY_DATES}/${locationId}`);
  const response = await fetch(url, {
    method: "GET",
  });
  if (!response.ok) {
    await throwAPIError(response, "Error fetching delivery dates");
  }
  return await response.json();
}

export async function addReviewRequest(
  review: Review,
  from: string = "server",
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

  if (!response.ok) {
    await throwAPIError(response, "Error adding review");
  }
  return await response.json();
}

/**
 * Get all reviews for the authenticated user.
 * 
 * @param from - The domain to make the request to ("server" or "client")
 * @returns A Promise that resolves with an array of reviews
 */
export async function getUserReviewsRequest(
  from: string = "server",
): Promise<APIReviewResponse[]> {
  const url: string = makeUrl(from, ENDPOINT_USER_REVIEWS);
  const response = await fetch(url, {
    method: "GET",
    credentials: "include",
  });

  if (!response.ok) {
    await throwAPIError(response, "Error fetching user reviews");
  }
  return await response.json();
}

/**
 * Update an existing review.
 * 
 * @param review - The review object with updated rating and comments
 * @param from - The domain to make the request to ("server" or "client")
 * @returns A Promise that resolves with the response from the update request
 */
export async function updateReviewRequest(
  review: Review,
  from: string = "server",
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

  if (!response.ok) {
    await throwAPIError(response, "Error updating review");
  }
  return await response.json();
}
