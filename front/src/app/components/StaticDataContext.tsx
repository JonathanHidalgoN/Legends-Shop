"use client";
import React, { createContext, useContext } from "react";
import { Item } from "../interfaces/Item";
import { Location } from "../interfaces/Location";

interface StaticDataContextType {
  items: Item[];
  tags: string[];
  effects: string[];
  locations: Location[];
}

const StaticDataContext = createContext<StaticDataContextType | undefined>(
  undefined,
);

export function StaticDataContextProvider({
  items,
  tags,
  effects,
  locations,
  children,
}: {
  items: Item[];
  tags: string[];
  effects: string[];
  locations: Location[];
  children: React.ReactNode;
}) {
  return (
    <StaticDataContext.Provider value={{ items, tags, effects, locations }}>
      {children}
    </StaticDataContext.Provider>
  );
}

export function useStaticData() {
  const context = useContext(StaticDataContext);
  if (!context) {
    throw new Error("useItems error");
  }
  return context;
}
