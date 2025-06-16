import { ShoppingCart } from "lucide-react";
import { useCart } from "../store/cart";

export function CartButton() {
  const count = useCart((s) => s.items.length);
  return (
    <button className="relative">
      <ShoppingCart className="text-white" size={22} />
      {count > 0 && (
        <span className="absolute -top-1 -right-2 text-[10px] bg-red-500 text-white rounded-full px-1">
          {count}
        </span>
      )}
    </button>
  );
}
