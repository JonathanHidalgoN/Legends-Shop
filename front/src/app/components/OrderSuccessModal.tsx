export default function OrderSuccessModal({ orderId, onClose }: {
  orderId: number, onClose: any
}) {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white p-6 rounded relative max-w-sm w-full">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-gray-500 hover:text-gray-700 text-2xl"
          aria-label="Close"
        >
          &times;
        </button>
        <div className="flex flex-col items-center">
          <div className="bg-green-500 text-white rounded-full h-16 w-16 flex items-center justify-center mb-4">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h2 className="text-xl font-bold mb-2">Congratulations!</h2>
          <p>Your order has been placed successfully.</p>
          <p className="mt-2">Order ID: {orderId}</p>
        </div>
      </div>
    </div>
  );
}
