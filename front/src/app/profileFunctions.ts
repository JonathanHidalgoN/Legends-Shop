import toast from "react-hot-toast";
import { getCurrentUserGoldRequest, getProfileInfoRequest } from "./request";
import { ProfileInfo } from "./interfaces/APIResponse";

export async function getCurrentUserGold(): Promise<number | null> {
  const response = await getCurrentUserGoldRequest("client");
  if (!response.ok) {
    toast.error("Server error while getting current user gold");
    return null;
  } else {
    const data = await response.json();
    return data.userGold;
  }
}

export async function getProfileInfo(): Promise<ProfileInfo | null> {
  const response = await getProfileInfoRequest("client");
  if (!response.ok) {
    toast.error("Server error while getting current user gold");
    return null;
  } else {
    const data = await response.json();
    return data.profileInfo;
  }
}
