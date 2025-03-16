"use client";

import { useAuthContext } from "@/app/components/AuthContext";
import { useRouter } from "next/navigation";
import { useState } from "react";
import toast from "react-hot-toast";

export default function SingupPage() {

  const { singup } = useAuthContext();

  const router = useRouter();

  const [formUserName, setFormUserName] = useState<string>("");
  const [formPassword1, setFormPassword1] = useState<string>("");
  const [formPassword2, setFormPassword2] = useState<string>("");
  const [singupError, setSingupError] = useState<boolean>(false);
  const [differentPassword, setDifferentPassword] = useState<boolean>(false);

  async function handleSingupSubmit(e: any): Promise<void> {
    e.preventDefault();
    if (formPassword1 !== formPassword2) {
      toast.error("Passwords do not match!");
      setDifferentPassword(true);
      return;
    } else {
      setDifferentPassword(false);
    }
    const responseStatus = await singup(formUserName, formPassword1);
    if (responseStatus === 200) {
      setFormUserName("");
      setFormPassword1("");
      setFormPassword2("");
      setSingupError(false);
      router.push("/");
    } else if (responseStatus === 400) {
      setSingupError(true);
    }
  }

  return (
    <div
      className="bg-[var(--white)] 
      min-h-screen flex flex-col items-center justify-center p-4"
    >
      <h1 className="text-3xl text-[var(--orange)] font-bold mb-6">Sing up!</h1>
      <form onSubmit={handleSingupSubmit} className="w-full max-w-md space-y-4">
        <div className="flex flex-col">
          <label
            htmlFor="username"
            className="mb-1 font-bold 
            text-[var(--orange)]"
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
            onChange={(e) => setFormPassword1(e.target.value)}
            className={`border p-2 rounded ${singupError || differentPassword ? "border-red-500" : ""}`}
          />
        </div>
        <div className="flex flex-col">
          <label
            htmlFor="password"
            className="mb-1 font-bold text-[var(--orange)]"
          >
            Confirm password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            placeholder="Repeat your password"
            value={formPassword2}
            onChange={(e) => setFormPassword2(e.target.value)}
            className={`border p-2 rounded ${singupError || differentPassword ? "border-red-500" : ""}`}
          />
          {singupError && (
            <span className="text-red-500 text-sm mt-1">
              Username already exist, change it
            </span>
          )}
          {differentPassword && (
            <span className="text-red-500 text-sm mt-1">
              Passwords do not match!
            </span>
          )}
        </div>
        <button
          type="submit"
          className="w-full bg-[var(--orange)] 
          text-white py-2 rounded hover:opacity-80 transition"
        >
          Sing up
        </button>
      </form>
    </div>
  );
}
