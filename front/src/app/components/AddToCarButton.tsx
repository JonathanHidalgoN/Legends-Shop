import { Item } from "../interfaces/Item";
import { useCarContext } from "./CarContext";
import { showSuccessToast } from "../customToast";
import { CartItem, CartStatus } from "../interfaces/Order";
import { APICartItemResponse } from "../interfaces/APIResponse";
import useSWR from "swr";
import { addToCarRequest } from "../request";
import { useErrorRedirect } from "./useErrorRedirect";
import { mapAPICartItemResponseToCartItem } from "../mappers";
import { useState } from "react";

export default function AddToCarButton({ item }: { item: Item }) {
  const { addOneItemToCar } = useCarContext();

  async function handleAddToCarButton() {
    const apiCartItem: APICartItemResponse = {
      id: null,
      status: CartStatus.PENDING,
      itemId: item.id
    };
    try {
      console.log("here");
      const data: APICartItemResponse = await addToCarRequest("client", apiCartItem);
      const cartItem: CartItem = mapAPICartItemResponseToCartItem(apiCartItem, item);
      addOneItemToCar(cartItem);
      showSuccessToast(`${item.name} added to car`)
    } catch (error) {

    }

  }



  return (
    <div>
      <button
        className="mt-6 bg-[var(--orange)] text-[var(--white)] 
      px-6 py-3 rounded hover:bg-[var(--pink1)] transition-colors"
        onClick={handleAddToCarButton}
      >
        Add to Car
      </button>
    </div>
  );
}
