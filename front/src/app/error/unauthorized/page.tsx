import Image from "next/image";

export default function UnauthorizedError() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6">
      <div className="relative w-48 h-48 mb-6 opacity-80">
        <Image
          src="/blitzIcon.png"
          alt="Blitz icon question mark"
          fill
          className="object-contain"
          priority
        />
      </div>
      <h1 className="text-2xl font-semibold text-[var(--orange)] mb-2">
        You have no credentials to access this page!
      </h1>
      <p className="text-[var(--gray)] max-w-md">
        Are you sure you want to go there?
      </p>
    </div>
  );
}
