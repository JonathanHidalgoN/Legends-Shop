"use client";

import { useAuthContext } from "@/app/components/AuthContext";
import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { APILoginResponse, LoginError } from "@/app/interfaces/APIResponse";

export default function LogInPage() {
  const { login } = useAuthContext();
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirect = searchParams.get("redirect") || "/";

  const [formUserName, setFormUserName] = useState<string>("");
  const [formPassword, setFormPassword] = useState<string>("");
  const [loginError, setLoginError] = useState<LoginError | null>(null);

  async function handleLoginSubmit(e: any): Promise<void> {
    e.preventDefault();
    const apiResponse: APILoginResponse = await login(
      formUserName,
      formPassword,
    );
    if (apiResponse.status === 200) {
      setFormUserName("");
      setFormPassword("");
      setLoginError(null);
      router.push(redirect);
    } else if (apiResponse.status === 401) {
      setLoginError(LoginError.INCORRECTCREDENTIALS);
    }
  }

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <div
        className="bg-[var(--white)] 
      min-h-screen flex flex-col items-center justify-center p-4"
      >
        <h1 className="text-3xl text-[var(--orange)] font-bold mb-6">Login</h1>
        <form
          onSubmit={handleLoginSubmit}
          className="w-full max-w-md space-y-4"
        >
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
    </Suspense>
  );
}
