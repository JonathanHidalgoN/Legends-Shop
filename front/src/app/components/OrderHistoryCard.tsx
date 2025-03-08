"use client";
import React from "react";
import { Order } from "@/app/interfaces/Order";
import { useStaticData } from "./StaticDataContext";
import { cancelOrderRequest } from "../request";
import toast from "react-hot-toast/headless";
import Image from "next/image";

export default function OrderHistoryCard({ order }: { order: Order }) {
  const { items } = useStaticData();

  const displayedItemNames = order.itemNames.slice(0, 4);
  const itemImages = displayedItemNames.map(name => {
    const item = items.find(i => i.name === name);
    return item?.img || "";
  });

  async function cancelOrder(orderId: number, orderStatus: string) {
    if (orderStatus !== "PENDING" && orderStatus !== "SHIPPED") {
      toast.error("Error canceling order")
      return;
    }
    const response = await cancelOrderRequest(orderId, "client");
    if (!response.ok) {
      toast.error("Error canceling order")
    }
  }

  const extraCount = order.itemNames.length - 4;

  return (
    <div className="flex flex-col md:flex-row border rounded shadow overflow-hidden max-w-2xl w-full">
      <div className="w-full md:w-1/3 bg-gray-100 flex items-center justify-center p-2">
        <div className="relative">
          <div className="grid grid-cols-2 grid-rows-2 gap-1">
            {itemImages.map((img, idx) => (
              <div key={idx} className="relative w-16 h-16">
                {img ? (

                  <Image
                    src={img}
                    alt={`Item ${displayedItemNames[idx]}`}
                    fill
                    className="object-cover rounded"
                  />
                ) : (
                  <div className="bg-gray-200 w-full h-full rounded" />
                )}
                {idx === 3 && extraCount > 0 && (
                  <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center text-white text-lg rounded">
                    +{extraCount}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="w-full md:w-2/3 p-4 flex flex-col justify-between">
        <div>
          <h2 className="font-bold text-lg">
            You ordered {displayedItemNames.join(", ")}
            {extraCount > 0 && " ..."}
          </h2>
          <p className="mt-1 text-sm">
            Order Date: {new Date(order.orderDate).toLocaleDateString()}
          </p>
          <p className="mt-1 text-sm">Total: ${order.total}</p>
          <p className="mt-1 text-sm">Status: {order.status}</p>
        </div>
        <div className="mt-4">
          <button
            className={`px-4 py-2 rounded transition-colors w-full md:w-auto ${order.status === "PENDING"
              ? "bg-red-500 text-white hover:bg-red-600 cursor-pointer"
              : "bg-gray-300 text-gray-500 cursor-not-allowed"
              }`}
            onClick={() => cancelOrder(order.id, order.status)}
            disabled={order.status !== "PENDING"}
          >
            Cancel Order
          </button>
        </div>
      </div>
    </div>
  );
}
