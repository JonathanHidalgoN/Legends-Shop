"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import {
  FromValues,
  logInRequest,
  logoutRequest,
  refreshTokenRequest,
  singupRequest,
} from "../request";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import {
  APILoginResponse,
  APISingupResponse,
  LoginError,
  SingupError,
} from "../interfaces/APIResponse";
import { showErrorToast } from "../customToast";
import { useLoading } from "./LoadingRequestContext";

interface AuthContextType {
  userName: string | null;
  setUserName: (userName: string | null) => void;
  login: (userName: string, password: string) => Promise<APILoginResponse>;
  logOut: () => void;
  refreshToken: () => Promise<void>;
  singup: (
    userName: string,
    password: string,
    email: string,
    birthDate: Date,
    location_id: number,
  ) => Promise<APISingupResponse>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [userName, setUserName] = useState<string | null>(null);
  const router = useRouter();
  const { startLoading, stopLoading } = useLoading();

  function createAPIResponseLogin(
    response: Response,
    data: any,
  ): APILoginResponse {
    if (!response.ok) {
      if (!data) {
        throw new Error(
          "You need the data to create the api response if the status is not ok",
        );
      } else {
        const errorTypeHeader: string | null =
          response.headers.get("X-Error-Type");
        let errorType: LoginError | null = null;
        if (errorTypeHeader === LoginError.INVALIDUSERNAME) {
          errorType = LoginError.INVALIDUSERNAME;
        }
        if (errorTypeHeader === LoginError.INCORRECTCREDENTIALS) {
          errorType = LoginError.INCORRECTCREDENTIALS;
        }
        if (errorTypeHeader === LoginError.INVALIDPASSWORD) {
          errorType = LoginError.INVALIDPASSWORD;
        }
        if (errorTypeHeader === LoginError.INTERNALSERVERERROR) {
          errorType = LoginError.INTERNALSERVERERROR;
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

  async function login(
    userName: string,
    password: string,
  ): Promise<APILoginResponse> {
    startLoading();
    const response = await logInRequest(userName, password, FromValues.CLIENT);
    stopLoading();
    if (!response.ok) {
      const data = await response.json();
      const result: APILoginResponse = createAPIResponseLogin(response, data);
      if (result.status == 401) {
        showErrorToast(result.message);
      } else if (result.status == 500) {
        showErrorToast("Internal server error login");
      } else {
        showErrorToast("Unexpected error");
      }
      return result;
    }
    const result: APILoginResponse = createAPIResponseLogin(response, null);
    setUserName(userName);
    toast.success(`Welcome ${userName}!`);
    return result;
  }
  function createAPIResponseSingup(
    response: Response,
    data: any,
  ): APISingupResponse {
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
        if (errorTypeHeader === SingupError.INTERNALSERVERERROR) {
          errorType = SingupError.INTERNALSERVERERROR;
        }
        if (errorTypeHeader === SingupError.INVALIDUSERGOLD) {
          errorType = SingupError.INVALIDUSERGOLD;
        }
        if (errorTypeHeader === SingupError.INVALIDUSERNAME) {
          errorType = SingupError.INVALIDUSERNAME;
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
        if (errorTypeHeader === SingupError.INVALIDPASSWORD) {
          errorType = SingupError.INVALIDPASSWORD;
        }
        if (errorTypeHeader === SingupError.INVALIDLOCATION) {
          errorType = SingupError.INVALIDLOCATION;
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
    location_id: number,
  ): Promise<APISingupResponse> {
    const response = await singupRequest(
      userName,
      password,
      email,
      birthDate,
      location_id,
      FromValues.CLIENT,
    );
    const data = await response.json();
    return createAPIResponseSingup(response, data);
  }

  async function refreshToken(): Promise<void> {
    try {
      const response = await refreshTokenRequest(FromValues.CLIENT);
      if (!response.ok) {
        logOut();
        return;
      }
      await response.json();
    } catch (error) {
      showErrorToast("Internal server error refreshing token");
    }
  }

  async function logOut() {
    try {
      const response = await logoutRequest(FromValues.CLIENT);
      if (!response.ok) {
        throw new Error("Logout failed");
      }
      setUserName(null);
      router.push("/");
      toast.success(`Logout succesfully`);
    } catch (error) {}
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
