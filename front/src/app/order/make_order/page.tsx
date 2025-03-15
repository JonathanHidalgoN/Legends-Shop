"use client";
import toast from "react-hot-toast";
import { useAuthContext } from "@/app/components/AuthContext";
import { useCarContext } from "@/app/components/CarContext";
import CarDropDown from "@/app/components/CarDropDown";
import { Order, OrderStatus } from "@/app/interfaces/Order";
import { orderRequest } from "@/app/request";
import { useRouter } from "next/navigation";
import { useState } from "react";
import OrderSuccessModal from "@/app/components/OrderSuccessModal";

export default function OrderPage() {
  const { carItems, getTotalCost, cleanCar } = useCarContext();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [orderId, setOrderId] = useState<number | null>(null);
  const { userName } = useAuthContext();
  const router = useRouter();

  async function handleBuy() {
    if (!userName) {
      toast.error("Login to order");
    } else {
      const order: Order = {
        itemNames: carItems.map((item) => item.name),
        total: getTotalCost(),
        userName: userName,
        orderDate: new Date(),
        id: 0,
        status: OrderStatus.PENDING,
        deliveryDate: new Date(),
      };
      const response = await orderRequest(order, "client");
      if (!response.ok) {
        throw new Error(``);
      }

      const data = await response.json();
      setOrderId(data.order_id);
      setShowModal(true);
      cleanCar();
    }
  }

  function handleCancel() {
    cleanCar();
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4 text-[var(--orange)]">
        Your Order
      </h1>
      <CarDropDown tiny={false} />
      <div className="mt-6 border-t pt-4">
        <div className="flex space-x-4">
          {userName && (
            <button
              onClick={handleBuy}
              className="flex-1 bg-[var(--orange)] text-white py-2 
                 rounded hover:opacity-80 transition-colors"
            >
              Buy
            </button>
          )}
          {showModal && (
            <OrderSuccessModal
              orderId={orderId}
              onClose={() => setShowModal(false)}
            />
          )}
          {!userName && (
            <button
              onClick={() => {
                router.push("/auth/login");
              }}
              className="flex-1 bg-[var(--orange)] text-white py-2 
                 rounded hover:opacity-80 transition-colors"
            >
              Login
            </button>
          )}
          <button
            onClick={handleCancel}
            className="flex-1 bg-gray-500 text-white py-2 rounded hover:bg-gray-800 transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
