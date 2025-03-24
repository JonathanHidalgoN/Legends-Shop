import Image from "next/image";
import toast from "react-hot-toast";

const SUCCESS_ICONS = ["/jhinIcon.png", "/luxIcon.png", "/zingsIcon.png"];
const ERROR_ICONS = ["/sadAmumu.png"];

export function showSuccessToast(msg: string) {
  const img: string =
    SUCCESS_ICONS[Math.floor(Math.random() * SUCCESS_ICONS.length)];
  toast.custom(
    (t) => (
      <div
        className={`${
          t.visible ? "animate-enter" : "animate-leave"
        } bg-white text-black p-4 rounded border border-black`}
      >
        <div className="flex items-center">
          <div className="bg-green-500 rounded-full p-1">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <span className="ml-3 font-medium">{msg}</span>
        </div>

        <div className="flex mt-2 justify-center">
          <div className="relative w-24 h-24 sm:w-32 sm:h-32">
            <Image
              src={img}
              alt="Success"
              width={128}
              height={128}
              className="object-contain bg-transparent"
            />
          </div>
        </div>
      </div>
    ),
    {
      duration: 3000,
    },
  );
}

export function showErrorToast(msg: string) {
  const img: string =
    ERROR_ICONS[Math.floor(Math.random() * ERROR_ICONS.length)];
  toast.custom(
    (t) => (
      <div
        className={`${
          t.visible ? "animate-enter" : "animate-leave"
        } bg-white text-black p-4 rounded border border-black`}
      >
        <div className="flex items-center">
          <div className="bg-red-500 rounded-full p-1">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </div>
          <span className="ml-3 font-medium">{msg}</span>
        </div>

        <div className="flex mt-2 justify-center">
          <div className="relative w-24 h-24 sm:w-32 sm:h-32">
            <Image
              src={img}
              alt="Success"
              width={128}
              height={128}
              className="object-contain bg-transparent"
            />
          </div>
        </div>
      </div>
    ),
    {
      duration: 3000,
    },
  );
}
