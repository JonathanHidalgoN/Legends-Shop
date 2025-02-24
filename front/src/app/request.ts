import { BACKEND_PORT, BACKEND_HOST } from "./envVariables";

export const ENDPOINT_LOGIN: string = `http://${BACKEND_HOST}:${BACKEND_PORT}/auth/logIn`


export async function logInRequest(userName: string, password: string) {
  return await fetch(ENDPOINT_LOGIN, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ userName, password }),
  })
}
