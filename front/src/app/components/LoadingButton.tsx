import { ReactNode } from "react";

interface LoadingButtonProps {
  onClick: () => void;
  isLoading: boolean;
  children: ReactNode;
  className?: string;
  disabled?: boolean;
}

export default function LoadingButton({
  onClick,
  isLoading,
  children,
  className = "",
  disabled = false,
}: LoadingButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={isLoading || disabled}
      className={`relative ${className} ${isLoading ? "cursor-wait" : ""}`}
    >
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}
      <span className={isLoading ? "opacity-0" : ""}>{children}</span>
    </button>
  );
}
