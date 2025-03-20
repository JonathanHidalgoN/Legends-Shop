import { RefObject } from "react";
import { ValidationResult } from "./interfaces/Errors";

// source: https://stackoverflow.com/questions/32553158/detect-click-outside-react-component
export function handleClickOutside(
  event: MouseEvent,
  ref: RefObject<HTMLDivElement | null>,
  noShowSetFunction: (value: boolean) => void,
) {
  if (ref.current && !ref.current.contains(event.target as Node)) {
    noShowSetFunction(false);
  }
}

export function validateUsernameInput(username: string): ValidationResult {
  let errorMsg: string | null = "";
  let valid: boolean = true;
  const validLen: boolean = username.length >= 8;
  if (!validLen) {
    errorMsg = "username is less than 8 characters";
  }
  valid = validLen && true;
  const finalMsg: string | null = valid ? null : errorMsg;
  return {
    valid: valid,
    input: "username",
    msg: finalMsg,
  };
}

export function validatePasswordInput(password: string): ValidationResult {
  let errorMsg: string | null = "";
  let valid: boolean = true;
  const validLen: boolean = password.length >= 8;
  if (!validLen) {
    errorMsg = "password is less than 8 characters";
  }
  valid = validLen && true;
  const finalMsg: string | null = valid ? null : errorMsg;
  return {
    valid: valid,
    input: "password",
    msg: finalMsg,
  };
}

export function validateEmailInput(email: string): ValidationResult {
  let errorMsg: string | null = "";
  let valid: boolean = true;
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const validPattern: boolean = pattern.test(email);
  if (!validPattern) {
    errorMsg = "invalid email pattern";
  }
  valid = validPattern && true;
  const finalMsg: string | null = valid ? null : errorMsg;
  return {
    valid: valid,
    input: "email",
    msg: finalMsg,
  };
}
