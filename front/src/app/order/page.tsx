"use client";
import { useAuthContext } from "../components/AuthContext";
import { useCarContext } from "../components/CarContext";
import CarDropDown from "../components/CarDropDown";
import { Order } from "../interfaces/Order";
import { orderRequest } from "../request";

export default function OrderPage() {
  const { carItems, getTotalCost, cleanCar } = useCarContext();
  const { userName } = useAuthContext();


  async function handleBuy() {
    if (!userName) {
      //Null userName handle
      console.log("Null userName");
    } else {
      const order: Order = {
        items: carItems,
        total: getTotalCost(),
        userName: userName,
        date: new Date(""),
        id: 0,
        status: ""
      };
      const response = await orderRequest(order, "client");
      if (!response.ok) {
        throw new Error(``);
      }
      console.log("Nice");

    }
  }

  function handleCancel() {
    cleanCar();
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4 text-[var(--orange)]">Your Order</h1>
      <CarDropDown tiny={false} />
      <div className="mt-6 border-t pt-4">
        <div className="flex space-x-4">
          <button
            onClick={handleBuy}
            className="flex-1 bg-[var(--orange)] text-white py-2 
            rounded hover:bg-orange-700 transition-colors"
          >
            Buy
          </button>
          <button
            onClick={handleCancel}
            className="flex-1 bg-gray-500
            text-white py-2 rounded hover:bg-gray-800 transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
