//DONT USED ANYMORE - USE stores/gameStore.ts INSTEAD
import { useState, useCallback, useEffect } from "react";
import type {
  Message,
  ActiveView,
  GeneratedImage,
  GeneratedImages,
} from "../types/chat";
import {
  DialogMessages,
  DialogSequence,
  updateDialogMessages,
  DetectionResultPayload, // Keep type here for now, or move to types/dialog.ts?
} from "../constants/DialogMessages"; // Note: Path might need update
import {
  calculateUserPoints,
  calculateProgressIncrement, // Now this will be used
} from "../utils/scoring"; // Note: Path will need update to lib/

// Define the expected type for the detection API response
type DetectApiResponse = {
  prompt: string; // The prompt used for detection
  score: number;
  imageBase64: string; // Add the detected image base64
  // Add other potential fields if the API returns more data
};
export type CarAnimationState =
  | "speaking"
  | "waiting"
  | "laughing"
  | "sad"
  | "scan"
  | "idle";

export function useChatLogic() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [prompt, setPrompt] = useState<string>("");
  const [isLoadingGeneration, setIsLoadingGeneration] =
    useState<boolean>(false);
  const [dialogSequence, setDialogSequence] = useState<DialogSequence>(
    DialogMessages.welcome
  );
  const [activeView, setActiveView] = useState<ActiveView>("chat");
  const [earnedPoints, setEarnedPoints] = useState<number>(0); // Consider if this state belongs here or at a higher level if shared
  const [trainingProgress, setTrainingProgress] = useState<number>(0); // Consider if this state belongs here or at a higher level
  const [detectionCount, setDetectionCount] = useState<number>(0); // Add detectionCount
  const [signalModalOpen, setSignalModalOpen] = useState<boolean>(false); // New state to signal modal opening
  const [carAnimationState, setCarAnimationState] =
    useState<CarAnimationState>("idle"); // Initial state is 'idle'

  // Function to reset the signal
  const resetSignalModalOpen = useCallback(() => {
    setSignalModalOpen(false);
    console.log("Modal open signal reset.");
  }, []);

  // Callback to finalize state updates after animation
  // Accepts currentDetectionCount as an argument to avoid stale closure issues
  const finalizeScoreUpdate = useCallback(
    (pointsToAdd: number, score: number, currentDetectionCount: number) => {
      const progressIncrement = calculateProgressIncrement(score);
      const currentProgress = trainingProgress; // Capture current progress before update

      console.log(
        `FinalizeUpdate: Called. Current detectionCount passed: ${currentDetectionCount}`
      );

      setEarnedPoints((prev) => prev + pointsToAdd);
      setTrainingProgress((prev) => Math.min(100, prev + progressIncrement));

      console.log(
        `Finalized Update: Points (${
          earnedPoints + pointsToAdd // Use argument directly for logging consistency if needed, though state will update
        }), Progress (${Math.min(
          100,
          currentProgress + progressIncrement
        ).toFixed(0)}%) updated.`
      );

      // Use the passed currentDetectionCount for the check
      if (currentDetectionCount >= 5) {
        console.log(
          `FinalizeUpdate: Condition met (currentDetectionCount: ${currentDetectionCount} >= 5). Signaling modal open.`
        );
        setSignalModalOpen(true);
      } else {
        console.log(
          `FinalizeUpdate: Condition NOT met (currentDetectionCount: ${currentDetectionCount} < 5). Not signaling.`
        );
      }
    },
    [trainingProgress, earnedPoints]
  );

  // Function to reset the detection counter
  const resetDetectionCount = useCallback(() => {
    setDetectionCount(0);
    console.log("Detection count reset.");
  }, []);

  // Function to run when image is selected
  const handleImageSelect = async (
    messageId: number,
    selectedImageBase64: string,
    selectedIndex: number
  ) => {
    console.log(
      `Selected image index: ${selectedIndex}, Base64 (start): ${selectedImageBase64.substring(
        0,
        30
      )}...`
    );

    let associatedPrompt = "";
    const imageGridMsgIndex = messages.findIndex((msg) => msg.id === messageId);
    if (
      imageGridMsgIndex > 0 &&
      messages[imageGridMsgIndex - 1].type === "user"
    ) {
      associatedPrompt = messages[imageGridMsgIndex - 1].content as string;
    } else {
      console.error(
        "Could not find the associated user prompt for the image grid."
      );
      // Potentially handle error state more explicitly
    }

    setMessages((prevMessages) =>
      prevMessages.map((msg) =>
        msg.id === messageId
          ? { ...msg, selectedImageIndex: selectedIndex, isDetecting: true }
          : msg
      )
    );

    setDialogSequence(DialogMessages.imageSelected);
    setCarAnimationState("scan");

    try {
      console.log(
        "Calling detection API for prompt:",
        associatedPrompt,
        "and selected image index:",
        selectedIndex
      );

      const response = await fetch("/api/detect", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: associatedPrompt,
          imageBase64: selectedImageBase64,
        }),
      });

      if (!response.ok) {
        const errorData = await response.text();
        console.error("Detection API call failed:", response.status, errorData);
        setMessages((prevMessages) =>
          prevMessages.map((msg) =>
            msg.id === messageId ? { ...msg, isDetecting: false } : msg
          )
        );
        setDialogSequence(DialogMessages.error);
        return;
      }

      const result: DetectApiResponse = await response.json();
      const score = result.score;
      const detectedImage = result.imageBase64; // Extract detectedImage
      const points = calculateUserPoints(score); // Calculate points based on score

      console.log(
        "Detection API call successful. Score:",
        score,
        "Points earned:",
        points
      );

      if (score >= 0 && score < 50) {
        setCarAnimationState("laughing");
      } else if (score >= 50 && score <= 100) {
        setCarAnimationState("sad");
      } else {
        setCarAnimationState("speaking");
      }

      setMessages((prevMessages) =>
        prevMessages.map((msg) =>
          msg.id === messageId
            ? {
                ...msg,
                isDetecting: false,
                detectedImageUrl: detectedImage, // Store the detected image URL
                lastDetectionScore: score, // Store score
                lastDetectionPoints: points, // Store points
              }
            : msg
        )
      );

      if (typeof score === "number") {
        // Increment detection count *after* successful API call and *before* setting dialog
        let updatedDetectionCount = 0;
        setDetectionCount((prev) => {
          updatedDetectionCount = prev + 1;
          console.log(
            `Detection count incremented to: ${updatedDetectionCount}`
          );
          return updatedDetectionCount;
        });

        // Now set the dialog sequence which will trigger the animation
        setDialogSequence(updateDialogMessages.detectionResult(score, points));
        console.log(
          `Calculated ${points} points. Dialog updated, waiting for animation to finalize state.`
        );
      } else {
        console.error("Invalid similarity score received:", score);
        setDialogSequence(DialogMessages.error);
      }
    } catch (error) {
      console.error("Error calling detection API:", error);
      setMessages((prevMessages) =>
        prevMessages.map((msg) =>
          msg.id === messageId ? { ...msg, isDetecting: false } : msg
        )
      );
      setDialogSequence(DialogMessages.error);
    }
  };

  // Function to handle prompt submission and image generation
  const handleGenerate = async () => {
    if (!prompt.trim() || isLoadingGeneration) return;

    setIsLoadingGeneration(true); // Set loading true at the beginning
    setCarAnimationState("waiting");

    if (activeView !== "chat") {
      setActiveView("chat");
    }
    setDialogSequence(DialogMessages.loading);

    const newUserMessage: Message = {
      id: Date.now(),
      type: "user",
      content: prompt,
    };
    const currentPrompt = prompt;
    setPrompt(""); // Clear prompt input after submission

    // Add user message first
    setMessages((prevMessages) => [...prevMessages, newUserMessage]);

    // Add placeholder for image grid while loading
    const loadingImageGridMessage: Message = {
      id: Date.now() + 1,
      type: "image_grid",
      content: [],
      isLoading: true,
    };
    setMessages((prevMessages) => [...prevMessages, loadingImageGridMessage]);

    try {
      console.log("Calling generation API for prompt:", currentPrompt);
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt: currentPrompt }),
      });

      if (!response.ok) {
        const errorData = await response.text();
        console.error(
          "Generation API call failed:",
          response.status,
          errorData
        );

        // Remove the loading image grid message on error
        setMessages((prevMessages) =>
          prevMessages.filter((msg) => msg.id !== loadingImageGridMessage.id)
        );
        setDialogSequence(DialogMessages.error);
        setIsLoadingGeneration(false);
        return;
      }

      //  Setting result and extracting base64 images
      const result: GeneratedImages = await response.json();
      const imageUrls = result.images.map(
        (img) => `data:image/png;base64,${img.imageBase64}`
      );

      setMessages((prevMessages) =>
        prevMessages.map((msg) =>
          msg.id === loadingImageGridMessage.id
            ? { ...msg, content: imageUrls, isLoading: false }
            : msg
        )
      );

      // Use the 'completed' message after generation is successful
      setDialogSequence(DialogMessages.completed);
    } catch (error) {
      console.error("Error calling generation API:", error);
      setMessages((prevMessages) =>
        prevMessages.filter((msg) => msg.id !== loadingImageGridMessage.id)
      );
      setDialogSequence(DialogMessages.error);
    } finally {
      setIsLoadingGeneration(false);
    }
  };

  const handleTypeAnimationComplete = useCallback(() => {
    setCarAnimationState((currentState) => {
      // States that should transition to 'idle' after their associated TypeAnimation completes
      const statesToIdleAfterTyping = [
        "speaking",
        "laughing",
        "sad",
        "waiting",
      ];
      if (statesToIdleAfterTyping.includes(currentState)) {
        console.log(
          `TypeAnimation complete, car state changing from "${currentState}" to "idle".`
        );
        return "idle";
      }
      console.log(
        `TypeAnimation complete, car state is "${currentState}", not changing to "idle" based on this rule.`
      );
      return currentState;
    });
  }, []);

  useEffect(() => {
    console.log(
      `Car Animation useEffect triggered. Dialog: ${dialogSequence.initial}, Current Car State: ${carAnimationState}`
    );

    const isApiInProgress =
      carAnimationState === "waiting" || carAnimationState === "scan";
    if (isApiInProgress) {
      console.log(
        "Car Animation: API call in progress, state will not be changed by this effect."
      );
      return;
    }

    const isDetectionResultDialog =
      typeof dialogSequence.expanded === "object" &&
      dialogSequence.expanded.type === "detectionResult";

    if (isDetectionResultDialog) {
      if (
        carAnimationState === "laughing" ||
        carAnimationState === "sad" ||
        carAnimationState === "speaking"
      ) {
        console.log(
          `Car Animation: Dialog is for detection result, car is appropriately '${carAnimationState}'. State preserved by useEffect.`
        );
        return;
      }
    }
    if (
      carAnimationState === "idle" ||
      (carAnimationState !== "laughing" && carAnimationState !== "sad")
    ) {
      console.log(
        `Car Animation: Setting car to 'speaking'. Current state: '${carAnimationState}', Dialog: '${dialogSequence.initial}'`
      );
      setCarAnimationState("speaking");
    } else {
      console.log(
        `Car Animation: Car is '${carAnimationState}', not changing to 'speaking' for dialog '${dialogSequence.initial}'.`
      );
    }
  }, [dialogSequence]); // Only dependent on dialogSequence.

  // Placeholder functions - Implement or remove if not needed by the hook
  // If they only interact with UI state not managed here, keep them in the component
  const handleCopyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
    // Optionally, provide feedback to the user (e.g., toast notification)
    console.log("Message copied:", content);
  };

  // Add alert to handleEditMessage
  const handleEditMessage = (messageId: number) => {
    const messageToEdit = messages.find(
      (msg) => msg.id === messageId && msg.type === "user"
    );
    if (messageToEdit && typeof messageToEdit.content === "string") {
      // Add the alert here
      alert(`Editing message: "${messageToEdit.content}"`);
      setPrompt(messageToEdit.content);
      // You might want to remove the original message from the list here
      // depending on the desired UX for editing. Example:
      // setMessages(prevMessages => prevMessages.filter(msg => msg.id !== messageId));
      console.log("Editing message:", messageId);
    }
  };

  // This directly manipulates the view state managed here
  const handleSwitchView = (view: ActiveView) => {
    setActiveView(view);

    // Set dialog based on the selected view
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
        // Reset to welcome only if coming from another view or if messages are empty
        // This prevents resetting the dialog unnecessarily during chat interaction
        if (activeView !== "chat" || messages.length === 0) {
          setDialogSequence(DialogMessages.welcome);
        } else {
          setDialogSequence(DialogMessages.welcome);
        }
        break;
      default:
        setDialogSequence(DialogMessages.welcome); // Default fallback
    }
  };

  return {
    messages,
    prompt,
    isLoadingGeneration,
    dialogSequence,
    activeView,
    earnedPoints,
    trainingProgress,
    detectionCount,
    signalModalOpen,
    carAnimationState,
    setPrompt,
    handleGenerate,
    handleImageSelect,
    handleCopyMessage,
    handleEditMessage,
    handleSwitchView,
    finalizeScoreUpdate,
    resetDetectionCount,
    resetSignalModalOpen,
    handleTypeAnimationComplete,
  };
}
