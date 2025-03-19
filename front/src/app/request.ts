import { SERVER_DOMAIN, CLIENT_DOMAIN } from "./envVariables";
import { Order } from "./interfaces/Order";

//TODO: how to improve this solution?
export const ENDPOINT_LOGIN: string = `auth/token`;
export const ENDPOINT_SINGUP: string = `auth/singup`;
export const ENDPOINT_REFRESH_TOKEN: string = `auth/refresh_token`;
export const ENDPOINT_LOGIN_OUT: string = `auth/logout`;
export const ENDPOINT_ITEMS_ALL: string = `items/all`;
export const ENDPOINT_SOME_ITEMS: string = `items/some`;
export const ENDPOINT_ALL_TAGS: string = `items/uniqueTags`;
export const ENDPOINT_ORDER: string = `orders/order`;
export const ENDPOINT_ORDER_HISTORY: string = `orders/order_history`;
export const ENDPOINT_ORDER_CANCEL: string = `orders/cancel_order`;
export const ENDPOINT_PROFILE_CURRENT_GOLD: string = `profile/current_gold`;

function makeUrl(from: string, endpoint: string): string {
  let url: string;
  if (from === "server") {
    url = SERVER_DOMAIN + endpoint;
  } else {
    url = CLIENT_DOMAIN + endpoint;
  }
  return url;
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
  from: string = "server",
) {
  const url: string = makeUrl(from, ENDPOINT_SINGUP);
  const formData = new URLSearchParams();
  formData.append("username", userName);
  formData.append("password", password);
  formData.append("email", email);
  formData.append("birthDate", birthDate.toISOString().substring(0, 10));
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
export async function getUserHistoryRequest(
  from: string = "server",
  filters: {
    orderStatus?: string;
    minOrderDate?: Date;
    maxOrderDate?: Date;
    minDeliveryDate?: Date;
    maxDeliveryDate?: Date;
    sortField?: string;
    sortOrder?: string;
    filterItemNames?: string[];
  } = {},
) {
  const queryParams = new URLSearchParams();

  if (filters.orderStatus) {
    queryParams.append("orderStatus", filters.orderStatus);
  }
  if (filters.minOrderDate) {
    queryParams.append(
      "minOrderDate",
      filters.minOrderDate.toISOString().substring(0, 10),
    );
  }
  if (filters.maxOrderDate) {
    queryParams.append(
      "maxOrderDate",
      filters.maxOrderDate.toISOString().substring(0, 10),
    );
  }
  if (filters.minDeliveryDate) {
    queryParams.append(
      "minDeliveryDate",
      filters.minDeliveryDate.toISOString().substring(0, 10),
    );
  }
  if (filters.maxDeliveryDate) {
    queryParams.append(
      "maxDeliveryDate",
      filters.maxDeliveryDate.toISOString().substring(0, 10),
    );
  }
  if (filters.sortField) {
    queryParams.append("sortField", filters.sortField);
  }
  if (filters.sortOrder) {
    queryParams.append("sortOrder", filters.sortOrder);
  }
  if (filters.filterItemNames && filters.filterItemNames.length > 0) {
    queryParams.append("filterItemNames", filters.filterItemNames.join(","));
  }
  const url = `${makeUrl(from, ENDPOINT_ORDER_HISTORY)}?${queryParams.toString()}`;
  return await fetch(url, {
    credentials: "include",
  });
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
