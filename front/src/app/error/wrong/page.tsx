export default function WrongError() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6">
      <img
        src="/sadAmumu.png"
        alt="Sad Amumu"
        className="w-48 h-auto mb-6 opacity-80"
      />
      <h1 className="text-2xl font-semibold text-[var(--black)] mb-2">
        Oops, something went wrong!
      </h1>
      <p className="text-[var(--gray)] max-w-md">
        We're having trouble loading this page right now. Please try again later or contact support if the problem continues.
      </p>
    </div>
  );
}
