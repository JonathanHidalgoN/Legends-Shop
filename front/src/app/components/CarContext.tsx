"use client";

import React, { createContext, useContext, useState } from "react";
import { Item } from "../interfaces/Item";
import { CartItem, CartStatus } from "../interfaces/Order";

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
  addOneItemToCar: (carItem: CartItem) => void;
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
  function addOneItemToCar(cartItem: CartItem): void {
    setCarItems([...carItems, cartItem]);
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
