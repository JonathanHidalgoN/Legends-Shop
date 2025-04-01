"use client";
import { useAuthContext } from "@/app/components/AuthContext";
import { useCarContext } from "@/app/components/CarContext";
import CarDropDown from "@/app/components/CarDropDown";
import { CartItem, Order, OrderStatus } from "@/app/interfaces/Order";
import { orderRequest } from "@/app/request";
import { useRouter } from "next/navigation";
import { useState } from "react";
import OrderSuccessModal from "@/app/components/OrderSuccessModal";
import { usePathname } from "next/navigation";
import { getCurrentUserGold } from "@/app/profileFunctions";
import { showErrorToast } from "@/app/customToast";
import Image from "next/image";

export default function OrderPage() {
  const { carItems, getTotalCost, cleanCar, setCurrentGold, currentGold, currentLocation } =
    useCarContext();
  const [showModal, setShowModal] = useState<boolean>(false);
  const [orderId, setOrderId] = useState<number | null>(null);
  const { userName } = useAuthContext();
  const router = useRouter();
  const pathname = usePathname();

  function checkIfcanBuy(
    orderTotal: number,
    currentGold: number | null,
  ): boolean {
    if (!currentGold) {
      return false;
    }
    return orderTotal <= currentGold;
  }

  async function handleBuy() {
    if (!userName) {
      showErrorToast("Login to order");
    } else if (!currentLocation) {
      showErrorToast("Please select a delivery location");
    } else {
      const orderTotalCost: number = getTotalCost();
      const canBuy: boolean = checkIfcanBuy(orderTotalCost, currentGold);
      if (!canBuy) {
        showErrorToast("Farm more gold to buy");
        return;
      }
      const order: Order = {
        itemNames: carItems.map((carItem: CartItem) => carItem.item.name),
        total: getTotalCost(),
        userName: userName,
        orderDate: new Date(),
        id: 0,
        status: OrderStatus.PENDING,
        deliveryDate: new Date(),
        locationId: currentLocation.id
      };
      const response = await orderRequest(order, "client");
      if (!response.ok) {
        showErrorToast("Error making the order");
        return;
      }
      const leftGold: number | null = await getCurrentUserGold();
      setCurrentGold(leftGold);
      const data = await response.json();
      setOrderId(data.order_id);
      setShowModal(true);
      cleanCar();
    }
  }

  function handleCancel() {
    cleanCar();
  }

  const orderTotal = getTotalCost();
  const canBuy = checkIfcanBuy(orderTotal, currentGold);
  const remainingGold = currentGold !== null ? currentGold - orderTotal : null;

  return (
    <div className="min-h-screen bg-[var(--white)] py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header Section */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-[var(--orange)] mb-2">
            Your Order
          </h1>
          <p className="text-gray-600">
            Review your items and confirm your purchase
          </p>
        </div>

        {/* Order Summary Card */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-[var(--orange)]">
              Order Summary
            </h2>
          </div>

          {/* Items List */}
          <div className="space-y-4">
            <CarDropDown tiny={true} />
          </div>

          {/* Total Section */}
          <div className="mt-8 pt-6 border-t">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-lg font-semibold">Total Amount:</span>
                <span className="text-2xl font-bold text-[var(--yellow)]">
                  {orderTotal.toLocaleString()} g
                </span>
              </div>

              {userName && currentGold !== null && (
                <>
                  <div className="flex justify-between items-center">
                    <span className="text-lg font-semibold">Current Gold:</span>
                    <span className="text-xl font-bold text-yellow-500">
                      {currentGold.toLocaleString()} g
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-lg font-semibold">After Purchase:</span>
                    <span className="text-xl font-bold text-yellow-500">
                      {remainingGold?.toLocaleString()} g
                    </span>
                  </div>
                </>
              )}
            </div>

            {/* Action Buttons */}
            <div className="mt-8 space-y-4">
              <div className="flex gap-4">
                {userName ? (
                  <button
                    onClick={handleBuy}
                    disabled={!canBuy}
                    className={`flex-1 py-3 px-6 rounded-lg transition-all duration-300 
                      transform hover:scale-105 font-semibold text-lg
                      ${canBuy 
                        ? 'bg-[var(--orange)] text-white hover:bg-opacity-90' 
                        : 'bg-gray-300 text-gray-500 cursor-not-allowed'}`}
                  >
                    Confirm Purchase
                  </button>
                ) : (
                  <button
                    onClick={() => {
                      router.push(
                        `/auth/login?redirect=${encodeURIComponent(pathname)}`,
                      );
                    }}
                    className="flex-1 bg-[var(--orange)] text-white py-3 px-6 
                      rounded-lg hover:bg-opacity-90 transition-all duration-300 
                      transform hover:scale-105 font-semibold text-lg"
                  >
                    Login to Purchase
                  </button>
                )}
                <button
                  onClick={handleCancel}
                  className="flex-1 bg-gray-100 text-gray-700 py-3 px-6 
                    rounded-lg hover:bg-gray-200 transition-all duration-300 
                    transform hover:scale-105 font-semibold text-lg"
                >
                  Cancel Order
                </button>
              </div>
              {userName && !canBuy && (
                <p className="text-red-500 text-center text-sm">
                  Not enough gold! You need {orderTotal.toLocaleString()} g but have {currentGold?.toLocaleString()} g
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Success Modal */}
        {showModal && (
          <OrderSuccessModal
            orderId={orderId}
            onClose={() => setShowModal(false)}
          />
        )}
      </div>
    </div>
  );
}
