"use client";
import React, { useState } from "react";
import { Order, OrderStatus } from "@/app/interfaces/Order";
import { useStaticData } from "./StaticDataContext";
import { cancelOrderRequest } from "../request";
import toast from "react-hot-toast";
import Image from "next/image";
import { showErrorToast } from "../customToast";
import { useRouter } from "next/navigation";

export default function OrderHistoryCard({ order }: { order: Order }) {
  const router = useRouter();
  const { items } = useStaticData();
  const [orderStatus, setOrderStatus] = useState<string>(order.status);

  let itemCount: Record<string, number> = {};
  const uniqueNames: string[] = [...new Set(order.itemNames)];
  uniqueNames.forEach((name: string) => {
    itemCount[name] = order.itemNames.filter(
      (itemName: string) => itemName === name,
    ).length;
  });

  const displayedItemNames = uniqueNames
    .slice(0, 4)
    .map((name) => (itemCount[name] > 1 ? `${itemCount[name]} ${name}` : name));
  const itemImages = uniqueNames.map((name) => {
    const item = items.find((i) => i.name === name);
    return item?.img || "";
  });

  async function cancelOrder() {
    if (order.status !== "PENDING" && order.status !== "SHIPPED") {
      showErrorToast("Error canceling order");
      return;
    }
    const response = await cancelOrderRequest(order.id, "client");
    if (!response.ok) {
      showErrorToast("Error canceling order");
    }
    order.status = OrderStatus.CANCELED;
    setOrderStatus(order.status);
    toast.success("Order cancelled succesfully");
  }

  const extraCount = uniqueNames.length - 4;

  return (
    <div
      className="flex flex-col md:flex-row 
      border rounded shadow overflow-hidden max-w-2xl w-full
      border border-black"
    >
      <div
        className="w-full md:w-1/3 bg-gray-100 flex items-center justify-center p-2"
        style={{
          backgroundImage:
            "repeating-linear-gradient(45deg, #e5e7eb, #e5e7eb 2px, #fb923c 2px, #fb923c 4px)",
        }}
      >
        <div
          className={
            itemImages.length === 1
              ? "relative w-28 h-28"
              : "relative w-32 h-32"
          }
        >
          {itemImages.length === 1 ? (
            <div className="flex items-center justify-center w-full h-full">
              <Image
                src={itemImages[0]}
                alt={`Item ${uniqueNames[0]}`}
                fill
                className="object-cover rounded"
              />
            </div>
          ) : itemImages.length === 2 ? (
            <div className="grid grid-cols-2 gap-1 w-full h-full">
              {itemImages.map((img, idx) => (
                <div key={idx} className="relative">
                  <Image
                    src={img}
                    alt={`Item ${uniqueNames[idx]}`}
                    fill
                    className="object-cover rounded"
                  />
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 grid-rows-2 gap-1 w-full h-full">
              {itemImages.map((img, idx) => (
                <div key={idx} className="relative">
                  <Image
                    src={img}
                    alt={`Item ${uniqueNames[idx]}`}
                    fill
                    className="object-cover rounded"
                  />
                </div>
              ))}
            </div>
          )}
          {itemImages.length === 4 && extraCount > 0 && (
            <div
              className="absolute inset-0 
              bg-black bg-opacity-35 flex 
              items-center justify-center text-white text-lg rounded"
            >
              +{extraCount}
            </div>
          )}
        </div>
      </div>
      <div className="w-full md:w-2/3 p-4 flex flex-col justify-between">
        <div>
          <h2 className="font-bold text-lg">
            You ordered{" "}
            <span className="text-[var(--orange)]">
              {displayedItemNames.join(", ")}
              {extraCount > 0 && " ..."}
            </span>
          </h2>
          <p className="mt-1 text-sm font-bold">
            Order Date: {new Date(order.orderDate).toLocaleDateString()}
          </p>
          <p className="mt-1 text-sm font-bold">
            Delivery Date: {new Date(order.deliveryDate).toLocaleDateString()}
          </p>
          <p className="mt-1 text-sm font-bold">
            Total:
            <span>${order.total}</span>
          </p>
          <p className="mt-1 text-sm font-bold">Status: {orderStatus}</p>
        </div>
        <div className="mt-4 flex gap-2">
          <button
            className={`px-4 py-2 rounded transition-colors 
                       w-full md:w-auto ${
                         orderStatus === "PENDING"
                           ? "bg-red-500 text-white hover:bg-red-600 cursor-pointer"
                           : "bg-gray-300 text-gray-500 cursor-not-allowed"
                       }`}
            onClick={cancelOrder}
            disabled={orderStatus !== "PENDING"}
          >
            Cancel Order
          </button>
          {orderStatus === OrderStatus.DELIVERED && !order.reviewed && (
            <button
              className="px-4 py-2 rounded bg-yellow-500 text-white 
                       hover:bg-yellow-600 transition-all duration-300 
                       transform hover:scale-105 w-full md:w-auto"
              onClick={() => router.push(`/review/${order.id}`)}
            >
              Review
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
