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
import {
  APICartItemResponse,
  APILoginResponse,
  LoginError,
} from "../interfaces/APIResponse";
import { getCurrentUserGold } from "../profileFunctions";
import { CartItem } from "../interfaces/Order";
import { getAddedCartItemsRequest } from "../request";
import { mapAPICartItemResponseToCartItem } from "../mappers";
import LoginForm from "./LoginForm";
import LoadingButton from "./LoadingButton";

export default function Header({ items }: { items: Item[] }) {
  const { userName, logOut, login } = useAuthContext();
  const { carItems, setCarItems, currentGold, setCurrentGold } =
    useCarContext();

  const [showLoginDropdown, setShowLoginDropdown] = useState(false);
  const [showCartDropdown, setShowCartDropdown] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const [formUserName, setFormUserName] = useState<string>("");
  const [formPassword, setFormPassword] = useState<string>("");
  const [loginError, setLoginError] = useState<LoginError | null>(null);
  const [isNavigating, setIsNavigating] = useState(false);

  const loginDropDownRef: RefObject<HTMLDivElement | null> =
    useRef<HTMLDivElement>(null);
  const carDropDownRef: RefObject<HTMLDivElement | null> =
    useRef<HTMLDivElement>(null);

  const router = useRouter();

  async function handleLoginSubmit(e: any): Promise<void> {
    e.preventDefault();
    const apiResponse: APILoginResponse = await login(
      formUserName,
      formPassword,
    );
    if (apiResponse.status === 200) {
      const currentGold: number | null = await getCurrentUserGold();
      if (!currentGold) {
        apiResponse.errorType = LoginError.CURRENTGOLDERROR;
      } else {
        setCurrentGold(currentGold);
      }
      try {
        const apiCartItems: APICartItemResponse[] =
          await getAddedCartItemsRequest("client");
        const serverCartItems: CartItem[] = apiCartItems.map(
          (apiCartItem: APICartItemResponse) => {
            const matchItem: Item | undefined = items.find(
              (item: Item) => item.id == apiCartItem.itemId,
            );
            if (!matchItem) {
              throw Error("Error");
            }
            return mapAPICartItemResponseToCartItem(apiCartItem, matchItem);
          },
        );
        setCarItems(serverCartItems);
      } catch (error) {
        //todo: what to do in this error?
      }
      setShowLoginDropdown(false);
      setFormUserName("");
      setFormPassword("");
      setLoginError(null);
    } else if (apiResponse.status === 401) {
      setLoginError(apiResponse.errorType);
    }
  }

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
  }, [userName]);

  const handleNavigation = async (path: string) => {
    setIsNavigating(true);
    await router.push(path);
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
                <div className="text-center text-gray-500 py-4">Cart is empty</div>
              )}
            </div>
          )}
        </div>

        {userName && (
          <div className="relative">
            {isMounted ? (
              <LoadingButton
                onClick={() => handleNavigation(`/order/order_history/${userName}`)}
                isLoading={isNavigating}
                className="px-4 py-2 rounded-lg hover:bg-[var(--pink1)] transition-all duration-200 
                bg-[var(--orange)] text-[var(--white)] shadow-sm hover:shadow-md"
              >
                Orders
              </LoadingButton>
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
      </div>
    </header>
  );
}
