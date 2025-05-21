import React, { useState, KeyboardEvent, MouseEvent } from "react";
import { X } from "lucide-react";
import { Button } from "../ui/Button";
import { IconButton } from "../ui/IconButton";

interface InfoModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type TabId = "scoring" | "tips" | "goal" | "instructions";

interface Tab {
  id: TabId;
  label: string;
}

const tabs: Tab[] = [
  { id: "scoring", label: "Scoring" },
  { id: "tips", label: "Tips" },
  { id: "goal", label: "Our Goal" },
  { id: "instructions", label: "Game Instructions" },
];

const scoringData = [
  { recognized: "10%", points: 9 },
  { recognized: "20%", points: 8 },
  { recognized: "30%", points: 7 },
  { recognized: "40%", points: 6 },
  { recognized: "50%", points: 5 },
  { recognized: "60%", points: 4 },
  { recognized: "70%", points: 3 },
  { recognized: "80%", points: 2 },
  { recognized: "90%", points: 1 },
  { recognized: "100%", points: 0 },
];

export const InfoModal: React.FC<InfoModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<TabId>("scoring");

  const handleClose = () => {
    onClose();
  };

  const handleModalContentClick = (event: MouseEvent<HTMLDivElement>) => {
    event.stopPropagation();
  };

  const handleOuterKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Escape") {
      handleClose();
    }
  };

  const handleTabClick = (tabId: TabId) => {
    setActiveTab(tabId);
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 bg-black bg-black/60 backdrop-blur-sm p-4 flex items-center justify-center z-50 "
      onClick={handleClose}
      onKeyDown={handleOuterKeyDown}
      role="dialog"
      aria-modal="true"
      aria-labelledby="info-modal-title"
      tabIndex={-1}
    >
      <div
        className="relative bg-[var(--dark-gray)] text-white rounded-2xl shadow-lg p-10 w-full max-w-[800px] font-mono"
        onClick={handleModalContentClick}
        role="document"
      >
        <h2 id="info-modal-title" className="text-xl font-medium mb-4">
          Information
        </h2>

        {/* Close Button using IconButton */}
        <IconButton
          icon={<X size={20} />}
          onClick={handleClose}
          ariaLabel="Close information modal"
          className="absolute top-10 right-10 w-[42px] h-[42px]"
          tabIndex={0}
        />

        {/* Tab Buttons */}
        <div className="flex space-x-3 mb-6">
          {tabs.map((tab) => (
            <Button
              key={tab.id}
              variant={activeTab === tab.id ? "active" : "secondary"}
              size="sm"
              onClick={() => handleTabClick(tab.id)}
              aria-pressed={activeTab === tab.id}
              aria-label={`Select ${tab.label} tab`}
              tabIndex={0}
            >
              {tab.label}
            </Button>
          ))}
        </div>

        {/* Content Area */}
        <div className="mt-4">
          {activeTab === "scoring" && (
            <div className="h-[400px] w-full overflow-y-auto custom-scrollbar">
              <div className="flex justify-between text-sm text-foreground mb-2 px-2">
                <span>Recognized</span>
                <span>Points</span>
              </div>
              <ul className="flex flex-col">
                {scoringData.map((item, index) => (
                  <React.Fragment key={index}>
                    {index > 0 && (
                      <div className="h-px bg-weird-gradient mx-2" />
                    )}
                    <li className="flex justify-between py-2 px-2 text-sm">
                      <span>{item.recognized}</span>
                      <span>{item.points}</span>
                    </li>
                  </React.Fragment>
                ))}
              </ul>
            </div>
          )}
          {activeTab === "tips" && (
            <div className="h-[400px] w-full overflow-y-auto custom-scrollbar p-2 text-sm text-light">
              <p>Tips for creating creative and unique prompts.</p>
            </div>
          )}
          {activeTab === "goal" && (
            <div className="h-[400px] w-full overflow-y-auto custom-scrollbar p-2 space-y-4 text-sm text-light">
              <p>
                The goal of Weird Stuff in Traffic is to generate as many
                creative and unexpected prompts as possible to train a detection
                AI for autonomous driving. By challenging the AI with unusual
                and complex traffic scenarios, we aim to improve its ability to
                handle real-world situations, making autonomous vehicles safer
                and more reliable.
              </p>
              <p>
                Every prompt you create helps expose potential blind spots in
                the AI's understanding of the road, contributing to a smarter
                and more adaptive driving system. So, get creative and push the
                boundaries of what the AI can understand!
              </p>
            </div>
          )}
          {activeTab === "instructions" && (
            <div className="h-[400px] w-full overflow-y-auto custom-scrollbar p-2 space-y-6 text-sm text-light">
              <div className="rounded-2xl p-[2px] bg-weird-gradient">
                <div className="bg-[var(--gray)] rounded-2xl p-3 space-y-1">
                  <div className="font-bold">Goal</div>
                  <div>
                    Confuse the AI by creating traffic scenarios it struggles to
                    interpret. Earn points for creative prompts and unlock
                    upgrades as you progress.
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div className="font-bold text-base">How to Play:</div>

                <div className="space-y-2">
                  <div className="font-bold">1. Enter a Prompt:</div>
                  <ul className="list-disc pl-6 space-y-2">
                    <li>
                      Use the input field to type your own creative ideas.
                    </li>
                    <li>
                      The goal is to challenge the AI with unusual and
                      unpredictable scenarios.
                    </li>
                  </ul>
                </div>

                <div className="space-y-2">
                  <div className="font-bold">2. Get Inspiration:</div>
                  <ul className="list-disc pl-6 space-y-2">
                    <li>Slot Machine: Spin for three random words.</li>
                    <li>
                      Flying Words: Tap on floating words to build a prompt.
                    </li>
                    <li>
                      Fill in the Blank: Complete sentences for unpredictable
                      results.
                    </li>
                  </ul>
                </div>

                <div className="space-y-2">
                  <div className="font-bold">3. Submit and Score:</div>
                  <ul className="list-disc pl-6 space-y-2">
                    <li>Click Submit to see how the AI reacts.</li>
                    <li>
                      You earn points based on how effectively your prompt
                      confuses the AI.
                    </li>
                    <li>Use the feedback to improve your strategies.</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
