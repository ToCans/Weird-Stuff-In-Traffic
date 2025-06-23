"use client";

import Link from "next/link";
import { useState } from "react";
import { usePathname } from "next/navigation";
import type { ActiveView } from "@/app/types/chat";
import { IconButton } from "../ui/IconButton";
import { InfoModal } from "../modals/InfoModal";
import { useGameStore, useUIStore } from "@/app/stores";

// import { InfoModal } from "@/app/conponents/ui/InfoModal";

export function Header() {
  const { earnedPoints, trainingProgress, handleSwitchView } = useGameStore();
  const { isInfoModalOpen, toggleInfoModal } = useUIStore();

  const pathname = usePathname(); // Get current path
  const isChatPage = pathname === "/chat"; // Check if it's the chat page

  // Ensure progress is between 0 and 100 for the progress bar
  const clampedProgress = Math.max(0, Math.min(100, trainingProgress || 0));

  // Define the icon for the IconButton
  const infoIcon = (
    <span className="text-white text-xl font-regular font-mono">i</span>
  );

  return (
    <>
      <header className="fixed top-0 left-0 w-full p-10 z-50">
        <div className="container mx-auto">
          <div
            className={`flex items-center justify-between ${
              isChatPage ? "border-b-2 border-[#383838]" : ""
            }`}
          >
            <Link href="/" className="flex items-center gap-2 mb-3">
              <img src="/logo.png" alt="Weird Traffic Logo" />
            </Link>

            {isChatPage && (
              <div
                className="flex items-center gap-6"
                id="score-display-container"
              >
                {/* Earned Points Counter */}
                <div className="text-white font-mono flex items-center gap-2">
                  {/* Hide label on mobile */}
                  <span className="hidden md:inline">Points:</span>
                  <span className="text-gradient-weird font-bold text-[32px]">
                    {Math.round(earnedPoints)}{" "}
                    {/* Display rounded earned points */}
                  </span>
                </div>

                {/* Model Training Progress Bar */}
                <div className="text-white font-mono flex items-center gap-2">
                  {/* Hide label on mobile */}
                  <span className="hidden md:inline">Model Training:</span>
                  <div className="w-32 h-4 bg-[#383838] rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-[#B9E55A] to-[#1FBC4E] rounded-full transition-all duration-300 ease-in-out"
                      style={{ width: `${clampedProgress}%` }} // Dynamic width based on progress
                      role="progressbar"
                      aria-valuenow={clampedProgress}
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-label="Model Training Progress"
                    ></div>
                  </div>
                  <span className="text-sm w-10 text-right">
                    {clampedProgress.toFixed(0)}%
                  </span>{" "}
                  {/* Optional percentage display */}
                </div>
              </div>
            )}
            {/* Replace the div with IconButton component */}
            <IconButton
              id="game-header-info-button"
              icon={infoIcon}
              onClick={toggleInfoModal}
              ariaLabel="Game Info"
              className="w-12 h-12"
              variant="secondary"
            />
          </div>
        </div>
      </header>
      {isInfoModalOpen && (
        <InfoModal isOpen={isInfoModalOpen} onClose={toggleInfoModal} />
      )}
    </>
  );
}
