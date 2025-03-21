import { OrderSummary } from "./Order";

export enum SingupError {
  USERNAMEEXIST = "USERNAMEEXIST",
  EMAILEXIST = "EMAILEXIST",
  INVALIDEMAIL = "INVALIDEMAIL",
  INVALIDDATE = "INVALIDDATE",
  INVALIDUSERNAME = "INVALIDUSERNAME",
  INVALIDUSERGOLD = "INVALIDUSERGOLD",
  INTERNALSERVERERROR = "INTERNALSERVERERROR",
  INVALIDPASSWORD = "INVALIDPASSWORD",
}

export enum LoginError {
  INVALIDUSERNAME = "INVALIDUSERNAME",
  INVALIDPASSWORD = "INVALIDPASSWORD",
  INCORRECTCREDENTIALS = "INCORRECTCREDENTIALS",
  INTERNALSERVERERROR = "INTERNALSERVERERROR",
}

export interface APISingupResponse {
  status: number;
  errorType: SingupError | null;
  message: string;
}

export interface APILoginResponse {
  status: number;
  errorType: LoginError | null;
  message: string;
}

export interface UserInfo {
  userName: string;
  email: string;
  cretead: Date;
  lastSingIn: Date;
  goldSpend: number;
  currentGold: number;
  birthDate: Date;
}

export interface ProfileInfo {
  user: UserInfo;
  ordersInfo: OrderSummary[];
}
