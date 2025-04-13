import Image from "next/image";

export default function WrongError() {
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
      <p className="text-[var(--gray)] max-w-md">
        We&apos;re having trouble loading this page right now. Please try again later
        or contact support if the problem continues.
      </p>
    </div>
  );
}
