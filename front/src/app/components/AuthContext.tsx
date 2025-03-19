"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import {
  logInRequest,
  logoutRequest,
  refreshTokenRequest,
  singupRequest,
} from "../request";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import { APIResponse, SingupError } from "../interfaces/APIResponse";

interface AuthContextType {
  userName: string | null;
  setUserName: (userName: string | null) => void;
  login: (userName: string, password: string) => Promise<number>;
  logOut: () => void;
  refreshToken: () => Promise<void>;
  singup: (
    userName: string,
    password: string,
    email: string,
    birthDate: Date,
  ) => Promise<APIResponse>;
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

  function createAPIResponseSingup(response: Response, data: any): APIResponse {
    if (!response.ok) {
      if (!data) {
        throw new Error(
          "You need the data to create the api response if the status is not ok",
        );
      } else {
        const errorTypeHeader: string | null =
          response.headers.get("X-Error-Type");
        let errorType: SingupError | null = null;
        if (errorTypeHeader === SingupError.EMAILEXIST) {
          errorType = SingupError.EMAILEXIST;
        }
        if (errorTypeHeader === SingupError.INVALIDEMAIL) {
          errorType = SingupError.INVALIDEMAIL;
        }
        if (errorTypeHeader === SingupError.USERNAMEEXIST) {
          errorType = SingupError.USERNAMEEXIST;
        }
        if (errorTypeHeader === SingupError.INVALIDDATE) {
          errorType = SingupError.INVALIDDATE;
        }
        return {
          status: response.status,
          errorType: errorType,
          message: data.detail ? data.detail : "Error",
        };
      }
    } else {
      return {
        status: response.status,
        errorType: null,
        message: "Success",
      };
    }
  }

  async function singup(
    userName: string,
    password: string,
    email: string,
    birthDate: Date,
  ): Promise<APIResponse> {
    const response = await singupRequest(
      userName,
      password,
      email,
      birthDate,
      "client",
    );
    if (!response.ok) {
      const data = await response.json();
      const result: APIResponse = createAPIResponseSingup(response, data);
      if (result.status == 400) {
        toast.error(result.message);
      } else if (result.status == 500) {
        toast.error("Internal server error login");
      } else {
        toast.error("Unexpected error");
      }
      return result;
    }
    const result: APIResponse = createAPIResponseSingup(response, null);
    toast.success(`Singup succesfully ${userName}!`);
    await login(userName, password);
    return result;
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
        singup,
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
