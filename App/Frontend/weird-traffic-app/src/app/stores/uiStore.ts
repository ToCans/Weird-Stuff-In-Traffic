// src/stores/uiStore.ts
import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { UIState } from "./types";

interface UIStore extends UIState {
  // Modal actions
  toggleInfoModal: () => void;
  toggleShareModal: () => void;
  toggleShareModal2: (imageUrl?: string) => void;
  closeAllModals: () => void;

  // UI actions
  setShowCopiedTooltip: (show: boolean) => void;
  setRunTour: (run: boolean) => void;
  setActiveTab: (tab: UIState["activeTab"]) => void;
}

export const useUIStore = create<UIStore>()(
  devtools((set) => ({
    // Initial state
    isInfoModalOpen: false,
    isShareModalOpen: false,
    isShareModal2Open: false,
    sharedImageUrlForModal2: null,
    showCopiedTooltip: false,
    runTour: false,
    activeTab: "scoring",

    // Actions
    toggleInfoModal: () =>
      set((state) => ({
        isInfoModalOpen: !state.isInfoModalOpen,
      })),

    toggleShareModal: () =>
      set((state) => ({
        isShareModalOpen: !state.isShareModalOpen,
      })),

    toggleShareModal2: (imageUrl) =>
      set((state) => ({
        isShareModal2Open: imageUrl ? true : !state.isShareModal2Open,
        sharedImageUrlForModal2: imageUrl || null,
      })),

    closeAllModals: () =>
      set({
        isInfoModalOpen: false,
        isShareModalOpen: false,
        isShareModal2Open: false,
        sharedImageUrlForModal2: null,
      }),

    setShowCopiedTooltip: (show) => set({ showCopiedTooltip: show }),
    setRunTour: (run) => set({ runTour: run }),
    setActiveTab: (tab) => set({ activeTab: tab }),
  }))
);
