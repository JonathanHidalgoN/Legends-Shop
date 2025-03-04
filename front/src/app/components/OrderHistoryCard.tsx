"use client";
import React from "react";
import { Order } from "@/app/interfaces/Order";
import { useStaticData } from "./StaticDataContext";

export default function OrderHistoryCard({ order }: { order: Order }) {
  const { items } = useStaticData();

  const displayedItemNames = order.itemNames.slice(0, 4);
  const itemImages = displayedItemNames.map(name => {
    const item = items.find(i => i.name === name);
    return item?.img || "";
  });

  const extraCount = order.itemNames.length - 4;

  const status = "ok";

  return (
    <div className="flex flex-col md:flex-row border rounded shadow overflow-hidden max-w-2xl w-full">
      <div className="w-full md:w-1/3 bg-gray-100 flex items-center justify-center p-2">
        <div className="relative">
          <div className="grid grid-cols-2 grid-rows-2 gap-1">
            {itemImages.map((img, idx) => (
              <div key={idx} className="relative w-16 h-16">
                {img ? (
                  <img
                    src={img}
                    alt={`Item ${displayedItemNames[idx]}`}
                    className="object-cover w-full h-full rounded"
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
            Order Date: {new Date(order.date).toLocaleDateString()}
          </p>
          <p className="mt-1 text-sm">Total: ${order.total}</p>
          <p className="mt-1 text-sm">Status: {status}</p>
        </div>
        <div className="mt-4">
          <button
            className={`px-4 py-2 rounded transition-colors w-full md:w-auto ${status === "ok"
              ? "bg-red-500 text-white hover:bg-red-600 cursor-pointer"
              : "bg-gray-300 text-gray-500 cursor-not-allowed"
              }`}
            onClick={() => {
              if (status === "ok") {
                console.log("Cancel order:", order.id);
              }
            }}
            disabled={status !== "ok"}
          >
            Cancel Order
          </button>
        </div>
      </div>
    </div>
  );
}
