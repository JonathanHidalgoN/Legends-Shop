import { logInRequest } from "../request";

export async function signup(userName: string, password: string) {
  const response = await logInRequest(userName, password, "client");
  if (!response.ok) {
    throw new Error(``);
  }
  const data = await response.json()
  if (!("access_token" in data) || !("token_type" in data) ||
    data.token_type !== "bearer") {
    throw new Error(``);
  }
}
