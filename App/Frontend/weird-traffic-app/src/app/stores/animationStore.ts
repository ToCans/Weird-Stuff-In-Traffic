// src/stores/animationStore.ts
import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { AnimationState } from "./types";

interface AnimationStore extends AnimationState {
  setCurrentFrame: (frame: number) => void;
  incrementFrame: (maxFrames: number) => void;
  reset: () => void;
}

export const useAnimationStore = create<AnimationStore>()(
  devtools((set, get) => ({
    // Initial state
    currentFrame: 0,

    // Actions
    setCurrentFrame: (frame) => set({ currentFrame: frame }),

    incrementFrame: (maxFrames) =>
      set((state) => ({
        currentFrame: (state.currentFrame + 1) % maxFrames,
      })),

    reset: () => set({ currentFrame: 0 }),
  }))
);
