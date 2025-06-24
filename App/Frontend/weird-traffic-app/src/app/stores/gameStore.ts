// src/stores/gameStore.ts
import { create } from "zustand";
import { devtools, persist, createJSONStorage } from "zustand/middleware";
import type { GameState, CarAnimationState } from "./types";
import {
  DialogMessages,
  updateDialogMessages,
  type DialogSequence,
} from "@/app/constants/DialogMessages";
import {
  calculateUserPoints,
  calculateProgressIncrement,
} from "@/app/utils/scoring";
import {
  Message,
  ActiveView,
  GeneratedImages,
  DetectApiResponse,
} from "../types/chat";

interface GameStore extends GameState {
  // Actions
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  updateMessage: (id: number, updates: Partial<Message>) => void;
  setPrompt: (prompt: string) => void;
  setIsLoadingGeneration: (loading: boolean) => void;
  setDialogSequence: (sequence: DialogSequence) => void;
  setActiveView: (view: ActiveView) => void;
  setCarAnimationState: (state: CarAnimationState) => void;
  updateScore: (points: number) => void;
  updateProgress: (progress: number) => void;
  incrementDetectionCount: () => void;
  resetDetectionCount: () => void;
  setSignalModalOpen: (open: boolean) => void;

  // Complex actions
  handleGenerate: () => Promise<void>;
  handleImageSelect: (
    messageId: number,
    selectedImageBase64: string,
    selectedIndex: number
  ) => Promise<void>;
  finalizeScoreUpdate: (
    pointsToAdd: number,
    score: number,
    currentDetectionCount: number
  ) => void;
  handleSwitchView: (view: ActiveView) => void;
  handleTypeAnimationComplete: () => void;
  handleCopyMessage: (content: string) => void;
  handleEditMessage: (messageId: number) => void;
}

