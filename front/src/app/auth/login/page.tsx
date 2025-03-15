"use client";

import { useAuthContext } from "@/app/components/AuthContext";
import { useState } from "react";

export default function LogInPage() {
  const [formUserName, setFormUserName] = useState<string>("");
  const [formPassword, setFormPassword] = useState<string>("");
  const { login, loginError, setLoginError } = useAuthContext();

  async function handleLoginSubmit(e: any): Promise<void> {
    e.preventDefault();
    const responseStatus = await login(formUserName, formPassword);
    if (responseStatus === 200) {
      setFormUserName("");
      setFormPassword("");
      setLoginError(false);
    } else if (responseStatus === 401) {
      setLoginError(true);
    }
  }

  return (
    <div
      className="bg-[var(--white)] 
      min-h-screen flex flex-col items-center justify-center p-4"
    >
      <h1 className="text-3xl text-[var(--orange)] font-bold mb-6">Login</h1>
      <form onSubmit={handleLoginSubmit} className="w-full max-w-md space-y-4">
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
            className={`border p-2 rounded ${loginError ? "border-red-500" : ""}`}
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
            value={formPassword}
            onChange={(e) => setFormPassword(e.target.value)}
            className={`border p-2 rounded ${loginError ? "border-red-500" : ""}`}
          />
          {loginError && (
            <span className="text-red-500 text-sm mt-1">
              Incorrect user or password
            </span>
          )}
        </div>
        <button
          type="submit"
          className="w-full bg-[var(--orange)] 
          text-white py-2 rounded hover:bg-blue-700 transition"
        >
          Log In
        </button>
      </form>
    </div>
  );
}
