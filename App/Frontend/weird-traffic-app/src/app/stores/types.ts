import type { Message, ActiveView } from "../types/chat";
import type { DialogSequence } from "../constants/DialogMessages";

export type CarAnimationState =
  | "speaking"
  | "waiting"
  | "laughing"
  | "sad"
  | "scan"
  | "idle";

export interface GameState {
  // main game state
  messages: Message[];
  prompt: string;
  isLoadingGeneration: boolean;
  dialogSequence: DialogSequence;
  activeView: ActiveView;
  earnedPoints: number;
  trainingProgress: number;
  detectionCount: number;
  signalModalOpen: boolean;
  carAnimationState: CarAnimationState;
}

export interface UIState {
  // Modal states
  isInfoModalOpen: boolean;
  isShareModalOpen: boolean;
  isShareModal2Open: boolean;
  sharedImageUrlForModal2: string | null;

  // other UI states
  showCopiedTooltip: boolean;
  runTour: boolean;
  hasTutorialBeenShown: boolean;
  activeTab: "scoring" | "tips" | "goal" | "instructions";
}

export interface SlotMachineState {
  word1: string;
  word2: string;
  word3: string;
  displayWord1: string;
  displayWord2: string;
  displayWord3: string;
  isSpinning: boolean;
  spinCompleted: boolean;
}

export interface ClapWordsState {
  currentPhase: number;
  selectedWords: string[];
  flyingWords: Array<{
    id: number;
    text: string;
    x: number;
    y: number;
    dx: number;
    dy: number;
  }>;
}

export interface AnimationState {
  currentFrame: number;
}