export const useGameStore = create<GameStore>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        messages: [],
        prompt: "",
        isLoadingGeneration: false,
        dialogSequence: DialogMessages.welcome,
        activeView: "chat",
        earnedPoints: 0,
        trainingProgress: 0,
        detectionCount: 0,
        signalModalOpen: false,
        carAnimationState: "speaking",

        // Actions
        setMessages: (messages) => set({ messages }),
        addMessage: (message) =>
          set((state) => ({
            messages: [...state.messages, message],
          })),
        updateMessage: (id, updates) =>
          set((state) => ({
            messages: state.messages.map((msg) =>
              msg.id === id ? { ...msg, ...updates } : msg
            ),
          })),
        setPrompt: (prompt) => set({ prompt }),
        setIsLoadingGeneration: (loading) =>
          set({ isLoadingGeneration: loading }),
        setDialogSequence: (sequence) => {
          const { carAnimationState } = get();

          // Don't interrupt a specific emotional or processing animation
          // unless the new dialog requires a specific state.
          if (
            sequence === DialogMessages.loading &&
            (carAnimationState === "waiting" || carAnimationState === "scan")
          ) {
            set({ dialogSequence: sequence });
            return;
          }

          if (carAnimationState === "laughing" || carAnimationState === "sad") {
            set({ dialogSequence: sequence });
            return;
          }

          // For all other cases (e.g., transitioning from 'waiting' to 'completed'),
          // set the state to 'speaking'.
          set({
            dialogSequence: sequence,
            carAnimationState: "speaking",
          });
        },
        setActiveView: (view) => set({ activeView: view }),
        setCarAnimationState: (state) => set({ carAnimationState: state }),
        updateScore: (points) =>
          set((state) => ({
            earnedPoints: state.earnedPoints + points,
          })),
        updateProgress: (progress) =>
          set((state) => ({
            trainingProgress: Math.min(100, state.trainingProgress + progress),
          })),
        incrementDetectionCount: () =>
          set((state) => ({
            detectionCount: state.detectionCount + 1,
          })),
        resetDetectionCount: () => set({ detectionCount: 0 }),
        setSignalModalOpen: (open) => set({ signalModalOpen: open }),

        // Complex actions - useChatLogic'teki logic'leri buraya taşı
        handleGenerate: async () => {
          const {
            prompt,
            setIsLoadingGeneration,
            addMessage,
            setDialogSequence,
            setCarAnimationState,
            setActiveView,
            activeView,
          } = get();

          if (!prompt.trim() || get().isLoadingGeneration) return;

          setIsLoadingGeneration(true);
          setCarAnimationState("waiting");

          if (activeView !== "chat") {
            setActiveView("chat");
          }
          setDialogSequence(DialogMessages.loading);

          const newUserMessage = {
            id: Date.now(),
            type: "user" as const,
            content: prompt,
          };

          const loadingImageGridMessage = {
            id: Date.now() + 1,
            type: "image_grid" as const,
            content: [],
            isLoading: true,
          };

          addMessage(newUserMessage);
          set({ prompt: "" });
          addMessage(loadingImageGridMessage);

          try {
            const response = await fetch("/api/generate", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ prompt }),
            });

            if (!response.ok) {
              const errorData = await response.text();
              console.error(
                "Generation API call failed:",
                response.status,
                errorData
              );

              set((state) => ({
                messages: state.messages.filter(
                  (msg) => msg.id !== loadingImageGridMessage.id
                ),
              }));
              setDialogSequence(DialogMessages.error);
              return;
            }

            const result: GeneratedImages = await response.json();
            const imageUrls = result.images.map(
              (img) => `data:image/png;base64,${img.imageBase64}`
            );

            get().updateMessage(loadingImageGridMessage.id, {
              content: imageUrls,
              isLoading: false,
            });

            setDialogSequence(DialogMessages.completed);
          } catch (error) {
            console.error("Error calling generation API:", error);
            set((state) => ({
              messages: state.messages.filter(
                (msg) => msg.id !== loadingImageGridMessage.id
              ),
            }));
            setDialogSequence(DialogMessages.error);
          } finally {
            setIsLoadingGeneration(false);
          }
        },

        handleImageSelect: async (
          messageId,
          selectedImageBase64,
          selectedIndex
        ) => {
          console.log(
            `Selected image index: ${selectedIndex}, Base64 (start): ${selectedImageBase64.substring(
              0,
              30
            )}...`
          );

          let associatedPrompt = "";
          const {
            messages,
            updateMessage,
            setDialogSequence,
            setCarAnimationState,
          } = get();

          const imageGridMsgIndex = messages.findIndex(
            (msg) => msg.id === messageId
          );
          if (
            imageGridMsgIndex > 0 &&
            messages[imageGridMsgIndex - 1].type === "user"
          ) {
            associatedPrompt = messages[imageGridMsgIndex - 1]
              .content as string;
          } else {
            console.error(
              "Could not find the associated user prompt for the image grid."
            );
          }

          updateMessage(messageId, {
            selectedImageIndex: selectedIndex,
            isDetecting: true,
          });

          setDialogSequence(DialogMessages.imageSelected);
          setCarAnimationState("scan");

          try {
            const response = await fetch("/api/detect", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                prompt: associatedPrompt,
                imageBase64: selectedImageBase64,
              }),
            });

            if (!response.ok) {
              const errorData = await response.text();
              console.error(
                "Detection API call failed:",
                response.status,
                errorData
              );
              updateMessage(messageId, { isDetecting: false });
              setDialogSequence(DialogMessages.error);
              return;
            }

            const result: DetectApiResponse = await response.json();
            const score = result.score;
            const detectedImage = result.imageBase64;
            const points = calculateUserPoints(score);

            if (score >= 0 && score < 50) {
              setCarAnimationState("laughing");
            } else if (score >= 50 && score <= 100) {
              setCarAnimationState("sad");
            } else {
              setCarAnimationState("speaking");
            }

            updateMessage(messageId, {
              isDetecting: false,
              detectedImageUrl: detectedImage,
              lastDetectionAccuracy: score,
              lastDetectionPoints: points,
            });

            if (typeof score === "number") {
              const currentDetectionCount = get().detectionCount + 1;
              get().incrementDetectionCount();

              setDialogSequence(
                updateDialogMessages.detectionResult(score, points)
              );
            } else {
              console.error("Invalid score received:", score);
              setDialogSequence(DialogMessages.error);
            }
          } catch (error) {
            console.error("Error calling detection API:", error);
            updateMessage(messageId, { isDetecting: false });
            setDialogSequence(DialogMessages.error);
          }
        },

        finalizeScoreUpdate: (pointsToAdd, score, currentDetectionCount) => {
          const progressIncrement = calculateProgressIncrement(score);
          const { updateScore, updateProgress, setSignalModalOpen } = get();

          updateScore(pointsToAdd);
          updateProgress(progressIncrement);

          if (currentDetectionCount >= 5) {
            setSignalModalOpen(true);
          }
        },

        handleSwitchView: (view) => {
          const { setDialogSequence } = get();
          set({ activeView: view });

          switch (view) {
            case "slotmachine":
              setDialogSequence(DialogMessages.slotMachineWelcome);
              break;
            case "clapwords":
              setDialogSequence(DialogMessages.clapWordsWelcome);
              break;
            case "fillblank":
              setDialogSequence(DialogMessages.fillBlankWelcome);
              break;
            case "chat":
              setDialogSequence(DialogMessages.welcome);
              break;
            default:
              setDialogSequence(DialogMessages.welcome);
          }
        },

        handleTypeAnimationComplete: () => {
          const { carAnimationState } = get();
          const statesToIdleAfterTyping = [
            "speaking",
            "laughing",
            "sad",
            "waiting",
          ];

          if (statesToIdleAfterTyping.includes(carAnimationState)) {
            set({ carAnimationState: "idle" });
          }
        },

        handleCopyMessage: (content: string) => {
          navigator.clipboard.writeText(content);
          console.log("Message copied:", content);
        },

        handleEditMessage: (messageId: number) => {
          const { messages, setPrompt } = get();
          const messageToEdit = messages.find(
            (msg) => msg.id === messageId && msg.type === "user"
          );
          if (messageToEdit && typeof messageToEdit.content === "string") {
            alert(`Editing message: "${messageToEdit.content}"`);
            setPrompt(messageToEdit.content);
            console.log("Editing message:", messageId);
          }
        },
      }),
      {
        name: "weird-traffic-game",
        storage: createJSONStorage(() => sessionStorage),
        partialize: (state) => ({
          earnedPoints: state.earnedPoints,
          trainingProgress: state.trainingProgress,
          detectionCount: state.detectionCount,
        }),
      }
    )
  )
);
