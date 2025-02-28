"use client"

import React, { createContext, useContext, useState } from "react";
import { logInRequest, logoutRequest } from "../request";
import { useRouter } from "next/navigation";
import toast from 'react-hot-toast';

interface AuthContextType {
  userName: string | null;
  setUserName: (userName: string | null) => void;
  logIn: (userName: string, password: string) => void;
  logOut: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthContextProvider({ children }: { children: React.ReactNode }) {
  const [userName, setUserName] = useState<string | null>(null);
  const router = useRouter();

  async function logIn(userName: string, password: string) {
    try {
      const response = await logInRequest(userName, password, "client");
      if (!response.ok) {
        throw new Error(``);
      }
      const data = await response.json()
      if (!("access_token" in data) || !("token_type" in data) ||
        data.token_type !== "bearer") {
        throw new Error(``);
      }
      setUserName(userName);
      router.push("/");
      toast.success(`Welcome ${userName}!`)
    } catch (error) {
      toast.error("Error in the login process")
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

  return (
    <AuthContext.Provider value={{ userName, setUserName, logOut, logIn }}>
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
