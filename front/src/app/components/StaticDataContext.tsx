"use client";
import React, { createContext, useContext } from "react";
import { Item } from "../interfaces/Item";

interface StaticDataContextType {
  items: Item[];
  tags: string[];
}

const StaticDataContext = createContext<StaticDataContextType | undefined>(
  undefined,
);

export function StaticDataContextProvider({
  items,
  tags,
  children,
}: {
  items: Item[];
  tags: string[];
  children: React.ReactNode;
}) {
  return (
    <StaticDataContext.Provider value={{ items, tags }}>
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
