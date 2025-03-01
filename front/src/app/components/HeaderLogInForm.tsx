"use client"

import { useState } from "react";
import { useAuthContext } from "./AuthContext";

export default function HeaderLogInForm() {
  const [formUserName, setFormUserName] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const { logIn } = useAuthContext();
  return (<div>
    <div className="absolute right-0 mt-2 w-40 p-2 
              rounded shadow-lg bg-[var(--white)] z-10">
      <div className=" flex flex-col items-center justify-center p-4">
        <form onSubmit={(e) => {
          e.preventDefault();
          logIn(formUserName, password)
        }} className="w-full max-w-md space-y-4">
          <div className="flex flex-col">
            <label htmlFor="username" className="mb-1 font-bold 
            text-[var(--orange)]">
              Username
            </label>
            <input
              id="username"
              placeholder="Username"
              name="username"
              value={formUserName}
              onChange={(e) => setFormUserName(e.target.value)}
              className="border p-2 rounded"
            />
          </div>
          <div className="flex flex-col">
            <label htmlFor="password" className="mb-1 font-bold text-[var(--orange)]">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="border p-2 rounded"
            />
          </div>
          <button
            type="submit"
            className="w-full bg-[var(--orange)] text-white 
                    py-1 rounded hover:bg-orange-700 transition"
          >
            Log In
          </button>
        </form>
      </div>
    </div>
  </div>)
}
