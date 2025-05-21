"use client";

import React, { useState, useEffect } from "react";
import { Button } from "../ui/Button";
import { slotMachineWords } from "../../constants/SlotWords";
import { ArrowLeft } from "lucide-react";
import { RotateCcw } from "lucide-react";

// Define view types matching page.tsx
type ActiveView = "chat" | "slotmachine" | "clapwords" | "fillblank";

interface SlotmachineGameProps {
  prompt: string;
  setPrompt: (value: string) => void;
  setActiveView: (view: ActiveView) => void; // This now receives handleSwitchView from page.tsx
}

export const SlotmachineGame: React.FC<SlotmachineGameProps> = ({
  prompt,
  setPrompt,
  setActiveView,
}) => {
  const [word1, setWord1] = useState("---");
  const [word2, setWord2] = useState("---");
  const [word3, setWord3] = useState("---");
  const [displayWord1, setDisplayWord1] = useState("---");
  const [displayWord2, setDisplayWord2] = useState("---");
  const [displayWord3, setDisplayWord3] = useState("---");
  const [isSpinning, setIsSpinning] = useState(false);
  const [spinCompleted, setSpinCompleted] = useState(false);

  // Helper function to get a random word from a list
  const getRandomWord = (category: string[]): string => {
    if (!category || category.length === 0) {
      return ""; // Handle empty category
    }
    return category[Math.floor(Math.random() * category.length)];
  };

  // Function to spin the words
  const handleSpin = () => {
    if (isSpinning) return; // Do nothing if already spinning

    setIsSpinning(true);
    setSpinCompleted(false); // Reset completion on new spin

    // Placeholder for final words, set after timeout
    setWord1("");
    setWord2("");
    setWord3("");

    // Start timeout for spin duration
    const spinTimeout = setTimeout(() => {
      const finalWord1 = getRandomWord(slotMachineWords.nouns);
      const finalWord2 = getRandomWord(slotMachineWords.verbs);
      const finalWord3 = getRandomWord(slotMachineWords.places);

      setWord1(finalWord1);
      setWord2(finalWord2);
      setWord3(finalWord3);

      setDisplayWord1(finalWord1);
      setDisplayWord2(finalWord2);
      setDisplayWord3(finalWord3);

      setIsSpinning(false);
      setSpinCompleted(true);
    }, 3000); // 5 seconds spin duration

    // Cleanup timeout if component unmounts or spin is re-triggered
    return () => clearTimeout(spinTimeout);
  };

  // Effect for the spinning animation interval
  useEffect(() => {
    let animationInterval: ReturnType<typeof setInterval> | undefined;
    if (isSpinning) {
      animationInterval = setInterval(() => {
        setDisplayWord1(getRandomWord(slotMachineWords.nouns));
        setDisplayWord2(getRandomWord(slotMachineWords.verbs));
        setDisplayWord3(getRandomWord(slotMachineWords.places));
      }, 50); // Update every 50ms for fast visual effect
    } else {
      // If not spinning, ensure display words match final words (or initial '---')
      setDisplayWord1(word1 || "---");
      setDisplayWord2(word2 || "---");
      setDisplayWord3(word3 || "---");
    }

    // Cleanup interval on unmount or when isSpinning becomes false
    return () => {
      if (animationInterval) {
        clearInterval(animationInterval);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isSpinning, word1, word2, word3]); // Add word states to dependency array

  // Function to handle clicking on a word box
  const handleWordClick = (word: string) => {
    if (isSpinning || !word || word === "---") return;
    setPrompt(prompt ? `${prompt} ${word}` : word);
  };

  // Function to handle key down events for accessibility
  const handleWordKeyDown = (
    event: React.KeyboardEvent<HTMLDivElement>,
    word: string
  ) => {
    if (isSpinning || !word || word === "---") return;
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      handleWordClick(word);
    }
  };

  // Function to handle back navigation
  const handleBackToChat = () => {
    setActiveView("chat");
  };

  // Function to handle key down for the back button
  const handleBackKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      handleBackToChat();
    }
  };

  const handleUsePrompt = () => {
    if (!word1 || !word2 || !word3) return; // Don't use if words are not set
    const fullPrompt = `${word1} ${word2} ${word3}`;
    setPrompt(fullPrompt);
    // Optionally navigate back or indicate success
    // setActiveView('chat'); // Example navigation
  };

  const handleUseKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      handleUsePrompt();
    }
  };

  const handleReloadKeyDown = (
    event: React.KeyboardEvent<HTMLButtonElement>
  ) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      handleSpin();
    }
  };

  return (
    <div className="relative flex flex-col items-center justify-center h-full pt-16 p-4 sm:pt-4 gap-6 animate-slide-up-fade-in overflow-hidden">
      {/* Back to Chat Button */}
      <button
        onClick={handleBackToChat}
        onKeyDown={handleBackKeyDown}
        className="absolute top-4 left-4 z-10 flex items-center gap-2 text-white font-mono text-sm hover:underline cursor-pointer"
        aria-label="Back to chat view"
      >
        <ArrowLeft size={18} />
        <span>Back to chat</span>
      </button>

      <h2 className="text-[24px] font-mono text-white mb-2 text-center mt-8">
        Spin the slotmachine, until you have a prompt you like!
      </h2>
      {/* Word Boxes */}
      <div className="flex flex-col sm:flex-row gap-4 mb-4 w-full max-w-md justify-center">
        {/* Box 1 - Noun */}
        <div
          className={`bg-[var(--dark-gray)] p-4 border-2 border-[var(--green)] rounded-[24px] text-white font-mono font-regular min-w-[260px] text-center transition-all duration-200 ${
            !isSpinning && spinCompleted
              ? "cursor-pointer hover:shadow-[0_0_16px_#B9E55A] hover:scale-[1.02]"
              : "cursor-default"
          } ${isSpinning ? "animate-pulse" : ""}`}
          onClick={() => handleWordClick(displayWord1)}
          onKeyDown={(e) => handleWordKeyDown(e, displayWord1)}
          tabIndex={!isSpinning && spinCompleted ? 0 : -1}
          role="button"
          aria-live="polite"
          aria-label={`Noun: ${
            isSpinning ? "Spinning" : displayWord1 || "---"
          }. ${!isSpinning && spinCompleted ? "Click to add to prompt." : ""}`}
        >
          {displayWord1}
        </div>
        {/* Box 2 - Verb */}
        <div
          className={`bg-[var(--dark-gray)] p-4 border-2 border-[var(--green)] rounded-[24px] text-white font-mono font-regular min-w-[260px] text-center transition-all duration-200 ${
            !isSpinning && spinCompleted
              ? "cursor-pointer hover:shadow-[0_0_16px_#B9E55A] hover:scale-[1.02]"
              : "cursor-default"
          } ${isSpinning ? "animate-pulse" : ""}`}
          onClick={() => handleWordClick(displayWord2)}
          onKeyDown={(e) => handleWordKeyDown(e, displayWord2)}
          tabIndex={!isSpinning && spinCompleted ? 0 : -1}
          role="button"
          aria-live="polite"
          aria-label={`Verb: ${
            isSpinning ? "Spinning" : displayWord2 || "---"
          }. ${!isSpinning && spinCompleted ? "Click to add to prompt." : ""}`}
        >
          {displayWord2}
        </div>
        {/* Box 3 - Place */}
        <div
          className={`bg-[var(--dark-gray)] p-4 border-2 border-[var(--green)] rounded-[24px] text-white font-mono font-regular min-w-[260px] text-center transition-all duration-200 ${
            !isSpinning && spinCompleted
              ? "cursor-pointer hover:shadow-[0_0_16px_#B9E55A] hover:scale-[1.02]"
              : "cursor-default"
          } ${isSpinning ? "animate-pulse" : ""}`}
          onClick={() => handleWordClick(displayWord3)}
          onKeyDown={(e) => handleWordKeyDown(e, displayWord3)}
          tabIndex={!isSpinning && spinCompleted ? 0 : -1}
          role="button"
          aria-live="polite"
          aria-label={`Place: ${
            isSpinning ? "Spinning" : displayWord3 || "---"
          }. ${!isSpinning && spinCompleted ? "Click to add to prompt." : ""}`}
        >
          {displayWord3}
        </div>
      </div>

      {/* Control Buttons */}
      <div className="flex items-center gap-4">
        {/* Initial Spin Button */}
        {!spinCompleted && !isSpinning && (
          <Button
            onClick={handleSpin}
            className="font-mono transition-transform duration-200"
            aria-label="Spin words"
          >
            Spin
          </Button>
        )}

        {/* Spinning Indicator */}
        {isSpinning && (
          <button
            className="font-mono bg-[var(--gray)] text-foreground px-6 py-3 rounded-2xl cursor-not-allowed"
            disabled={true}
            aria-label="Spinning in progress"
          >
            Spinning...
          </button>
        )}

        {/* Use and Reload Buttons */}
        {spinCompleted && !isSpinning && (
          <>
            <Button
              onClick={handleUsePrompt}
              className="font-mono hover:shadow-[0_0_16px_#B9E55A]"
              aria-label={`Use prompt: ${word1} ${word2} ${word3}`}
            >
              Use
            </Button>
            <button
              onClick={handleSpin}
              onKeyDown={handleReloadKeyDown}
              className="p-2 rounded-[12px] text-foreground hover:shadow-[0_0_16px_#B9E55A] hover:scale-[1.02] transition-colors duration-200 cursor-pointer"
              aria-label="Spin again"
            >
              <RotateCcw size={20} />
            </button>
          </>
        )}
      </div>
    </div>
  );
};
