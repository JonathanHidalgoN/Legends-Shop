"use client";

import { useState } from "react";
import { useStaticData } from "./StaticDataContext";
import { getProfileInfoRequest } from "../request";
import useSWR from "swr";
import { APIProfileInfoResponse } from "../interfaces/APIResponse";
import { useErrorRedirect } from "./useErrorRedirect";

export default function ProfileView() {

  const { items } = useStaticData();

  const { data, error } = useSWR<APIProfileInfoResponse>(
    "client",
    getProfileInfoRequest,
  );
  useErrorRedirect(error);

  if (!data) {
    return <div>Loading...</div>;
  }

  return <div></div>;
}
