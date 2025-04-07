"use client";

import useSWR from "swr";
import { APIProfileInfoResponse } from "../interfaces/APIResponse";
import { FromValues, getProfileInfoRequest } from "../request";
import { useErrorRedirect } from "./useErrorRedirect";
import { ProfileInfo } from "../interfaces/profileInterfaces";
import { mapAPIProfileInfoResponseToProfileInfo } from "../mappers";
import { useStaticData } from "./StaticDataContext";

export default function ProfileView() {
  const { data, error } = useSWR<APIProfileInfoResponse>(
    ["profile-client", FromValues.CLIENT],
    getProfileInfoRequest,
  );
  const { locations } = useStaticData();
  useErrorRedirect(error);

  if (!data || error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[var(--orange)]"></div>
      </div>
    );
  }

  const profileInfo: ProfileInfo = mapAPIProfileInfoResponseToProfileInfo(data);
  const { user, ordersInfo } = profileInfo;

  const userLocation = locations.find((loc) => loc.id === user.locationId);

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        {/* Profile Header */}
        <div className="bg-gradient-to-r from-[var(--orange)] to-[var(--pink1)] p-8">
          <h1 className="text-4xl font-bold text-white">
            Welcome back,{" "}
            <span className="text-[var(--yellow)]">{user.userName}</span>
          </h1>
        </div>

        {/* User Information */}
        <div className="p-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold text-[var(--orange)] mb-6">
                Account Details
              </h2>
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-gray-600">Email:</span>
                  <span className="text-gray-800">{user.email}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-gray-600">Location:</span>
                  <span className="text-[var(--orange)] font-medium">
                    {userLocation?.country_name || "Not set"}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-gray-600">Created:</span>
                  <span className="text-gray-800">
                    {user.created.toLocaleDateString()}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-gray-600">
                    Last Sign-In:
                  </span>
                  <span className="text-gray-800">
                    {user.lastSingIn.toLocaleDateString()}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-gray-600">
                    Birth Date:
                  </span>
                  <span className="text-gray-800">
                    {user.birthDate.toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h2 className="text-2xl font-semibold text-[var(--orange)] mb-6">
                Gold Statistics
              </h2>
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-gray-600">
                    Current Gold:
                  </span>
                  <span className="text-[var(--yellow)] font-bold text-xl">
                    {user.currentGold.toLocaleString()} g
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-gray-600">
                    Total Gold Spent:
                  </span>
                  <span className="text-[var(--yellow)] font-bold text-xl">
                    {user.goldSpend.toLocaleString()} g
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Orders Summary */}
        <div className="p-8 border-t border-gray-200">
          <h2 className="text-2xl font-semibold text-[var(--orange)] mb-6">
            Orders Summary
          </h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">
                    Item Name
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">
                    Base Price
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">
                    Times Ordered
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">
                    Total Spend
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {ordersInfo.map((order, index) => (
                  <tr
                    key={index}
                    className="hover:bg-gray-50 transition-colors duration-150"
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-gray-900">
                      {order.itemName}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-[var(--yellow)] font-semibold">
                      {order.basePrice.toLocaleString()} g
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-900">
                      {order.timesOrdered.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-[var(--yellow)] font-semibold">
                      {order.totalSpend.toLocaleString()} g
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
