// src/store/cart.js
import { create } from "zustand";

export const useCart = create((set, get) => ({
  items: [], // [{ id, title, price, qty }]
  add(item) {
    const exists = get().items.find((i) => i.id === item.id);
    set({
      items: exists
        ? get().items.map((i) =>
            i.id === item.id ? { ...i, qty: i.qty + 1 } : i,
          )
        : [...get().items, { ...item, qty: 1 }],
    });
  },
  remove(id) {
    set({ items: get().items.filter((i) => i.id !== id) });
  },
  clear() {
    set({ items: [] });
  },
  total() {
    return get()
      .items.reduce((sum, i) => sum + i.price * i.qty, 0)
      .toFixed(2);
  },
  count() {
    return get().items.reduce((n, i) => n + i.qty, 0);
  },
}));
