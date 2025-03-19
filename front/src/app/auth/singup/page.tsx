"use client";

import { useAuthContext } from "@/app/components/AuthContext";
import { APISingupResponse, SingupError } from "@/app/interfaces/APIResponse";
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
  const [singupError, setSingupError] = useState<SingupError | null>(null);
  const [differentPassword, setDifferentPassword] = useState<boolean>(false);

  function checkPasswords(p1: string, p2: string): void {
    setDifferentPassword(p1 != p2)
    setFormPassword2(p2);
    setFormPassword1(p1);
  }

  function checkEmailPattern(email: string): void {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    setFormEmail(email);
    if (pattern.test(email)) {
      setSingupError(null);
    } else {
      setSingupError(SingupError.INVALIDEMAIL);
    }
  }

  async function handleSingupSubmit(e: any): Promise<void> {
    e.preventDefault();
    if (formPassword1 !== formPassword2) {
      toast.error("Passwords do not match!");
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
      setSingupError(null);
    } else if (responseStatus.status === 400) {
      setSingupError(responseStatus.errorType);
    }
  }

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
            onChange={(e) => setFormUserName(e.target.value)}
            className={`border p-2 rounded ${singupError ? "border-red-500" : ""}`}
          />
          {singupError === SingupError.USERNAMEEXIST && (
            <span className="text-red-500 text-sm mt-1">
              Username exist, change it
            </span>
          )}
          {singupError === SingupError.INVALIDUSERNAME && (
            <span className="text-red-500 text-sm mt-1">
              Invalid username
            </span>
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
            onChange={(e) => checkEmailPattern(e.target.value)}
            className={`border p-2 rounded ${singupError ? "border-red-500" : ""
              }`}
          />
          {singupError === SingupError.INVALIDEMAIL && (
            <span className="text-red-500 text-sm mt-1">
              This is not a valid email
            </span>
          )}
          {singupError === SingupError.EMAILEXIST && (
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
            onChange={(e) => checkPasswords(e.target.value, formPassword2)}
            className={`border p-2 rounded ${singupError || differentPassword ? "border-red-500" : ""}`}
          />
          {singupError === SingupError.INVALIDPASSWORD && (
            <span className="text-red-500 text-sm mt-1">
              Invalid password
            </span>
          )}
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
            onChange={(e) => checkPasswords(formPassword1, e.target.value)}
            className={`border p-2 rounded ${singupError || differentPassword ? "border-red-500" : ""}`}
          />
          {differentPassword && (
            <span className="text-red-500 text-sm mt-1">
              Passwords do not match!
            </span>
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
            className={`border p-2 rounded ${singupError ? "border-red-500" : ""
              }`}
          />
          {singupError === SingupError.INVALIDDATE && (
            <span className="text-red-500 text-sm mt-1">
              Not a valid date format
            </span>
          )}
        </div>
        <button
          type="submit"
          disabled={singupError === SingupError.INVALIDEMAIL}
          className={`w-full bg-[var(--orange)] text-white py-2 rounded transition ${singupError === SingupError.INVALIDEMAIL
            ? "opacity-50 cursor-not-allowed"
            : "hover:opacity-80"
            }`}
        >
          Submit
        </button>
      </form>
    </div>
  );
}
