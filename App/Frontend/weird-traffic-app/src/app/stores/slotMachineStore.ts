// src/stores/slotMachineStore.ts
import { create } from "zustand";
import { devtools } from "zustand/middleware";
import { slotMachineWords } from "@/app/constants/SlotWords";
import type { SlotMachineState } from "./types";

interface SlotMachineStore extends SlotMachineState {
  spin: () => void;
  reset: () => void;
  getRandomWord: (category: string[]) => string;
}

export const useSlotMachineStore = create<SlotMachineStore>()(
  devtools((set, get) => ({
    // Initial state
    word1: "---",
    word2: "---",
    word3: "---",
    displayWord1: "---",
    displayWord2: "---",
    displayWord3: "---",
    isSpinning: false,
    spinCompleted: false,

    // Helper function
    getRandomWord: (category) => {
      if (!category || category.length === 0) return "";
      return category[Math.floor(Math.random() * category.length)];
    },

    // Actions
    spin: () => {
      if (get().isSpinning) return;

      set({
        isSpinning: true,
        spinCompleted: false,
        word1: "",
        word2: "",
        word3: "",
      });

      // Animation interval
      const animationInterval = setInterval(() => {
        const { getRandomWord } = get();
        set({
          displayWord1: getRandomWord(slotMachineWords.nouns),
          displayWord2: getRandomWord(slotMachineWords.verbs),
          displayWord3: getRandomWord(slotMachineWords.places),
        });
      }, 50);

      // Final result
      setTimeout(() => {
        clearInterval(animationInterval);
        const { getRandomWord } = get();

        const finalWord1 = getRandomWord(slotMachineWords.nouns);
        const finalWord2 = getRandomWord(slotMachineWords.verbs);
        const finalWord3 = getRandomWord(slotMachineWords.places);

        set({
          word1: finalWord1,
          word2: finalWord2,
          word3: finalWord3,
          displayWord1: finalWord1,
          displayWord2: finalWord2,
          displayWord3: finalWord3,
          isSpinning: false,
          spinCompleted: true,
        });
      }, 3000);
    },

    reset: () =>
      set({
        word1: "---",
        word2: "---",
        word3: "---",
        displayWord1: "---",
        displayWord2: "---",
        displayWord3: "---",
        isSpinning: false,
        spinCompleted: false,
      }),
  }))
);
