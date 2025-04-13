"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";
import Image from "next/image";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // You can log the error to an error reporting service here
    console.error("Error caught by ErrorBoundary:", error, errorInfo);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6">
          <div className="relative w-48 h-48 mb-6 opacity-80">
            <Image
              src="/sadAmumu.png"
              alt="sad amumu"
              fill
              className="object-contain"
              priority
            />
          </div>
          <h1 className="text-2xl font-semibold text-[var(--orange)] mb-2">
            Oops, something went wrong!
          </h1>
          <p className="text-[var(--gray)] max-w-md mb-4">
            We&apos;re having trouble loading this page right now. Please try again later
            or contact support if the problem continues.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-[var(--orange)] text-white rounded-md hover:bg-opacity-90 transition-all"
          >
            Refresh Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 
