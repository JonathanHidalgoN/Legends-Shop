"use client";

import React, { createContext, useContext, useState } from "react";
import { Item } from "../interfaces/Item";

interface CarContextType {
  carItems: Item[];
  setCarItems: (items: Item[]) => void;
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
  addOneItemToCar: (item: Item) => void;
  /**
   * Calculates and returns the total cost of all items in the cart.
   * Assumes each item has a cost defined in item.gold.base.
   * @returns The total cost.
   */
  getTotalCost: () => number;
}

const CarContext = createContext<CarContextType | undefined>(undefined);

export function CarContextProvider({ children }: { children: React.ReactNode }) {
  const [carItems, setCarItems] = useState<Item[]>([]);

  /**
   * Removes one instance of an item from the cart.
   * If multiple instances exist, only the first occurrence is removed.
   * @param item - The item to remove.
   */
  function deleteOneItemFromCar(item: Item): void {
    const index = carItems.findIndex(cartItem => cartItem.name === item.name);
    if (index !== -1) {
      setCarItems([...carItems.slice(0, index), ...carItems.slice(index + 1)]);
    }
  }

  /**
   * Removes all instances of a given item from the cart.
   * @param item - The item to remove.
   */
  function deleteAllItemFromCar(item: Item): void {
    setCarItems(carItems.filter((carItem: Item) => carItem.name !== item.name));
  }

  /**
   * Adds one instance of an item to the cart.
   * @param item - The item to add.
   */
  function addOneItemToCar(item: Item): void {
    setCarItems([...carItems, item]);
  }

  /**
   * Calculates the total cost of items in the cart.
   * Sums up the cost of each item based on its gold.base value.
   * @returns The total cost as a number.
   */
  function getTotalCost(): number {
    return carItems.reduce((total, item) => total + item.gold.base, 0);
  }

  return (
    <CarContext.Provider value={{
      carItems,
      setCarItems,
      deleteOneItemFromCar,
      deleteAllItemFromCar,
      addOneItemToCar,
      getTotalCost
    }}>
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
