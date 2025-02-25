"use client"

import { useState } from "react"
import { signup } from "../functions";
import { useRouter } from "next/navigation";
import { allTagsRequet } from "@/app/request";

export default function LogInPage() {
  const [userName, setUserName] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [error, setError] = useState<string>("");
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    try {
      signup(userName, password);
    } catch (error: unknown) {
      //This way linter wont complain ):
      if (error instanceof Error) {
        setError(error.message)
        console.error(error.message);
      } else {
        setError("An unknown error occurred");
        console.error("An unknown error occurred");
      }
    }
    console.log("nice");
    // router.push("/");
  }

  return (
    <div className="bg-[var(--white)] 
      min-h-screen flex flex-col items-center justify-center p-4">
      <h1 className="text-3xl text-[var(--orange)] font-bold mb-6">Login</h1>
      <form onSubmit={handleSubmit} className="w-full max-w-md space-y-4">
        <div className="flex flex-col">
          <label htmlFor="username" className="mb-1 font-bold 
            text-[var(--orange)]">
            Username
          </label>
          <input
            id="username"
            name="username"
            placeholder="Username"
            value={userName}
            onChange={(e) => setUserName(e.target.value)}
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
        {error && <p className="text-red-500">{error}</p>}
        <button
          type="submit"
          className="w-full bg-[var(--orange)] text-white py-2 rounded hover:bg-blue-700 transition"
        >
          Log In
        </button>
      </form>
    </div>
  );
}


