"use client"

import React, { createContext, useContext, useState } from "react";
import { Item } from "../interfaces/Item";

interface CarContextType {
  carItems: Item[];
  setCarItems: (items: Item[]) => void;
}

const CarContext = createContext<CarContextType | undefined>(undefined);

export function CarContextProvider({ children }: { children: React.ReactNode }) {
  const [carItems, setCarItems] = useState<Item[]>([]);

  return (
    <CarContext.Provider value={{ carItems: carItems, setCarItems: setCarItems }}>
      {children}
    </CarContext.Provider>
  );
}

export function useCarContext() {
  const context = useContext(CarContext);
  if (!context) {
    throw new Error("context user error");
  }
  return context;
}
