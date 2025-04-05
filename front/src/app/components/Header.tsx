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
import LoginForm from "./LoginForm";
import LoadingButton from "./LoadingButton";
import { useStaticData } from "./StaticDataContext";

export default function Header({ items }: { items: Item[] }) {
  const { userName, logOut } = useAuthContext();
  const { carItems, currentGold, currentLocation, setCurrentLocation } =
    useCarContext();
  const { locations } = useStaticData();
  console.log(locations);

  const [showLoginDropdown, setShowLoginDropdown] = useState(false);
  const [showCartDropdown, setShowCartDropdown] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const [isNavigating, setIsNavigating] = useState(false);
  const [showLocationDropdown, setShowLocationDropdown] = useState(false);
  const [showOrdersDropdown, setShowOrdersDropdown] = useState(false);

  const loginDropDownRef: RefObject<HTMLDivElement | null> =
    useRef<HTMLDivElement>(null);
  const carDropDownRef: RefObject<HTMLDivElement | null> =
    useRef<HTMLDivElement>(null);
  const locationDropdownRef: RefObject<HTMLDivElement | null> =
    useRef<HTMLDivElement>(null);
  const ordersDropdownRef: RefObject<HTMLDivElement | null> =
    useRef<HTMLDivElement>(null);

  const router = useRouter();

  useEffect(() => {
    setIsMounted(true);
    const handleClick = (event: MouseEvent) => {
      handleClickOutside(event, loginDropDownRef, setShowLoginDropdown);
      handleClickOutside(event, carDropDownRef, setShowCartDropdown);
      handleClickOutside(event, locationDropdownRef, setShowLocationDropdown);
      handleClickOutside(event, ordersDropdownRef, setShowOrdersDropdown);
    };
    document.addEventListener("mousedown", handleClick);
    return () => {
      document.removeEventListener("mousedown", handleClick);
    };
  }, [userName]);

  const handleNavigation = async (path: string) => {
    setIsNavigating(true);
    router.push(path);
    setIsNavigating(false);
  };

  return (
    <header
      className="w-full flex items-center justify-between p-4 
      bg-[var(--white2)] shadow-md sticky top-0 z-50"
    >
      <div
        className={`text-2xl ${sigmar.className} ml-12 mr-12
                    bg-[var(--white2)] text-[var(--orange)] hover:text-[var(--pink1)] transition-colors duration-200`}
      >
        <Link href="/">Legends Shop</Link>
      </div>
      <div className="flex-1 mx-4">
        <SearchBar items={items} />
      </div>

      <div className="flex items-center space-x-6">
        <div className="relative">
          <button
            onClick={() => {
              setShowLoginDropdown((prev) => !prev);
            }}
            className="px-4 py-2 rounded-lg hover:bg-[var(--pink1)] transition-all duration-200
            bg-[var(--orange)] text-[var(--white)] shadow-sm hover:shadow-md"
          >
            {userName ? "Welcome " + userName : "Login"}
          </button>
          {userName && showLoginDropdown && (
            <div
              ref={loginDropDownRef}
              className="absolute right-0 mt-2 w-48 p-2 rounded-lg shadow-lg bg-white z-10 
              transform transition-all duration-200 ease-in-out"
            >
              <LoadingButton
                onClick={() => {
                  handleNavigation(`/profile/${userName}`);
                  setShowLoginDropdown(false);
                }}
                isLoading={isNavigating}
                className="block w-full text-left px-3 py-2 hover:bg-gray-100 rounded-md transition-colors duration-150"
              >
                Profile
              </LoadingButton>
              <button
                onClick={() => {
                  logOut();
                  setShowLoginDropdown(false);
                }}
                className="block w-full text-left px-3 py-2 hover:bg-gray-100 rounded-md transition-colors duration-150"
              >
                Logout
              </button>
            </div>
          )}
          {!userName && showLoginDropdown && (
            <div ref={loginDropDownRef}>
              <div
                className="absolute right-0 mt-2 w-96 p-4 
                rounded-lg shadow-lg bg-[var(--white)] z-10 transform transition-all duration-200 ease-in-out"
              >
                <div className="flex flex-col items-center justify-center">
                  <LoginForm
                    onSuccess={() => setShowLoginDropdown(false)}
                    className="w-full"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="relative">
          <LoadingButton
            onClick={() => setShowCartDropdown((prev) => !prev)}
            isLoading={false}
            className="px-4 py-2 rounded-lg flex items-center hover:bg-[var(--pink1)] transition-all duration-200
            bg-[var(--orange)] text-[var(--white)] shadow-sm hover:shadow-md"
          >
            Car
          </LoadingButton>
          {showCartDropdown && (
            <div
              ref={carDropDownRef}
              className="absolute right-2 mt-2 w-96 p-4 rounded-lg shadow-lg bg-white z-10 
              transform transition-all duration-200 ease-in-out"
            >
              {carItems.length > 0 ? (
                <>
                  <CarDropDown tiny={true} />
                  <LoadingButton
                    onClick={() => {
                      handleNavigation("/order/make_order/");
                      setShowCartDropdown(false);
                    }}
                    isLoading={isNavigating}
                    className="mt-4 bg-[var(--orange)] 
                    text-[var(--white)] rounded-lg hover:bg-[var(--pink1)] 
                    transition-all duration-200 w-full py-2 shadow-sm hover:shadow-md"
                  >
                    Order now!
                  </LoadingButton>
                </>
              ) : (
                <div className="text-center text-gray-500 py-4">
                  Cart is empty
                </div>
              )}
            </div>
          )}
        </div>

        {userName && (
          <div className="relative">
            {isMounted ? (
              <>
                <LoadingButton
                  onClick={() => setShowOrdersDropdown((prev) => !prev)}
                  isLoading={isNavigating}
                  className="px-4 py-2 rounded-lg hover:bg-[var(--pink1)] transition-all duration-200 
                  bg-[var(--orange)] text-[var(--white)] shadow-sm hover:shadow-md"
                >
                  Orders
                </LoadingButton>
                {showOrdersDropdown && (
                  <div
                    ref={ordersDropdownRef}
                    className="absolute right-0 mt-2 w-48 p-2 rounded-lg shadow-lg bg-white z-10 
                    transform transition-all duration-200 ease-in-out"
                  >
                    <LoadingButton
                      onClick={() => {
                        handleNavigation(`/order/order_history/${userName}`);
                        setShowOrdersDropdown(false);
                      }}
                      isLoading={isNavigating}
                      className="block w-full text-left px-3 py-2 hover:bg-gray-100 rounded-md transition-colors duration-150"
                    >
                      Order History
                    </LoadingButton>
                    <button
                      onClick={() => {
                        handleNavigation(`/order/review_history/${userName}`);
                        setShowOrdersDropdown(false);
                      }}
                      className="block w-full text-left px-3 py-2 hover:bg-gray-100 rounded-md transition-colors duration-150"
                    >
                      Reviews
                    </button>
                  </div>
                )}
              </>
            ) : null}
          </div>
        )}

        {userName && currentGold != null && (
          <div className="flex items-center border-2 border-yellow-500 bg-white rounded-lg p-3 shadow-sm hover:shadow-md transition-all duration-200">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6 text-yellow-500 mr-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M16 11V7a4 4 0 00-8 0v4M5 11h14l1 9H4l1-9z"
              />
            </svg>
            <span className="text-yellow-500 text-xl font-bold">
              {currentGold.toLocaleString()} g
            </span>
          </div>
        )}

        {locations.length > 0 && (
          <div className="relative flex items-center">
            <div
              className="flex items-center cursor-pointer px-2 py-1.5 rounded hover:bg-gray-100 transition-colors duration-200"
              onClick={() => setShowLocationDropdown((prev) => !prev)}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4 text-gray-600 mr-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <div className="flex flex-col">
                <span className="text-xs text-gray-500">Deliver to</span>
                <span className="text-sm font-medium text-[var(--orange)]">
                  {currentLocation?.country_name || "Select location"}
                </span>
              </div>
            </div>
            {isMounted && showLocationDropdown && (
              <div
                className="absolute top-full left-0 w-64 bg-white shadow-lg rounded-lg mt-2 z-50"
                ref={locationDropdownRef}
              >
                <div className="p-2">
                  {locations.map((location) => (
                    <div
                      key={location.id}
                      onClick={() => {
                        setCurrentLocation(location);
                        setShowLocationDropdown(false);
                      }}
                      className={`px-3 py-2 rounded-md cursor-pointer hover:bg-gray-100 transition-colors duration-150 ${
                        currentLocation?.id === location.id ? "bg-gray-50" : ""
                      }`}
                    >
                      {location.country_name}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
}
