"use client";

import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import { Item } from "../interfaces/Item";
import { CartItem, CartStatus } from "../interfaces/Order";
import { useAuthContext } from "./AuthContext";
import { APICartItemResponse } from "../interfaces/APIResponse";
import { addToCarRequest, deleteCartItemRequest, getDeliveryDatesRequest } from "../request";
import { mapAPICartItemResponseToCartItem } from "../mappers";
import {
  showErrorToast,
  showSuccessToast,
  showWarningToast,
} from "../customToast";
import { Location } from "../interfaces/Location";
import { DeliveryDate } from "../interfaces/DeliveryDate";
import { useStaticData } from "./StaticDataContext";

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
  handleClientAddingItemToCar: (item: Item) => Promise<void>;
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
  currentLocation: Location | null;
  setCurrentLocation: (location: Location) => void;
  deliveryDates: DeliveryDate[];
  setDeliveryDates: (dates: DeliveryDate[]) => void;
}

const CarContext = createContext<CarContextType | undefined>(undefined);

export function CarContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [currentGold, setCurrentGold] = useState<number | null>(null);
  const [currentLocation, setCurrentLocation] = useState<Location | null>(null);
  const [deliveryDates, setDeliveryDates] = useState<DeliveryDate[]>([]);
  const { userName } = useAuthContext();
  const { locations, items } = useStaticData();

  let cartItemsNotInServerCount = useRef<number>(0);
  let pendingServerDeletedCartItems = useRef<CartItem[]>([]);
  const isAuthenticated: boolean = userName !== null;

  useEffect(() => {
    if (locations.length > 0) {
      setCurrentLocation(locations[0]);
    }
  }, [locations]);

  useEffect(() => {
    if (currentLocation && items.length > 0) {
      const locationId = currentLocation.id;
      const currentDeliveryLocationId = deliveryDates[0]?.locationId;
      
      if (!currentDeliveryLocationId || currentDeliveryLocationId !== locationId) {
        fetchDeliveryDates();
      }
    }
  }, [currentLocation, cartItems]);

  async function fetchDeliveryDates() {
    if (!currentLocation) return;

    try {
      const dates = await getDeliveryDatesRequest(
        currentLocation.id
      );
      setDeliveryDates(dates);
    } catch (error) {
      console.error("Error fetching delivery dates:", error);
      showErrorToast("Failed to fetch delivery dates");
    }
  }

  async function addInClientCarItemsToServer(
    cartItem: CartItem,
  ): Promise<CartItem | null> {
    try {
      const apiCartItem: APICartItemResponse = {
        id: null,
        status: CartStatus.INCLIENT,
        itemId: cartItem.item.id,
      };
      const serverCartItemResponse: APICartItemResponse = await addToCarRequest(
        "client",
        apiCartItem,
        `Error adding ${cartItem.item.name} to car`,
      );
      const serverCartItem: CartItem = mapAPICartItemResponseToCartItem(
        serverCartItemResponse,
        cartItem.item,
      );
      return serverCartItem;
    } catch (error) {
      return null;
    }
  }

  async function handleClientAddingItemToCar(item: Item): Promise<void> {
    const warningFlagTurn: boolean = cartItemsNotInServerCount.current % 5 == 0;
    let cartItem: CartItem = {
      id: null,
      status: CartStatus.INCLIENT,
      item: item,
    };
    if (!isAuthenticated) {
      if (warningFlagTurn) {
        showWarningToast(`Tip: Login so we can remember your cart`);
      }
      cartItemsNotInServerCount.current = cartItemsNotInServerCount.current + 1;
    } else {
      const serverCartItem = await addInClientCarItemsToServer(cartItem);
      if (!serverCartItem) {
        return;
      }
      cartItem = serverCartItem;
    }
    setCartItems([...cartItems, cartItem]);
    if (isAuthenticated || !warningFlagTurn) {
      showSuccessToast(`${cartItem.item.name} added to cart`);
    }
  }

  async function checkIfAddCartItemIdToPendingToDeleteList(cartItem: CartItem) {
    if (cartItem.status == CartStatus.ADDED && cartItem.id) {
      if (isAuthenticated) {
        try {
          await deleteCartItemRequest(
            "client",
            cartItem.id,
            `Error deleting ${cartItem.item.name}`,
          );
          return;
        } catch (error) {
          //The request display the error msg, then add to the list the item pending to delete
          //maybe add a timer to try again?
        }
      }
      pendingServerDeletedCartItems.current.push(cartItem);
    }
  }

  useEffect(() => {
    async function handleLoginWithCartClientItems(): Promise<void> {
      const updatedItems = await Promise.all(
        cartItems.map(async (cartItem) => {
          if (cartItem.status === CartStatus.INCLIENT) {
            const serverCartItem = await addInClientCarItemsToServer(cartItem);
            return serverCartItem ? serverCartItem : cartItem;
          }
          return cartItem;
        }),
      );
      setCartItems(updatedItems);
    }

    async function handleLoginWithPendingItemsToDelete(): Promise<void> {
      const newPending: CartItem[] = [];
      for (const cartItem of pendingServerDeletedCartItems.current) {
        if (cartItem.id) {
          try {
            await deleteCartItemRequest(
              "client",
              cartItem.id,
              `Error deleting ${cartItem.item.name}`,
            );
          } catch (error) {
            newPending.push(cartItem);
          }
        } else {
          newPending.push(cartItem);
        }
      }
      pendingServerDeletedCartItems.current = newPending;
    }

    if (isAuthenticated) {
      handleLoginWithCartClientItems();
      handleLoginWithPendingItemsToDelete();
    }
  }, [isAuthenticated]);

  /**
   * Removes one instance of an item from the cart.
   * If multiple instances exist, only the first occurrence is removed.
   * @param item - The item to remove.
   */
  function deleteOneItemFromCar(item: Item): void {
    const index = cartItems.findIndex((i) => i.item.id === item.id);
    if (index !== -1) {
      const selectedCartItem: CartItem | undefined = cartItems.at(index);
      //Have to do the if for the liner ):
      if (selectedCartItem) {
        checkIfAddCartItemIdToPendingToDeleteList(selectedCartItem);
      }
      setCartItems([
        ...cartItems.slice(0, index),
        ...cartItems.slice(index + 1),
      ]);
    }
  }

  /**
   * Removes all instances of a given item from the cart.
   * @param item - The item to remove.
   */
  function deleteAllItemFromCar(item: Item): void {
    const filterCartItems: CartItem[] = cartItems.filter(
      (i: CartItem) => i.item.id !== item.id,
    );
    filterCartItems.forEach((cartItem: CartItem) =>
      checkIfAddCartItemIdToPendingToDeleteList(cartItem),
    );
    setCartItems(cartItems.filter((i: CartItem) => i.item.id !== item.id));
  }

  /**
   * Calculates the total cost of items in the cart.
   * Sums up the cost of each item based on its gold.base value.
   * @returns The total cost as a number.
   */
  function getTotalCost(): number {
    return cartItems.reduce((total, item) => total + item.item.gold.base, 0);
  }

  /**
   * Deletes all car items
   */
  function cleanCar(): void {
    cartItems.forEach((cartItem: CartItem) =>
      checkIfAddCartItemIdToPendingToDeleteList(cartItem),
    );
    setCartItems([]);
  }

  return (
    <CarContext.Provider
      value={{
        carItems: cartItems,
        setCarItems: setCartItems,
        deleteOneItemFromCar,
        deleteAllItemFromCar,
        handleClientAddingItemToCar,
        getTotalCost,
        cleanCar,
        currentGold,
        setCurrentGold,
        currentLocation,
        setCurrentLocation,
        deliveryDates,
        setDeliveryDates,
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
