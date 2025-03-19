"use client";
import { RefObject, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { sigmar } from "../fonts";
import SearchBar from "./SearchBar";
import { useCarContext } from "./CarContext";
import { Item } from "../interfaces/Item";
import { useAuthContext } from "./AuthContext";
import { useRouter } from "next/navigation";
import CarDropDown from "./CarDropDown";
import { handleClickOutside } from "../functions";
import { getCurrentUserGold } from "../profileFunctions";

export default function Header({ items }: { items: Item[] }) {

  const { userName, logOut, login } = useAuthContext();
  const { carItems, currentGold, setCurrentGold } = useCarContext();

  const [showLoginDropdown, setShowLoginDropdown] = useState(false);
  const [showCartDropdown, setShowCartDropdown] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const [formUserName, setFormUserName] = useState<string>("");
  const [formPassword, setFormPassword] = useState<string>("");
  const [loginError, setLoginError] = useState<boolean>(false);

  const loginDropDownRef: RefObject<HTMLDivElement | null> =
    useRef<HTMLDivElement>(null);
  const carDropDownRef: RefObject<HTMLDivElement | null> =
    useRef<HTMLDivElement>(null);

  const router = useRouter();
  async function handleLoginSubmit(e: any): Promise<void> {
    e.preventDefault();
    const responseStatus = await login(formUserName, formPassword);
    if (responseStatus === 200) {
      setShowLoginDropdown(false);
      setFormUserName("");
      setFormPassword("");
      setLoginError(false);
    } else if (responseStatus === 401) {
      setLoginError(true);
    }
  }


  useEffect(() => {
    setIsMounted(true);
    async function fetchUserGold() {
      if (userName) {
        const userGold: number | null = await getCurrentUserGold();
        if (userGold !== null) {
          setCurrentGold(userGold);
        } else {
          setCurrentGold(null);
        }
      } else {
        setCurrentGold(null);
      }
    }
    fetchUserGold();

    const handleClick = (event: MouseEvent) => {
      handleClickOutside(event, loginDropDownRef, setShowLoginDropdown);
      handleClickOutside(event, carDropDownRef, setShowCartDropdown);
    };

    document.addEventListener("mousedown", handleClick);
    return () => {
      document.removeEventListener("mousedown", handleClick);
    };
  }, [userName]);

  return (
    <header
      className="w-full flex items-center justify-between p-4 
      bg-[var(--white2)]"
    >
      <div
        className={`text-xl ${sigmar.className} ml-12 mr-12
                    bg-[var(--white2)] text-[var(--orange)]`}
      >
        <Link href="/">Legends Shop</Link>
      </div>
      <div className="flex-1 mx-4">
        <SearchBar items={items} />
      </div>

      <div className="flex items-center space-x-4">
        <div className="relative">
          <button
            onClick={() => {
              setShowLoginDropdown((prev) => !prev);
            }}
            className="p-2 rounded hover:opacity-80 transition
            bg-[var(--orange)] text-[var(--white)]"
          >
            {userName ? "Welcome " + userName : "Login"}
          </button>
          {userName && showLoginDropdown && (
            <div
              ref={loginDropDownRef}
              className="absolute right-0 mt-2 w-40 p-2 rounded shadow-lg bg-white z-10"
            >
              <button
                onClick={() => {
                  router.push(`/profile/${userName}`);
                  setShowLoginDropdown(false);
                }}
                className="block w-full text-left px-2 py-1 hover:bg-gray-100"
              >
                Profile
              </button>
              <button
                onClick={() => {
                  logOut();
                  setShowLoginDropdown(false);
                }}
                className="block w-full text-left px-2 py-1 hover:bg-gray-100"
              >
                Logout
              </button>
            </div>
          )}
          {!userName && showLoginDropdown && (
            <div ref={loginDropDownRef}>
              <div
                className="absolute right-0 mt-2 w-40 p-2 
              rounded shadow-lg bg-[var(--white)] z-10"
              >
                <div className=" flex flex-col items-center justify-center p-4">
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
                        placeholder="Username"
                        name="username"
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
                    <div className="flex flex-col items-center w-full">
                      <button
                        type="submit"
                        className="w-full max-w-md bg-[var(--orange)] text-white py-1 rounded hover:opacity-80 transition"
                      >
                        Log In
                      </button>
                      <div className="my-2 text-center">Are you new?</div>
                      <button
                        onClick={() => {
                          setShowLoginDropdown(false);
                          router.push("/auth/singup/");
                        }}
                        className="w-full max-w-md bg-[var(--orange)] text-white py-1 rounded hover:opacity-80 transition"
                      >
                        Sign Up
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="relative">
          <button
            onClick={() => setShowCartDropdown((prev) => !prev)}
            className="p-2 rounded flex items-center hover:opacity-80 transition
            bg-[var(--orange)] text-[var(--white)]"
          >
            Car
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M16 11V7a4 4 0 00-8 0v4"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M5 11h14l1 9H4l1-9z"
            />
          </button>
          {showCartDropdown && (
            <div
              ref={carDropDownRef}
              className="absolute right-0 mt-2 w-80 p-2 rounded shadow-lg bg-white z-10"
            >
              {carItems.length > 0 ? (
                <>
                  <CarDropDown tiny={true} />
                  <button
                    className="mt-2 bg-[var(--orange)] 
                    text-[var(--white)] rounded hover:bg-[var(--pink1)] 
                    transition-colors w-full"
                    onClick={() => {
                      router.push("/order/make_order/");
                      setShowCartDropdown(false);
                    }}
                  >
                    Order now!
                  </button>
                </>
              ) : (
                <div className="text-center text-xs">Cart is empty</div>
              )}
            </div>
          )}
        </div>

        {userName && (
          <div className="relative">
            {isMounted ? (
              <Link href={`/order/order_history/${userName}`}>
                <button className="p-2 rounded hover:opacity-80 transition bg-[var(--orange)] text-[var(--white)]">
                  Orders
                </button>
              </Link>
            ) : null}
          </div>
        )}

        {userName && currentGold != null && (
          <div className="flex items-center border border-yellow-500 bg-white rounded p-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6 text-yellow-500 mr-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 11h14l1 9H4l1-9z" />
            </svg>
            <span className="text-yellow-500 text-xl font-bold">{currentGold.toLocaleString()} g</span>
          </div>
        )}

      </div>
    </header>
  );
}
