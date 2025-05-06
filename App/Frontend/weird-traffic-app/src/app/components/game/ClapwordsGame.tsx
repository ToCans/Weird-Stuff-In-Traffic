"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { Button } from "../ui/Button";
import {
  clapWordsNouns,
  clapWordsVerbs,
  clapWordsPlaces,
} from "../../constants/SlotWords";
import { ArrowLeft, RotateCcw } from "lucide-react";

// Define view types matching page.tsx
type ActiveView = "chat" | "slotmachine" | "clapwords" | "fillblank";

interface ClapwordsGameProps {
  setPrompt: (value: string) => void;
  setActiveView: (view: ActiveView) => void;
}

interface FlyingWord {
  id: number;
  text: string;
  x: number;
  y: number;
  dx: number;
  dy: number;
}

const phaseInstructions = [
  "Clap a noun",
  "Clap a verb",
  "Clap a place/situation",
  "Done! 🚦",
];

const wordsByPhase = [clapWordsNouns, clapWordsVerbs, clapWordsPlaces];

export const ClapwordsGame: React.FC<ClapwordsGameProps> = ({
  setPrompt,
  setActiveView,
}) => {
  const [currentPhase, setCurrentPhase] = useState<number>(0);
  const [selectedWords, setSelectedWords] = useState<string[]>([]);
  const [flyingWords, setFlyingWords] = useState<FlyingWord[]>([]);
  const containerRef = useRef<HTMLDivElement>(null);
  const animationRef = useRef<number | null>(null);

  const getWordsForPhase = useCallback((phase: number): string[] => {
    if (phase >= 0 && phase < wordsByPhase.length) {
      return wordsByPhase[phase];
    }
    return [];
  }, []);

  const spawnWords = useCallback(() => {
    if (!containerRef.current || currentPhase >= wordsByPhase.length) return;

    const words = getWordsForPhase(currentPhase);
    const containerRect = containerRef.current.getBoundingClientRect();
    const newFlyingWords: FlyingWord[] = words.map((text, index) => {
      // Ensure words don't spawn too close to edges
      const maxX = containerRect.width - 150;
      const maxY = containerRect.height - 100;

      return {
        id: Date.now() + index,
        text,
        x: Math.max(10, Math.random() * maxX),
        y: Math.max(10, Math.random() * maxY),
        dx: (Math.random() - 0.5) * 2, // Horizontal speed
        dy: (Math.random() - 0.5) * 2, // Vertical speed
      };
    });
    setFlyingWords(newFlyingWords);
  }, [currentPhase, getWordsForPhase]);

  const animateWords = useCallback(() => {
    if (!containerRef.current) return;

    const containerRect = containerRef.current.getBoundingClientRect();
    const containerWidth = containerRect.width;
    const containerHeight = containerRect.height;

    setFlyingWords((prevWords) =>
      prevWords.map((word) => {
        let { x, y, dx, dy } = word;

        x += dx;
        y += dy;

        const wordWidth = 120;
        const wordHeight = 36;

        // Bounce off edges
        if (x <= 0 || x >= containerWidth - wordWidth) {
          dx = -dx;
          x = x <= 0 ? 0 : containerWidth - wordWidth;
        }

        if (y <= 0 || y >= containerHeight - wordHeight - 70) {
          dy = -dy;
          y = y <= 0 ? 0 : containerHeight - wordHeight - 70;
        }

        return { ...word, x, y, dx, dy };
      })
    );

    animationRef.current = requestAnimationFrame(animateWords);
  }, []);

  useEffect(() => {
    // Spawn words when component mounts or phase changes
    spawnWords();

    // Start animation loop
    animationRef.current = requestAnimationFrame(animateWords);

    // Clean up animation on unmount or phase change
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [currentPhase, spawnWords, animateWords]);

  const handleWordClick = (word: FlyingWord) => {
    if (currentPhase >= wordsByPhase.length) return;

    // Add the selected word to our array
    const newSelectedWords = [...selectedWords, word.text];
    setSelectedWords(newSelectedWords);

    // Update the prompt with the current selection immediately
    setPrompt(newSelectedWords.join(" "));

    // Move to next phase
    setCurrentPhase((prev) => prev + 1);
  };

  const handleWordKeyDown = (
    event: React.KeyboardEvent<HTMLDivElement>,
    word: FlyingWord
  ) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      handleWordClick(word);
    }
  };

  const handleBackToChat = () => {
    setActiveView("chat");
  };

  const handleRestart = () => {
    setSelectedWords([]);
    setCurrentPhase(0);
  };

  return (
    <div
      ref={containerRef}
      className="relative flex flex-col items-center justify-center h-full w-full pt-16 p-4 sm:pt-4 gap-6 animate-slide-up-fade-in overflow-hidden"
    >
      {/* Back to Chat Button */}
      <button
        onClick={handleBackToChat}
        className="absolute top-4 left-4 z-20 flex items-center gap-2 text-white font-mono text-sm hover:underline cursor-pointer"
        aria-label="Back to chat view"
        tabIndex={0}
      >
        <ArrowLeft size={18} />
        <span>Back to chat</span>
      </button>

      {/* Instruction Text */}
      <div
        className="absolute top-4 left-1/2 transform -translate-x-1/2 z-20 text-white font-mono px-4 py-2"
        aria-live="polite"
      >
        {phaseInstructions[currentPhase]}
      </div>

      {/* Flying Words Area */}
      <div className="absolute inset-0 w-full h-full z-10">
        {flyingWords.map((word) => (
          <div
            key={word.id}
            className="absolute bg-[#333333] text-white font-mono text-sm px-4 py-2 rounded-[24px] border border-[#444444] cursor-pointer hover:bg-[var(--green)] hover:text-black hover:scale-105 transition-all duration-150"
            style={{
              left: `${word.x}px`,
              top: `${word.y}px`,
            }}
            onClick={() => handleWordClick(word)}
            onKeyDown={(e) => handleWordKeyDown(e, word)}
            role="button"
            tabIndex={0}
            aria-label={word.text}
          >
            {word.text}
          </div>
        ))}
      </div>

      {/* Bottom Bar - Sentence Preview and Controls */}
      <div className="absolute bottom-5 left-1/2 transform -translate-x-1/2 z-20 flex items-center gap-4">
        {/* Show selected words preview */}
        {selectedWords.length > 0 && (
          <div className="bg-[var(--dark-gray)] text-white font-mono px-4 py-2 rounded-2xl">
            {selectedWords.join(" ")}
            {currentPhase < wordsByPhase.length ? "..." : "."}
          </div>
        )}

        {/* Show Restart button when done */}
        {currentPhase === wordsByPhase.length && (
          <button
            onClick={handleRestart}
            className="p-2 rounded-[12px] text-foreground hover:shadow-[0_0_16px_#B9E55A] hover:scale-[1.02] transition-colors duration-200 cursor-pointer"
            aria-label="Start again"
            tabIndex={0}
          >
            <RotateCcw size={20} />
          </button>
        )}
      </div>
    </div>
  );
};
