"use client";

import Image from "next/image";
import { Dialog } from "@/app/components/ui/Dialog";
import { Header } from "@/app/components/game/Header";
import { motion } from "framer-motion";
import { TypeAnimation } from "react-type-animation";
import { useRef, useEffect, useMemo, useState, useCallback } from "react";
import { PromptInput } from "@/app/components/ui/Input";
import { ImageDisplay } from "@/app/components/game/ImageDisplay";
import { DetectionResultPayload } from "@/app/constants/DialogMessages";
import { MessageActions } from "@/app/components/game/MessageActions";
import { SlotmachineGame } from "@/app/components/game/SlotMachine";
import { ClapwordsGame } from "@/app/components/game/ClapwordsGame";
import { useGameStore, useUIStore } from "@/app/stores";
import { Modal } from "@/app/components/modals/ShareModal_1";
import { ShareModal2 } from "@/app/components/modals/ShareModal_2";
import dynamic from "next/dynamic";
import CarAnimation from "@/app/components/game/CarAnimation";

// Dynamically import TutorialTour with SSR disabled
const TutorialTour = dynamic(
  () => import("@/app/components/game/TutorialTour"),
  { ssr: false }
);

export default function ChatPage() {
  const {
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
    handleSwitchView,
    finalizeScoreUpdate,
    handleTypeAnimationComplete,
    resetDetectionCount,
    setSignalModalOpen,
    handleCopyMessage,
    handleEditMessage,
  } = useGameStore();

  const {
    isShareModalOpen,
    isShareModal2Open,
    sharedImageUrlForModal2,
    runTour,
    toggleShareModal,
    toggleShareModal2,
    initializeTutorial,
  } = useUIStore();

  const chatContainerRef = useRef<HTMLDivElement>(null);
  const modalTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize tutorial on component mount
  useEffect(() => {
    initializeTutorial();
  }, [initializeTutorial]);

  useEffect(() => {
    if (modalTimeoutRef.current) {
      clearTimeout(modalTimeoutRef.current);
      modalTimeoutRef.current = null;
    }

    if (signalModalOpen) {
      modalTimeoutRef.current = setTimeout(() => {
        toggleShareModal();
        modalTimeoutRef.current = null;
      }, 2000);
    }

    return () => {
      if (modalTimeoutRef.current) {
        clearTimeout(modalTimeoutRef.current);

        modalTimeoutRef.current = null;
      }
    };
  }, [signalModalOpen, toggleShareModal]);

  const animationSequence = useMemo(() => {
    const sequenceItems: (string | number | (() => void))[] = [];
    const defaultDelay = 1000;

    sequenceItems.push(dialogSequence.initial);

    if (
      typeof dialogSequence.expanded === "object" &&
      dialogSequence.expanded?.type === "detectionResult"
    ) {
      const result = dialogSequence.expanded as DetectionResultPayload;
      sequenceItems.push(defaultDelay);
      const scoreMessage = `${result.baseMessageExpanded}${result.score.toFixed(
        0
      )}%\nYou've earned ${result.points} points!`;
      sequenceItems.push(scoreMessage);
      sequenceItems.push(() => {
        finalizeScoreUpdate(result.points, result.score, detectionCount);
      });
    } else if (typeof dialogSequence.expanded === "string") {
      if (dialogSequence.expanded !== dialogSequence.initial) {
        sequenceItems.push(defaultDelay);
        sequenceItems.push(dialogSequence.expanded);
      }
    }
    if (
      !(
        typeof dialogSequence.expanded === "object" &&
        dialogSequence.expanded?.type === "detectionResult"
      )
    ) {
      sequenceItems.push(() => {
        if (handleTypeAnimationComplete) {
          handleTypeAnimationComplete();
        }
      });
    }
    return sequenceItems;
  }, [
    dialogSequence,
    finalizeScoreUpdate,
    detectionCount,
    handleTypeAnimationComplete,
  ]);

  useEffect(() => {
    if (activeView === "chat" && chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages, activeView]);

  const handleCloseShareModal = () => {
    toggleShareModal();
    resetDetectionCount();
  };

  const handleOpenShareModal2 = useCallback(
    (imageUrl: string) => {
      toggleShareModal2(imageUrl);
    },
    [toggleShareModal2]
  );

  const handleCloseShareModal2 = useCallback(() => {
    toggleShareModal2();
  }, [toggleShareModal2]);

  return (
    <div className="h-screen w-screen flex flex-col bg-[#1f1f1f] overflow-hidden">
      <div style={{ height: "5rem" }}>
        <Header />
      </div>
      {/* Main content area - Grid layout - Responsive */}
      <div className="flex flex-col md:flex-row flex-1 overflow-y-auto md:overflow-hidden">
        {/* 3 column grid */}
        {/* Column 1: Dialog and Car */}
        <div className="w-full md:w-1/3 flex flex-col justify-between p-4 md:p-6 md:ml-10 md:mt-10 order-2 md:order-1 overflow-y-auto custom-scrollbar">
          {/* Dialog */}
          <div
            className="max-w-xs mx-auto md:mx-0 animate-slide-up-fade-in z-10 relative"
            id="avatar-dialog-container"
          >
            <Dialog>
              {typeof dialogSequence.expanded === "object" &&
              dialogSequence.expanded.type === "detectionResult" ? (
                <TypeAnimation
                  sequence={[
                    dialogSequence.expanded.baseMessageInitial,
                    1000,
                    dialogSequence.expanded.baseMessageExpanded,
                    () => {
                      if (handleTypeAnimationComplete) {
                        handleTypeAnimationComplete();
                      }
                      const detectionResult =
                        dialogSequence.expanded as DetectionResultPayload;
                      finalizeScoreUpdate(
                        detectionResult.points,
                        detectionResult.score,
                        detectionCount
                      );
                    },
                  ]}
                  wrapper="span"
                  speed={60}
                  style={{ whiteSpace: "pre-line", display: "inline-block" }}
                  repeat={0}
                  cursor={true}
                  key={JSON.stringify(dialogSequence) + "-detection"}
                />
              ) : (
                <TypeAnimation
                  sequence={animationSequence}
                  wrapper="span"
                  speed={60}
                  style={{ whiteSpace: "pre-line", display: "inline-block" }}
                  repeat={0}
                  cursor={true}
                  key={JSON.stringify(dialogSequence) + "-normal"}
                />
              )}
            </Dialog>
          </div>
          {/* Car Animation */}
          <CarAnimation animationState={carAnimationState} />
        </div>
        {/* Column 2 & 3: Chat Area and Prompt Input */}
        <div className="w-full md:w-2/3 flex flex-col justify-between p-4 md:p-6 md:mr-10 md:mt-3 order-1 md:order-2">
          {/* Content Area: Conditionally render Chat or Game */}
          <div
            ref={chatContainerRef}
            className={`flex-1 relative z-0 space-y-6 custom-scrollbar p-4 ${
              activeView !== "chat" || messages.length === 0
                ? "flex flex-col justify-center items-center"
                : ""
            } ${
              activeView === "chat" ? "md:overflow-y-auto" : "overflow-hidden"
            }`}
            style={{ minHeight: "300px" }}
          >
            {/* Render Chat View */}
            {activeView === "chat" && (
              <>
                {messages.length === 0 ? (
                  <div className="text-transparent bg-weird-gradient bg-clip-text font-mono text-2xl text-center animate-slide-up-fade-in">
                    Welcome beginner
                  </div>
                ) : (
                  messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`relative flex w-full ${
                        msg.type === "user" ? "justify-end" : "justify-start"
                      }`}
                    >
                      {/* User Messages */}
                      {msg.type === "user" && (
                        <div
                          className={`group p-3 rounded-4xl max-w-[80%] sm:max-w-[70%] bg-[var(--dark-gray)] text-white relative`}
                        >
                          <p
                            style={{ whiteSpace: "pre-wrap" }}
                            className="break-words"
                          >
                            {msg.content as string}
                          </p>
                          {prompt !== msg.content && (
                            <MessageActions
                              messageContent={msg.content as string}
                              onCopy={() =>
                                handleCopyMessage(msg.content as string)
                              }
                              onEdit={() => handleEditMessage(msg.id)}
                            />
                          )}
                        </div>
                      )}

                      {/* Image Grid Messages */}
                      {msg.type === "image_grid" &&
                        Array.isArray(msg.content) && (
                          <div className="w-full max-w-full sm:max-w-[calc(70%+2rem)] mb-5">
                            <ImageDisplay
                              imageUrls={msg.content as string[]}
                              isLoading={msg.isLoading}
                              altTextPrefix={`Images for prompt`}
                              onImageSelect={(selectedImageBase64, index) =>
                                handleImageSelect(
                                  msg.id,
                                  selectedImageBase64,
                                  index
                                )
                              }
                              isDetecting={msg.isDetecting}
                              selectedImageIndex={msg.selectedImageIndex}
                              onShare={handleOpenShareModal2}
                              detectedImageUrl={msg.detectedImageUrl}
                            />
                          </div>
                        )}
                    </div>
                  ))
                )}
              </>
            )}

            {/* Render Slot Machine Game View */}
            {activeView === "slotmachine" && (
              <SlotmachineGame
                prompt={prompt}
                setPrompt={setPrompt}
                setActiveView={handleSwitchView}
              />
            )}

            {/* Render Clap Words Game View */}
            {activeView === "clapwords" && (
              <ClapwordsGame
                setPrompt={setPrompt}
                setActiveView={handleSwitchView}
              />
            )}

            {/* Placeholder for other games */}
            {/* {activeView === 'fillblank' && <FillblankGame ... />} */}
          </div>

          <motion.div
            className="w-full mt-auto"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          >
            <PromptInput
              prompt={prompt}
              setPrompt={setPrompt}
              onGenerate={handleGenerate}
              isLoading={isLoadingGeneration}
              disabled={isLoadingGeneration}
              setActiveView={handleSwitchView}
              activeView={activeView}
            />
          </motion.div>
        </div>
      </div>
      {/* Only render TutorialTour if runTour is true */}
      {runTour && <TutorialTour />}
      <Modal
        isOpen={isShareModalOpen}
        onClose={handleCloseShareModal}
        content={
          <div className="flex flex-col items-left text-left gap-6">
            <h3 className="text-xl text-white font-mono">
              Do you want to share your picture?
            </h3>
            <p className="text-sm font-mono text-white">
              If so, click the share icon on the image you want to share.
            </p>
          </div>
        }
      ></Modal>
      {/* Render ShareModal2 */}
      <ShareModal2
        isOpen={isShareModal2Open}
        onClose={handleCloseShareModal2}
        imageUrl={sharedImageUrlForModal2}
        accuracy={
          messages.find(
            (msg) => msg.detectedImageUrl === sharedImageUrlForModal2
          )?.lastDetectionAccuracy ?? null
        }
        pointsReceived={
          messages.find(
            (msg) => msg.detectedImageUrl === sharedImageUrlForModal2
          )?.lastDetectionPoints ?? null
        }
        totalScore={earnedPoints}
      />
    </div>
  );
}
