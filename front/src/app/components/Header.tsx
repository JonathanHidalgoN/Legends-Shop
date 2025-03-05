"use client"
import { RefObject, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { sigmar } from "../fonts";
import SearchBar from "./SearchBar";
import { useCarContext } from "./CarContext";
import { Item } from "../interfaces/Item";
import { useAuthContext } from "./AuthContext";
import { useRouter } from "next/navigation";
import CarDropDown from "./CarDropDown";
import HeaderLogInForm from "./HeaderLogInForm";
import { handleClickOutside } from "../functions";

export default function Header({ items }:
  { items: Item[] }) {
  const [showLoginDropdown, setShowLoginDropdown] = useState(false);
  const [showCartDropdown, setShowCartDropdown] = useState(false);
  const { userName, logOut } = useAuthContext();
  const loginDropDownRef: RefObject<HTMLDivElement | null> = useRef<HTMLDivElement>(null);
  const carDropDownRef: RefObject<HTMLDivElement | null> = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const [isMounted, setIsMounted] = useState(false);
  const { carItems } = useCarContext();

  useEffect(() => {
    setIsMounted(true);
    const handleClick = (event: MouseEvent) => {
      handleClickOutside(event, loginDropDownRef, setShowLoginDropdown);
      handleClickOutside(event, carDropDownRef, setShowCartDropdown);
    };
    document.addEventListener("mousedown", handleClick);
    return () => {
      document.removeEventListener("mousedown", handleClick);
    };
  }, []);

  return (
    <header
      className="w-full flex items-center justify-between p-4 
      bg-[var(--white2)]"
    >
      <div
        className={`text-xl ${sigmar.className} ml-12 mr-12
                    bg-[var(--white2)] text-[var(--orange)]`}
      >
        <Link href="/">
          Legends Shop
        </Link>
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
            <div ref={loginDropDownRef}
              className="absolute right-0 mt-2 w-40 p-2 rounded shadow-lg bg-white z-10">
              <button
                onClick={() => {
                  router.push("/profile");
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
              <HeaderLogInForm />
            </div>
          )}
        </div>

        <div className="relative">
          <button
            onClick={() => setShowCartDropdown((prev) => !prev)}
            className="p-2 rounded flex items-center hover:opacity-80 transition
            bg-[var(--orange)] text-[var(--white)]">
            Car
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="gold"
              viewBox="0 0 24 24"
              strokeWidth="2"
              stroke="currentColor"
              className="h-6 w-6"
            >
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
            </svg>
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
                      router.push("/order/make_order/")
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
      </div>
    </header >
  );
};
