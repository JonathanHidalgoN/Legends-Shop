"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { logInRequest, logoutRequest, refreshTokenRequest } from "../request";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";

interface AuthContextType {
  userName: string | null;
  setUserName: (userName: string | null) => void;
  login: (userName: string, password: string) => Promise<number>;
  logOut: () => void;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [userName, setUserName] = useState<string | null>(null);
  const router = useRouter();

  async function login(userName: string, password: string): Promise<number> {
    const response = await logInRequest(userName, password, "client");
    if (!response.ok) {
      if (response.status == 401) {
        toast.error("Incorrect username or password");
      } else if (response.status == 500) {
        toast.error("Internal server error login");
      } else {
        toast.error("Unexpected error");
      }
      return response.status;
    }
    setUserName(userName);
    toast.success(`Welcome ${userName}!`);
    return response.status;
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
      console.log(error);
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
      toast.success(`Logout succesfully`);
    } catch (error) {
      console.log("Error");
    }
  }

  useEffect(() => {
    if (!userName) return;
    const refreshInterval = setInterval(
      () => {
        refreshToken();
      },
      29 * 60 * 1000,
    );
    return () => clearInterval(refreshInterval);
  }, [userName]);

  return (
    <AuthContext.Provider
      value={{
        userName,
        setUserName,
        logOut,
        login,
        refreshToken,
      }}
    >
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
