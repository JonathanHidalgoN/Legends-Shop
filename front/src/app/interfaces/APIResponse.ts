export enum SingupError {
  USERNAMEEXIST = "USERNAMEEXIST",
  EMAILEXIST = "EMAILEXIST",
  INVALIDEMAIL = "INVALIDEMAIL",
  INVALIDDATE = "INVALIDDATE"
}

export interface APIResponse {
  status: number;
  errorType: SingupError | null;
  message: string;
}

