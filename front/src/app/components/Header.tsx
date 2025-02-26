"use client"
import { RefObject, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { sigmar } from "../fonts";
import SearchBar from "./SearchBar";
import { Gold, Item } from "../interfaces/Item";
import { useAuth } from "./AuthContext";
import { useRouter } from "next/navigation";
import { logoutRequest } from "../request";
import { useCarContext } from "./CarContext";
import CarDropDown from "./CarDropDown";

export default function Header({ items }:
  { items: Item[] }) {
  const [showLoginDropdown, setShowLoginDropdown] = useState(false);
  const [showCartDropdown, setShowCartDropdown] = useState(false);
  const { userName, setUserName } = useAuth();
  const loginDropDownRef: RefObject<HTMLDivElement | null> = useRef<HTMLDivElement>(null);
  const carDropDownRef: RefObject<HTMLDivElement | null> = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const { carItems, setCarItems } = useCarContext();

  //This is a compy of a function Can I create a general one?
  // Hide suggestions when clicking outside
  // source: https://stackoverflow.com/questions/32553158/detect-click-outside-react-component
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        loginDropDownRef.current &&
        !loginDropDownRef.current.contains(event.target as Node)
      ) {
        setShowLoginDropdown(false);
      }
      if (
        carDropDownRef.current &&
        !carDropDownRef.current.contains(event.target as Node)
      ) {
        setShowCartDropdown(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  async function handleLogout() {
    try {
      const response = await logoutRequest("client");
      if (!response.ok) {
        throw new Error("Logout failed");
      }
      setUserName(null);
      router.push("/");
    } catch (error) {
      console.log("Error");
    }
  }

  function deleteOneItemFromCartDropDown(item: Item) {
    const index = carItems.findIndex(cartItem => cartItem.name === item.name);
    if (index !== -1) {
      setCarItems([...carItems.slice(0, index), ...carItems.slice(index + 1)]);
    }
  }

  return (
    <header
      className="w-full flex items-center justify-between p-4"
      style={{ backgroundColor: 'var(--white2)', color: "white2" }}
    >
      <div
        className={`text-xl ${sigmar.className}`}
        style={{ backgroundColor: 'var(--white2)', color: 'var(--orange)' }}
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
              if (userName) {
                setShowLoginDropdown((prev) => !prev)
              }
              else {
                router.push("/auth/login");
              }
            }}
            className="p-2 rounded hover:opacity-80 transition"
            style={{ backgroundColor: 'var(--orange)', color: 'var(--white)' }}
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
                  handleLogout();
                  setShowLoginDropdown(false);
                }}
                className="block w-full text-left px-2 py-1 hover:bg-gray-100"
              >
                Logout
              </button>
            </div>
          )}
        </div>

        <div className="relative">
          <button
            onClick={() => setShowCartDropdown((prev) => !prev)}
            className="p-2 rounded flex items-center hover:opacity-80 transition"
            style={{ backgroundColor: 'var(--orange)', color: 'var(--white)' }}
          >
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
                    onClick={() => router.push("/order")}
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

      </div>
    </header >
  );
};
