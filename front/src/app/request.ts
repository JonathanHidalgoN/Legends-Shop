import { BACKEND_PORT, BACKEND_HOST } from "./envVariables";

/**
 * Endpoint URL for user login.
 * This endpoint accepts POST requests with a JSON body containing { userName, password }.
 */
export const ENDPOINT_LOGIN: string = `http://${BACKEND_HOST}:${BACKEND_PORT}/auth/logIn`;

/**
 * Endpoint URL to fetch all items.
 */
export const ENDPOINT_ITEMS_ALL: string = `http://${BACKEND_HOST}:${BACKEND_PORT}/items/all`;

/**
 * Endpoint URL to fetch a subset of items.
 */
export const ENDPOINT_SOME_ITEMS: string = `http://${BACKEND_HOST}:${BACKEND_PORT}/items/some`;

/**
 * Endpoint URL to fetch all unique tags.
 */
export const ENDPOINT_ALL_TAGS: string = `http://${BACKEND_HOST}:${BACKEND_PORT}/items/uniqueTags`;

/**
 * Makes a POST request to the login endpoint with the provided username and password.
 *
 * @param userName - The username of the user attempting to log in.
 * @param password - The password for the user.
 * @returns A Promise that resolves with the response from the login request.
 */
export async function logInRequest(userName: string, password: string) {
  return await fetch(ENDPOINT_LOGIN, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ userName, password }),
  });
}

/**
 * Makes a GET request to fetch a subset of items.
 *
 * @returns A Promise that resolves with the response from the request.
 */
export async function someItemsRequest() {
  return await fetch(ENDPOINT_SOME_ITEMS);
}

/**
 * Makes a GET request to fetch all items.
 *
 * @returns A Promise that resolves with the response from the request.
 */
export async function allItemsRequest() {
  return await fetch(ENDPOINT_ITEMS_ALL);
}

/**
 * Makes a GET request to fetch all unique tags.
 *
 * @returns A Promise that resolves with the response from the request.
 */
export async function allTagsRequet() {
  return await fetch(ENDPOINT_ALL_TAGS);
}
