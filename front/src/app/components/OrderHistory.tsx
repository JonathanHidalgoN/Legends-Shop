"use client";
import React, { useState, useEffect } from "react";
import { Order } from "@/app/interfaces/Order";
import OrderHistoryCard from "@/app/components/OrderHistoryCard";
import { getUserHistoryRequest } from "@/app/request";
import toast from "react-hot-toast";

export default function OrderHistory({ urlUserName }: { urlUserName: string }) {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchUserHistory() {
      try {
        const response = await getUserHistoryRequest(urlUserName);
        if (!response.ok) {
          toast.error("Error fetching order history");
          return;
        }
        const data = await response.json();
        setOrders(data);
      } catch (error) {
        console.log(error);
        toast.error("An unexpected error occurred");
      } finally {
        setLoading(false);
      }
    }
    fetchUserHistory();
  }, [urlUserName]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="flex flex-col justify-center items-center gap-4 p-4">
      {orders.length > 0 ? (
        orders.map(order => (
          <OrderHistoryCard key={order.id} order={order} />
        ))
      ) : (
        <div>No orders found.</div>
      )}
    </div>
  );
}
