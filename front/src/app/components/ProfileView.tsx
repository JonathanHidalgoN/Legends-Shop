"use client";

import useSWR from "swr";
import { APIProfileInfoResponse } from "../interfaces/APIResponse";
import { getProfileInfoRequest } from "../request";
import { useErrorRedirect } from "./useErrorRedirect";
import { useState } from "react";
import { ProfileInfo } from "../interfaces/profileInterfaces";
import { mapAPIProfileInfoResponseToProfileInfo } from "../mappers";

export default function ProfileView() {
  const { data, error } = useSWR<APIProfileInfoResponse>(
    "client",
    getProfileInfoRequest
  );
  useErrorRedirect(error);

  if (!data) {
    return <div className="text-center py-10">Loading...</div>;
  } else {

    const profileInfo: ProfileInfo = mapAPIProfileInfoResponseToProfileInfo(data);

    const { user, ordersInfo } = profileInfo;

    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">
          Check your profile, <span className="text-[var(--orange)]">{user.userName}.</span>
        </h1>

        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold mb-4">User Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p>
                <span className="font-bold">Email:</span> {user.email}
              </p>
              <p>
                <span className="font-bold">Created:</span>{" "}
                {user.created.toLocaleDateString()}
              </p>
              <p>
                <span className="font-bold">Last Sign-In:</span>{" "}
                {user.lastSingIn.toLocaleDateString()}
              </p>
            </div>
            <div>
              <p>
                <span className="font-bold">Gold Spent:</span> {user.goldSpend}
              </p>
              <p>
                <span className="font-bold">Current Gold:</span>{" "}
                {user.currentGold}
              </p>
              <p>
                <span className="font-bold">Birth Date:</span>{" "}
                {user.birthDate.toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-semibold mb-4">Orders Summary</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <span className="font-bold text-[var(--orange)]">
                      Item Name
                    </span>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <span className="font-bold text-[var(--orange)]">
                      Base Price
                    </span>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <span className="font-bold text-[var(--orange)]">
                      Times Ordered
                    </span>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <span className="font-bold text-[var(--orange)]">
                      Total Spend
                    </span>
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {ordersInfo.map((order, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap">{order.itemName}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      ${order.basePrice}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {order.timesOrdered}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      ${order.totalSpend}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  }
}
