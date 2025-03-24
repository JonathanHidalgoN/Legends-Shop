import { Item } from "../interfaces/Item";
import { useCarContext } from "./CarContext";

export default function AddToCarButton({ item }: { item: Item }) {
  const { handleClientAddingItemToCar } = useCarContext();

  return (
    <div>
      <button
        className="mt-6 bg-[var(--orange)] text-[var(--white)] 
      px-6 py-3 rounded hover:bg-[var(--pink1)] transition-colors"
        onClick={() => handleClientAddingItemToCar(item)}
      >
        Add to Car
      </button>
    </div>
  );
}
