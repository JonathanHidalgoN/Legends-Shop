"use client"

import React, { createContext, useContext, useState } from "react";

interface AuthContextType {
  userName: string | null;
  setUserName: (userName: string | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthContextProvider({ children }: { children: React.ReactNode }) {
  const [userName, setUser] = useState<string | null>(null);

  return (
    <AuthContext.Provider value={{ userName: userName, setUserName: setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("context user error");
  }
  return context;
}
