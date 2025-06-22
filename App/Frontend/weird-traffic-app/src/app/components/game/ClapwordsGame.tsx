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

const WORD_WIDTH = 120; // Approximate width of a word element
const WORD_HEIGHT = 36; // Approximate height of a word element
const WORD_SPAWN_PADDING = 5; // Minimum padding between spawned words

const phaseInstructions = [
  "Clap a noun",
  "Clap a verb",
  "Clap a place/situation",
  "Done! 🚦",
];

const wordsByPhase = [clapWordsNouns, clapWordsVerbs, clapWordsPlaces];

// Helper function to check for rectangle overlap
const rectsOverlap = (
  rect1: { x: number; y: number; width: number; height: number },
  rect2: { x: number; y: number; width: number; height: number },
  padding = 0
) => {
  return (
    rect1.x < rect2.x + rect2.width + padding &&
    rect1.x + rect1.width + padding > rect2.x &&
    rect1.y < rect2.y + rect2.height + padding &&
    rect1.y + rect1.height + padding > rect2.y
  );
};

export const ClapwordsGame: React.FC<ClapwordsGameProps> = ({
  setPrompt,
  setActiveView,
}) => {
  const [currentPhase, setCurrentPhase] = useState<number>(0);
  const [selectedWords, setSelectedWords] = useState<string[]>([]);
  const [flyingWords, setFlyingWords] = useState<FlyingWord[]>([]);
  const containerRef = useRef<HTMLDivElement>(null);
  const animationRef = useRef<number | null>(null);

  const flyingWordsTopOffset = 60;
  const flyingWordsBottomOffset = 70;

  const getWordsForPhase = useCallback((phase: number): string[] => {
    if (phase >= 0 && phase < wordsByPhase.length) {
      return wordsByPhase[phase];
    }
    return [];
  }, []);

  const spawnWords = useCallback(() => {
    if (!containerRef.current || currentPhase >= wordsByPhase.length) {
      setFlyingWords([]);
      return;
    }

    const gameAreaRect = containerRef.current.getBoundingClientRect();
    const minFlyableAreaHeight = WORD_HEIGHT + 20;
    const minGameAreaHeight =
      flyingWordsTopOffset + flyingWordsBottomOffset + minFlyableAreaHeight;
    const minGameAreaWidth = WORD_WIDTH + 30;

    if (
      gameAreaRect.width < minGameAreaWidth ||
      gameAreaRect.height < minGameAreaHeight
    ) {
      setFlyingWords([]);
      return;
    }

    const wordsToSpawn = getWordsForPhase(currentPhase);
    const availableHeightForFlying = Math.max(
      0,
      gameAreaRect.height - flyingWordsTopOffset - flyingWordsBottomOffset
    );
    const spawnableRegionHeight = Math.max(
      0,
      availableHeightForFlying - WORD_HEIGHT
    );
    const spawnableRegionWidth = Math.max(
      0,
      gameAreaRect.width - WORD_WIDTH - 20 // 10px margin each side
    );

    const newFlyingWordsArray: FlyingWord[] = [];
    const MAX_PLACEMENT_ATTEMPTS_PER_WORD = 15;
    const MIN_SPEED = 0.5;
    const MAX_SPEED_FACTOR = 1.5; // Max speed will be around 1.5px/frame

    for (const [index, text] of wordsToSpawn.entries()) {
      let placed = false;
      let finalX = 0,
        finalY = 0,
        finalDx = 0,
        finalDy = 0;

      for (
        let attempt = 0;
        attempt < MAX_PLACEMENT_ATTEMPTS_PER_WORD;
        attempt++
      ) {
        let dx_val, dy_val;
        do {
          dx_val = (Math.random() - 0.5) * 2 * MAX_SPEED_FACTOR;
          dy_val = (Math.random() - 0.5) * 2 * MAX_SPEED_FACTOR;
          if (dx_val !== 0 && Math.abs(dx_val) < MIN_SPEED)
            dx_val = Math.sign(dx_val) * MIN_SPEED;
          if (dy_val !== 0 && Math.abs(dy_val) < MIN_SPEED)
            dy_val = Math.sign(dy_val) * MIN_SPEED;
        } while (dx_val === 0 && dy_val === 0);

        const potentialX = 10 + Math.random() * spawnableRegionWidth;
        const potentialY = Math.random() * spawnableRegionHeight;
        const currentWordRect = {
          x: potentialX,
          y: potentialY,
          width: WORD_WIDTH,
          height: WORD_HEIGHT,
        };

        let isOverlapping = false;
        for (const existingWord of newFlyingWordsArray) {
          const existingWordRect = {
            x: existingWord.x,
            y: existingWord.y,
            width: WORD_WIDTH,
            height: WORD_HEIGHT,
          };
          if (
            rectsOverlap(currentWordRect, existingWordRect, WORD_SPAWN_PADDING)
          ) {
            isOverlapping = true;
            break;
          }
        }

        finalX = potentialX; // Store last attempted details
        finalY = potentialY;
        finalDx = dx_val;
        finalDy = dy_val;

        if (!isOverlapping) {
          placed = true;
          break;
        }
      }

      // Add the word, using the last attempted position (even if it might overlap after max attempts)
      newFlyingWordsArray.push({
        id: Date.now() + Math.random() * 1000 + index, // Unique ID
        text,
        x: finalX,
        y: finalY,
        dx: finalDx,
        dy: finalDy,
      });
    }
    setFlyingWords(newFlyingWordsArray);
  }, [
    currentPhase,
    getWordsForPhase,
    flyingWordsTopOffset,
    flyingWordsBottomOffset,
  ]);

  const animateWords = useCallback(() => {
    if (!containerRef.current) {
      animationRef.current = requestAnimationFrame(animateWords);
      return;
    }

    const gameAreaRect = containerRef.current.getBoundingClientRect();

    const minRequiredHeightForAnimation =
      flyingWordsTopOffset + flyingWordsBottomOffset + WORD_HEIGHT;
    if (
      gameAreaRect.height < minRequiredHeightForAnimation ||
      gameAreaRect.width < WORD_WIDTH
    ) {
      animationRef.current = requestAnimationFrame(animateWords);
      return;
    }

    const availableHeightForFlying = Math.max(
      0,
      gameAreaRect.height - flyingWordsTopOffset - flyingWordsBottomOffset
    );

    setFlyingWords((prevWords) => {
      if (prevWords.length === 0) return [];
      return prevWords.map((word) => {
        let { x, y, dx, dy } = word;

        x += dx;
        y += dy;

        const rightBoundaryX = Math.max(0, gameAreaRect.width - WORD_WIDTH);
        const bottomBoundaryY = Math.max(
          0,
          availableHeightForFlying - WORD_HEIGHT
        );

        if (x <= 0 || x >= rightBoundaryX) {
          dx = -dx;
          x = x <= 0 ? 0 : rightBoundaryX;
        }

        if (y <= 0 || y >= bottomBoundaryY) {
          dy = -dy;
          y = y <= 0 ? 0 : bottomBoundaryY;
        }

        // Ensure velocities don't accidentally become zero and stay zero if they were non-zero
        if (dx === 0 && dy === 0 && (word.dx !== 0 || word.dy !== 0)) {
          dx = (Math.random() - 0.5) * 0.4 || 0.2;
          dy = (Math.random() - 0.5) * 0.4 || 0.2;
        }

        return { ...word, x, y, dx, dy };
      });
    });

    animationRef.current = requestAnimationFrame(animateWords);
  }, [flyingWordsTopOffset, flyingWordsBottomOffset]);

  useEffect(() => {
    spawnWords(); // Attempt to spawn words for the current phase

    // Ensure animation loop is running.
    // cancelAnimationFrame will be called if animationRef.current already has a value.
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    animationRef.current = requestAnimationFrame(animateWords);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }
    };
  }, [currentPhase, spawnWords, animateWords]); // spawnWords and animateWords are memoized

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
        className="absolute bottom-1 left-2 z-30 flex items-center gap-2 text-white font-mono text-sm hover:underline cursor-pointer"
        aria-label="Back to chat view"
        tabIndex={0}
      >
        <ArrowLeft size={18} />
        <span>Back to chat</span>
      </button>

      {/* Instruction Text */}
      <div
        className="absolute top-4 left-1/2 transform -translate-x-1/2 z-30 text-white font-mono px-4 py-2"
        aria-live="polite"
      >
        {phaseInstructions[currentPhase]}
      </div>

      {/* Flying Words Area */}
      <div
        className="absolute left-0 right-0 w-full z-10"
        style={{
          top: `${flyingWordsTopOffset}px`,
          height: `calc(100% - ${
            flyingWordsTopOffset + flyingWordsBottomOffset
          }px)`,
        }}
      >
        {flyingWords.map((word) => (
          <div
            key={word.id}
            className="absolute bg-[#333333] text-white font-mono text-sm px-4 py-2 rounded-[24px] border border-[#444444] cursor-pointer hover:scale-105 transition-all duration-150 hover:[background:linear-gradient(to_right,#b9e55a,#1fbc4e)] hover:text-black hover:border-transparent"
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
            className="p-2 rounded-[12px] text-[white] hover:shadow-[0_0_16px_#B9E55A] hover:scale-[1.02] transition-colors duration-200 cursor-pointer"
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
