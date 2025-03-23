import { getCurrentUserGoldRequest } from "./request";
import { showErrorToast } from "./customToast";

export async function getCurrentUserGold(): Promise<number | null> {
  const response = await getCurrentUserGoldRequest("client");
  if (!response.ok) {
    showErrorToast("Server error while getting current user gold");
    return null;
  } else {
    const data = await response.json();
    return data.userGold;
  }
}
