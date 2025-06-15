import { create } from "zustand";
import { devtools } from "zustand/middleware";
import {
  clapWordsNouns,
  clapWordsVerbs,
  clapWordsPlaces,
} from "@/app/constants/SlotWords";
import type { ClapWordsState } from "./types";

interface ClapWordsStore extends ClapWordsState {
  setCurrentPhase: (phase: number) => void;
  addSelectedWord: (word: string) => void;
  setFlyingWords: (words: ClapWordsState["flyingWords"]) => void;
  updateFlyingWords: (
    updater: (
      words: ClapWordsState["flyingWords"]
    ) => ClapWordsState["flyingWords"]
  ) => void;
  reset: () => void;
  getWordsForPhase: (phase: number) => string[];
}

export const useClapWordsStore = create<ClapWordsStore>()(
  devtools((set, get) => ({
    // Initial state
    currentPhase: 0,
    selectedWords: [],
    flyingWords: [],

    // Helper
    getWordsForPhase: (phase) => {
      const wordsByPhase = [clapWordsNouns, clapWordsVerbs, clapWordsPlaces];
      if (phase >= 0 && phase < wordsByPhase.length) {
        return wordsByPhase[phase];
      }
      return [];
    },

    // Actions
    setCurrentPhase: (phase) => set({ currentPhase: phase }),

    addSelectedWord: (word) =>
      set((state) => ({
        selectedWords: [...state.selectedWords, word],
        currentPhase: state.currentPhase + 1,
      })),

    setFlyingWords: (words) => set({ flyingWords: words }),

    updateFlyingWords: (updater) =>
      set((state) => ({
        flyingWords: updater(state.flyingWords),
      })),

    reset: () =>
      set({
        currentPhase: 0,
        selectedWords: [],
        flyingWords: [],
      }),
  }))
);
