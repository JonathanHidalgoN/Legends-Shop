"use client";

import { useAuthContext } from "@/app/components/AuthContext";
import { showErrorToast } from "@/app/customToast";
import {
  validateEmailInput,
  validatePasswordInput,
  validateUsernameInput,
} from "@/app/functions";
import { APISingupResponse, SingupError } from "@/app/interfaces/APIResponse";
import {
  defaultValidationResult,
  ValidationResult,
} from "@/app/interfaces/Errors";
import { useRouter } from "next/navigation";
import { useState } from "react";
import toast from "react-hot-toast";

export default function SingupPage() {
  const { singup } = useAuthContext();
  const router = useRouter();

  const [formUserName, setFormUserName] = useState<string>("");
  const [formPassword1, setFormPassword1] = useState<string>("");
  const [formPassword2, setFormPassword2] = useState<string>("");
  const [formEmail, setFormEmail] = useState<string>("");
  const [formBirthDate, setFormBirthDate] = useState<string>("");
  const [singupApiError, setSingupApiError] = useState<SingupError | null>(
    null,
  );
  const [differentPassword, setDifferentPassword] = useState<boolean>(false);
  const [validUsernameInput, setValidUsernameInput] =
    useState<ValidationResult>(defaultValidationResult);
  const [validEmailInput, setValidEmailInput] = useState<ValidationResult>(
    defaultValidationResult,
  );
  const [validPasswordInput, setValidPasswordInput] =
    useState<ValidationResult>(defaultValidationResult);

  function passwordsInputHandleChange(p1: string, p2: string): void {
    const different: boolean = p1 != p2;
    setDifferentPassword(different);
    setFormPassword2(p2);
    setFormPassword1(p1);
    if (!different) {
      const validInput: ValidationResult = validatePasswordInput(p1);
      setValidPasswordInput(validInput);
    }
  }

  function emailInputHandleChange(email: string): void {
    const validInput: ValidationResult = validateEmailInput(email);
    setFormEmail(email);
    setValidEmailInput(validInput);
  }

  function usernameInputHandleChange(username: string): void {
    const validInput: ValidationResult = validateUsernameInput(username);
    setFormUserName(username);
    setValidUsernameInput(validInput);
  }

  async function handleSingupSubmit(e: any): Promise<void> {
    e.preventDefault();
    if (formPassword1 !== formPassword2) {
      showErrorToast("Passwords do not match!");
      setDifferentPassword(true);
      return;
    } else {
      setDifferentPassword(false);
    }
    const birthDate = new Date(formBirthDate);
    const responseStatus: APISingupResponse = await singup(
      formUserName,
      formPassword1,
      formEmail,
      birthDate,
    );
    if (responseStatus.status === 200) {
      router.push("/");
      setFormUserName("");
      setFormEmail("");
      setFormBirthDate("");
      setFormPassword1("");
      setFormPassword2("");
      setSingupApiError(null);
    } else if (responseStatus.status === 400) {
      setSingupApiError(responseStatus.errorType);
    }
  }

  const emptyFields: boolean =
    formPassword1 === "" ||
    formUserName === "" ||
    formPassword2 === "" ||
    formEmail === "" ||
    formBirthDate === "";

  const canSubmit: boolean =
    validEmailInput.valid &&
    validPasswordInput.valid &&
    validUsernameInput.valid &&
    !differentPassword &&
    !emptyFields;

  return (
    <div className="bg-[var(--white)] min-h-screen flex flex-col items-center justify-center p-4">
      <h1 className="text-3xl text-[var(--orange)] font-bold mb-6">Sing up!</h1>
      <form onSubmit={handleSingupSubmit} className="w-full max-w-md space-y-4">
        <div className="flex flex-col">
          <label
            htmlFor="username"
            className="mb-1 font-bold text-[var(--orange)]"
          >
            Username
          </label>
          <input
            id="username"
            name="username"
            placeholder="Username"
            value={formUserName}
            onChange={(e) => usernameInputHandleChange(e.target.value)}
            className={`border p-2 rounded ${singupApiError || !validUsernameInput.valid ? "border-red-500" : ""}`}
          />
          {!validUsernameInput.valid && (
            <span className="text-red-500 text-sm mt-1">
              {validUsernameInput.msg}
            </span>
          )}
          {singupApiError === SingupError.USERNAMEEXIST && (
            <span className="text-red-500 text-sm mt-1">
              Username exist, change it
            </span>
          )}
          {singupApiError === SingupError.INVALIDUSERNAME && (
            <span className="text-red-500 text-sm mt-1">Invalid username</span>
          )}
        </div>

        <div className="flex flex-col">
          <label
            htmlFor="email"
            className="mb-1 font-bold text-[var(--orange)]"
          >
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            placeholder="Email"
            value={formEmail}
            onChange={(e) => emailInputHandleChange(e.target.value)}
            className={`border p-2 rounded ${
              singupApiError || !validEmailInput.valid ? "border-red-500" : ""
            }`}
          />
          {!validEmailInput.valid && (
            <span className="text-red-500 text-sm mt-1">
              {validEmailInput.msg}
            </span>
          )}
          {singupApiError === SingupError.INVALIDEMAIL && (
            <span className="text-red-500 text-sm mt-1">
              This is not a valid email
            </span>
          )}
          {singupApiError === SingupError.EMAILEXIST && (
            <span className="text-red-500 text-sm mt-1">
              An user with this email already exists, change it
            </span>
          )}
        </div>

        <div className="flex flex-col">
          <label
            htmlFor="password"
            className="mb-1 font-bold text-[var(--orange)]"
          >
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            placeholder="Password"
            value={formPassword1}
            onChange={(e) =>
              passwordsInputHandleChange(e.target.value, formPassword2)
            }
            className={`border p-2 rounded ${singupApiError || differentPassword || !validPasswordInput.valid ? "border-red-500" : ""}`}
          />
        </div>

        <div className="flex flex-col">
          <label
            htmlFor="confirm-password"
            className="mb-1 font-bold text-[var(--orange)]"
          >
            Confirm password
          </label>
          <input
            id="confirm-password"
            name="confirm-password"
            type="password"
            placeholder="Repeat your password"
            value={formPassword2}
            onChange={(e) =>
              passwordsInputHandleChange(formPassword1, e.target.value)
            }
            className={`border p-2 rounded ${singupApiError || differentPassword || !validPasswordInput.valid ? "border-red-500" : ""}`}
          />
          {differentPassword && (
            <span className="text-red-500 text-sm mt-1">
              Passwords do not match!
            </span>
          )}
          {!validPasswordInput.valid && (
            <span className="text-red-500 text-sm mt-1">
              {validPasswordInput.msg}
            </span>
          )}
          {singupApiError === SingupError.INVALIDPASSWORD && (
            <span className="text-red-500 text-sm mt-1">Invalid password</span>
          )}
        </div>

        <div className="flex flex-col">
          <label
            htmlFor="birthdate"
            className="mb-1 font-bold text-[var(--orange)]"
          >
            Date of Birth
          </label>
          <input
            id="birthdate"
            name="birthdate"
            type="date"
            value={formBirthDate}
            onChange={(e) => setFormBirthDate(e.target.value)}
            className={`border p-2 rounded ${
              singupApiError ? "border-red-500" : ""
            }`}
          />
          {singupApiError === SingupError.INVALIDDATE && (
            <span className="text-red-500 text-sm mt-1">
              Not a valid date format
            </span>
          )}
        </div>
        <button
          type="submit"
          disabled={!canSubmit}
          className={`w-full bg-[var(--orange)] text-white py-2 rounded transition 
${!canSubmit ? "opacity-50 cursor-not-allowed" : "hover:opacity-80"}`}
        >
          Submit
        </button>
      </form>
    </div>
  );
}
