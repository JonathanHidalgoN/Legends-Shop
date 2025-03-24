"use client";

import React, { createContext, useContext, useState } from "react";
import { Item } from "../interfaces/Item";
import { CartItem, CartStatus } from "../interfaces/Order";
import { useAuthContext } from "./AuthContext";
import { APICartItemResponse } from "../interfaces/APIResponse";
import { addToCarRequest } from "../request";
import { mapAPICartItemResponseToCartItem } from "../mappers";
import { showErrorToast, showSuccessToast, showWarningToast } from "../customToast";

interface CarContextType {
  carItems: CartItem[];
  setCarItems: (cartItems: CartItem[]) => void;
  /**
   * Deletes one instance of an item from the cart.
   * @param item - The item to be removed.
   */
  deleteOneItemFromCar: (item: Item) => void;
  /**
   * Deletes all instances of a specific item from the cart.
   * @param item - The item to remove completely.
   */
  deleteAllItemFromCar: (item: Item) => void;
  /**
   * Adds one instance of an item to the cart.
   * @param item - The item to add.
   */
  addOneItemToCar: (item: Item) => Promise<void>;
  /**
   * Calculates and returns the total cost of all items in the cart.
   * Assumes each item has a cost defined in item.gold.base.
   * @returns The total cost.
   */
  getTotalCost: () => number;

  /**
   * Deletes all car items
   */
  cleanCar: () => void;
  currentGold: number | null;
  setCurrentGold: (value: number | null) => void;
}

const CarContext = createContext<CarContextType | undefined>(undefined);

export function CarContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [carItems, setCarItems] = useState<CartItem[]>([]);
  const [currentGold, setCurrentGold] = useState<number | null>(null);
  const [carItemsNotInServerCount, setCarItemsNotInServerCout] = useState<number>(0);
  const { userName } = useAuthContext();
  const isAuthenticated: boolean = userName !== null;

  /**
   * Removes one instance of an item from the cart.
   * If multiple instances exist, only the first occurrence is removed.
   * @param item - The item to remove.
   */
  function deleteOneItemFromCar(item: Item): void {
    const index = carItems.findIndex((i) => i.item.id === item.id);
    if (index !== -1) {
      setCarItems([...carItems.slice(0, index), ...carItems.slice(index + 1)]);
    }
  }

  /**
   * Removes all instances of a given item from the cart.
   * @param item - The item to remove.
   */
  function deleteAllItemFromCar(item: Item): void {
    setCarItems(carItems.filter((i: CartItem) => i.item.id !== item.id));
  }

  /**
   * Adds one instance of an item to the cart.
   * @param item - The item to add.
   */
  async function addOneItemToCar(item: Item): Promise<void> {
    if (isAuthenticated) {
      const apiCartItem: APICartItemResponse = {
        id: null,
        status: CartStatus.PENDING,
        itemId: item.id
      };
      try {
        const data: APICartItemResponse = await addToCarRequest("client", apiCartItem);
        const mappedCartItem: CartItem = mapAPICartItemResponseToCartItem(data, item);
        setCarItems([...carItems, mappedCartItem]);
        showSuccessToast(`${mappedCartItem.item.name} added to car`)
      } catch (error) {
        showErrorToast(`${item.name} could not be added to the car`)
      }
    } else {
      if (carItemsNotInServerCount % 5 == 0) {
        showWarningToast(`Login so we can remember you added ${item.name} to car`)
      }
      const cartItem: CartItem = {
        id: null,
        status: CartStatus.ADDED,
        item: item
      }
      setCarItems([...carItems, cartItem]);
      setCarItemsNotInServerCout(carItemsNotInServerCount + 1);
      showSuccessToast(`${cartItem.item.name} added to car`)
    }
  }

  /**
   * Calculates the total cost of items in the cart.
   * Sums up the cost of each item based on its gold.base value.
   * @returns The total cost as a number.
   */
  function getTotalCost(): number {
    return carItems.reduce((total, item) => total + item.item.gold.base, 0);
  }

  /**
   * Deletes all car items
   */
  function cleanCar(): void {
    setCarItems([]);
  }

  return (
    <CarContext.Provider
      value={{
        carItems,
        setCarItems,
        deleteOneItemFromCar,
        deleteAllItemFromCar,
        addOneItemToCar,
        getTotalCost,
        cleanCar,
        currentGold,
        setCurrentGold,
      }}
    >
      {children}
    </CarContext.Provider>
  );
}

export function useCarContext() {
  const context = useContext(CarContext);
  if (!context) {
    throw new Error("CarContext must be used within a CarContextProvider");
  }
  return context;
}
