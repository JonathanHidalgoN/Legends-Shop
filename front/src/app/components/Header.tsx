// components/Header.jsx
import { useState } from "react";
import Link from "next/link";

const Header = ({
  user = null,
}) => {
  const [showLoginDropdown, setShowLoginDropdown] = useState(false);
  const [showCartDropdown, setShowCartDropdown] = useState(false);

  return (
    <header
      className="w-full flex items-center justify-between p-4"
      style={{ backgroundColor: 'var(--white)', color: "white" }}
    >
      <div
        className="text-xl font-legens-shop"
        style={{ backgroundColor: 'var(--white)', color: 'var(--foreground)' }}
      >
        <Link href="/">
          Legens Shop
        </Link>
      </div>

      <div className="flex-1 mx-4">
        <input
          type="text"
          placeholder="Search..."
          className="w-full p-2 rounded focus:outline-none"
          style={{ backgroundColor: 'var(--white2)', color: 'var(--foreground)' }}
        />
      </div>

      <div className="flex items-center space-x-4">
        <div className="relative">
          <button
            onClick={() => setShowLoginDropdown((prev) => !prev)}
            className="p-2 rounded hover:opacity-80 transition"
            style={{ backgroundColor: 'var(--background)', color: 'var(--foreground)' }}
          >
            {user && user.name ? user.name : "Login"}
          </button>
          {showLoginDropdown && (
            <div className="absolute right-0 mt-2 w-40 p-2 rounded shadow-lg bg-white z-10">
            </div>
          )}
        </div>

        <div className="relative">
          <button
            onClick={() => setShowCartDropdown((prev) => !prev)}
            className="p-2 rounded flex items-center hover:opacity-80 transition"
            style={{ backgroundColor: 'var(--background)', color: 'var(--foreground)' }}
          >
            Cart
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
            <div className="absolute right-0 mt-2 w-40 p-2 rounded shadow-lg bg-white z-10">
              {/* Cart dropdown */}
            </div>
          )}
        </div>

      </div>
    </header>
  );
};

export default Header;
