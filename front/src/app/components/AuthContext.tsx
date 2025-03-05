"use client"

import React, { createContext, useContext, useEffect, useState } from "react";
import { logInRequest, logoutRequest, refreshTokenRequest } from "../request";
import { useRouter } from "next/navigation";
import toast from 'react-hot-toast';

interface AuthContextType {
  userName: string | null;
  setUserName: (userName: string | null) => void;
  logIn: (userName: string, password: string) => Promise<boolean>;
  logOut: () => void;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthContextProvider({ children }: { children: React.ReactNode }) {
  const [userName, setUserName] = useState<string | null>(null);
  const router = useRouter();

  async function logIn(userName: string, password: string): Promise<boolean> {
    const response = await logInRequest(userName, password, "client");
    if (!response.ok) {
      toast.error("Login error");
      return false;
    }
    setUserName(userName);
    toast.success(`Welcome ${userName}!`)
    return true;
  }

  async function refreshToken(): Promise<void> {
    try {
      const response = await refreshTokenRequest("client");
      if (!response.ok) {
        logOut();
        return;
      }
      await response.json();
    } catch (error) {
      toast.error("Internal server error refreshing token");
    }
  }

  async function logOut() {
    try {
      const response = await logoutRequest("client");
      if (!response.ok) {
        throw new Error("Logout failed");
      }
      setUserName(null);
      router.push("/");
      toast.success(`Logout succesfully`)
    } catch (error) {
      console.log("Error");
    }
  }

  useEffect(() => {
    if (!userName) return;
    const refreshInterval = setInterval(() => {
      refreshToken();
    }, 29 * 60 * 1000);
    return () => clearInterval(refreshInterval);
  }, [userName])

  return (
    <AuthContext.Provider value={{ userName, setUserName, logOut, logIn, refreshToken }}>
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
