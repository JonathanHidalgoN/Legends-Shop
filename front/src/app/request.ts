import { BACKEND_PORT, BACKEND_HOST } from "./envVariables";
import { Order } from "./interfaces/Order";

//TODO: how to improve this solution?
export const SERVER_DOMAIN: string = `http://${BACKEND_HOST}:${BACKEND_PORT}/`
export const CLIENT_DOMAIN: string = `http://localhost:${BACKEND_PORT}/`
export const ENDPOINT_LOGIN: string = `auth/token`;
export const ENDPOINT_LOGIN_OUT: string = `auth/logout`;
export const ENDPOINT_ITEMS_ALL: string = `items/all`;
export const ENDPOINT_SOME_ITEMS: string = `items/some`;
export const ENDPOINT_ALL_TAGS: string = `items/uniqueTags`;
export const ENDPOINT_ORDER: string = `orders/order`;
export const ENDPOINT_ORDER_HISTORY: string = `orders/order_history`;

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
export async function logInRequest(userName: string, password: string, from: string = "server") {
  const url: string = makeUrl(from, ENDPOINT_LOGIN);
  const formData = new URLSearchParams();
  formData.append("username", userName);
  formData.append("password", password);
  return await fetch(url, {
    method: 'POST',
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    credentials: "include",
    body: formData.toString(),
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
    method: "POST",
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
export async function getUserHistoryRequest(from: string = "server") {
  const url: string = makeUrl(from, ENDPOINT_ORDER_HISTORY);
  return await fetch(url, {
    credentials: "include",
  });
}
