import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuthContext } from "./AuthContext";
import { useCarContext } from "./CarContext";
import { useStaticData } from "./StaticDataContext";
import { APILoginResponse, LoginError } from "../interfaces/APIResponse";
import { getCurrentUserGold } from "../profileFunctions";
import { CartItem } from "../interfaces/Order";
import { getAddedCartItemsRequest } from "../request";
import { mapAPICartItemResponseToCartItem } from "../mappers";
import { Item } from "../interfaces/Item";
import { validateUsernameInput, validatePasswordInput } from "../functions";
import { ValidationResult, defaultValidationResult } from "../interfaces/Errors";

interface LoginFormProps {
  onSuccess?: () => void;
  redirectPath?: string;
  className?: string;
}

export default function LoginForm({ onSuccess, redirectPath, className = "" }: LoginFormProps) {
  const { login } = useAuthContext();
  const router = useRouter();
  const { setCarItems, setCurrentGold } = useCarContext();
  const { items } = useStaticData();

  const [formUserName, setFormUserName] = useState<string>("");
  const [formPassword, setFormPassword] = useState<string>("");
  const [loginError, setLoginError] = useState<LoginError | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [validUsernameInput, setValidUsernameInput] = useState<ValidationResult>(defaultValidationResult);
  const [validPasswordInput, setValidPasswordInput] = useState<ValidationResult>(defaultValidationResult);

  const validateForm = () => {
    const usernameValidation = validateUsernameInput(formUserName);
    const passwordValidation = validatePasswordInput(formPassword);
    
    setValidUsernameInput(usernameValidation);
    setValidPasswordInput(passwordValidation);

    if (!usernameValidation.valid || !passwordValidation.valid) {
      return false;
    }
    return true;
  };

  async function handleLoginSubmit(e: React.FormEvent): Promise<void> {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    try {
      const apiResponse: APILoginResponse = await login(formUserName, formPassword);
      
      if (apiResponse.status === 200) {
        const currentGold: number | null = await getCurrentUserGold();
        if (!currentGold) {
          apiResponse.errorType = LoginError.CURRENTGOLDERROR;
        } else {
          setCurrentGold(currentGold);
        }

        try {
          const apiCartItems = await getAddedCartItemsRequest("client");
          const serverCartItems: CartItem[] = apiCartItems.map((apiCartItem) => {
            const matchItem: Item | undefined = items.find(
              (item: Item) => item.id == apiCartItem.itemId
            );
            if (!matchItem) {
              throw Error("Error");
            }
            return mapAPICartItemResponseToCartItem(apiCartItem, matchItem);
          });
          setCarItems(serverCartItems);
        } catch (error) {
          console.error("Error fetching cart items:", error);
        }

        setFormUserName("");
        setFormPassword("");
        setLoginError(null);
        setValidUsernameInput(defaultValidationResult);
        setValidPasswordInput(defaultValidationResult);
        
        if (onSuccess) {
          onSuccess();
        }
        
        if (redirectPath) {
          router.push(redirectPath);
        }
      } else if (apiResponse.status === 401) {
        setLoginError(LoginError.INCORRECTCREDENTIALS);
      }
    } catch (error) {
      setLoginError(LoginError.INTERNALSERVERERROR);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form onSubmit={handleLoginSubmit} className={`w-full max-w-md space-y-4 ${className}`}>
      <div className="flex flex-col">
        <label htmlFor="username" className="mb-1 font-bold text-[var(--orange)]">
          Username
        </label>
        <input
          id="username"
          name="username"
          placeholder="Username"
          value={formUserName}
          onChange={(e) => {
            setFormUserName(e.target.value);
            setLoginError(null);
            setValidUsernameInput(validateUsernameInput(e.target.value));
          }}
          className={`border p-2 rounded ${loginError || !validUsernameInput.valid ? "border-red-500" : ""}`}
          disabled={isLoading}
        />
        {!validUsernameInput.valid && (
          <span className="text-red-500 text-sm mt-1">
            {validUsernameInput.msg}
          </span>
        )}
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
          value={formPassword}
          onChange={(e) => {
            setFormPassword(e.target.value);
            setLoginError(null);
            setValidPasswordInput(validatePasswordInput(e.target.value));
          }}
          className={`border p-2 rounded ${loginError || !validPasswordInput.valid ? "border-red-500" : ""}`}
          disabled={isLoading}
        />
        {!validPasswordInput.valid && (
          <span className="text-red-500 text-sm mt-1">
            {validPasswordInput.msg}
          </span>
        )}
        {loginError && (
          <span className="text-red-500 text-sm mt-1">
            {loginError === LoginError.INCORRECTCREDENTIALS
              ? "Incorrect username or password"
              : loginError === LoginError.INVALIDUSERNAME
              ? "Username is required"
              : loginError === LoginError.INVALIDPASSWORD
              ? "Password is required"
              : "An error occurred. Please try again."}
          </span>
        )}
      </div>
      <div className="flex flex-col gap-4">
        <button
          type="submit"
          className="w-full bg-[var(--orange)] text-white py-2 rounded hover:opacity-80 transition disabled:opacity-50"
          disabled={isLoading || !validUsernameInput.valid || !validPasswordInput.valid}
        >
          {isLoading ? "Logging in..." : "Log In"}
        </button>
        <span className="text-center text-m">Are you new?</span>
        <Link
          href="/auth/signup"
          className="w-full text-center bg-[var(--orange)] text-white py-2 rounded hover:opacity-80 transition"
        >
          Sign up
        </Link>
      </div>
    </form>
  );
} 