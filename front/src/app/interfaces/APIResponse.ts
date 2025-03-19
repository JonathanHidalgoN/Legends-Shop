export enum SingupError {
  USERNAMEEXIST = "USERNAMEEXIST",
  EMAILEXIST = "EMAILEXIST",
  INVALIDEMAIL = "INVALIDEMAIL",
  INVALIDDATE = "INVALIDDATE",
  INVALIDUSERNAME = "INVALIDUSERNAME",
  INVALIDUSERGOLD = "INVALIDUSERGOLD",
  INTERNALSERVERERROR = "INTERNALSERVERERROR"
}

export enum LoginError {
  INVALIDUSERNAME = "INVALIDUSERNAME",
  INVALIDPASSWORD = "INVALIDPASSWORD",
  INCORRECTCREDENTIALS = "INCORRECTCREDENTIALS",
  INTERNALSERVERERROR = "INTERNALSERVERERROR"
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
