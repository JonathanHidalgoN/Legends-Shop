"use client"

import { useEffect, useState } from "react";
import { ProfileInfo } from "../interfaces/APIResponse";
import { getProfileInfo } from "../profileFunctions";

export default function ProfileView({ userName }: { userName: string }) {

  const [loading, setLoading] = useState<boolean>(true);
  const [profileInfo, setProfileInfo] = useState<ProfileInfo | null>(null);

  useEffect(() => {
    async function fetchProfileInfo() {
      const profileInfo: ProfileInfo | null = await getProfileInfo()
      setProfileInfo(profileInfo);
    }
    fetchProfileInfo();
  }, []);

  if (loading) return <div>Loading...</div>;

  return <div></div>;
}
