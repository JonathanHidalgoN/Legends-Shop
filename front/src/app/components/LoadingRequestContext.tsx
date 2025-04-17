"use client";
import React, { createContext, useContext, useState } from "react";

type LoadingContextType = {
  loadingCount: number;
  startLoading: () => void;
  stopLoading: () => void;
  isLoading: boolean;
  setIsLoading: (isLoading: boolean) => void;
};

const LoadingContext = createContext<LoadingContextType | undefined>(undefined);

export function LoadingProvider({ children }: { children: React.ReactNode }) {
  const [loadingCount, setLoadingCount] = useState(0);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const startLoading = () => setLoadingCount((c) => c + 1);
  const stopLoading = () => setLoadingCount((c) => Math.max(0, c - 1));

  return (
    <LoadingContext.Provider
      value={{
        loadingCount,
        startLoading,
        stopLoading,
        isLoading,
        setIsLoading,
      }}
    >
      {children}
      {loadingCount > 0 && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="relative p-6 rounded-lg">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-[var(--orange)]"></div>
            <div className="mt-4 text-white text-lg font-semibold">
              Loading...
            </div>
          </div>
        </div>
      )}
    </LoadingContext.Provider>
  );
}

export const useLoading = (): LoadingContextType => {
  const context = useContext(LoadingContext);
  if (!context)
    throw new Error("useLoading must be used within a LoadingProvider");
  return context;
};
