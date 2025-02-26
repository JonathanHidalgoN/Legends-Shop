"use client";
import { useCarContext } from "../components/CarContext";
import CarDropDown from "../components/CarDropDown";

export default function OrderPage() {
  const { carItems, setCarItems } = useCarContext();


  function handleBuy() {
    console.log("Buy button clicked");
  }

  function handleCancel() {
    setCarItems([]);
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
