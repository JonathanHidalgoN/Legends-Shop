import { Item } from "../interfaces/Item";
import { useCarContext } from "./CarContext";

export default function BuyButton({ item }: { item: Item }) {
  const { carItems, setCarItems } = useCarContext();

  function handleBuyClick() {
    setCarItems([...carItems, item]);
  }

  return (<div>
    <button
      className="mt-6 bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700 transition-colors"
      onClick={handleBuyClick}
    >
      Add to Car
    </button>

  </div>);
}
