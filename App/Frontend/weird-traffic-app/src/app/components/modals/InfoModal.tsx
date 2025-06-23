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
      className="fixed inset-0 bg-black/70 p-4 flex items-center justify-center z-50 animate-slide-up-fade-in"
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
            <div className="h-[410px] w-full overflow-y-auto custom-scrollbar">
              <div className="flex justify-between text-sm text-[white] mb-2 px-2">
                <span>Recognized</span>
                <span>Points</span>
              </div>
              <ul className="flex flex-col">
                {scoringData.map((item, index) => (
                  <li key={item.recognized}>
                    {index > 0 && (
                      <div className="h-[2px] bg-weird-gradient mx-2" />
                    )}
                    <div className="flex justify-between py-2 px-2 text-sm">
                      <span>{item.recognized}</span>
                      <span>{item.points}</span>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {activeTab === "tips" && (
            <div className="h-[410px] w-full overflow-y-auto custom-scrollbar p-2 space-y-4 text-sm text-light">
              <div className="rounded-2xl p-[2px] bg-weird-gradient">
                <div className="bg-[var(--gray)] rounded-2xl p-3">
                  <div className="font-bold mb-2">Tip</div>
                  <div>
                    The more unusual and unexpected your scenario, the higher
                    your chances of confusing the AI and earning maximum points!
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <div className="font-bold text-base mb-2">
                    Effective Strategies:
                  </div>
                  <ul className="list-disc pl-6 space-y-2">
                    <li>
                      <strong>Combine unexpected elements:</strong> "A giraffe
                      driving a motorcycle in heavy rain"
                    </li>
                    <li>
                      <strong>Add weather chaos:</strong> "Snow tornado with
                      flying umbrellas blocking traffic"
                    </li>
                    <li>
                      <strong>Mix scales:</strong> "Giant ants carrying tiny
                      cars across the street"
                    </li>
                    <li>
                      <strong>Time paradoxes:</strong> "Medieval knights riding
                      horses next to cars"
                    </li>
                  </ul>
                </div>

                <div>
                  <div className="font-bold text-base mb-2">
                    What NOT to Include:
                  </div>
                  <ul className="list-disc pl-6 space-y-2">
                    <li>Violence, gore, or harmful content</li>
                    <li>Inappropriate or offensive material</li>
                    <li>Personal information or real names</li>
                    <li>Copyright-protected characters or brands</li>
                  </ul>
                </div>

                <div>
                  <div className="font-bold text-base mb-2">
                    Prompt Structure Tips:
                  </div>
                  <ul className="list-disc pl-6 space-y-2">
                    <li>
                      <strong>Start with a base:</strong> "Busy intersection
                      with..."
                    </li>
                    <li>
                      <strong>Add the weird element:</strong> "...dancing
                      elephants..."
                    </li>
                    <li>
                      <strong>Include context:</strong> "...during a
                      thunderstorm at night"
                    </li>
                    <li>
                      <strong>Be specific:</strong> Use colors, sizes, emotions,
                      and details
                    </li>
                  </ul>
                </div>

                <div className="bg-[var(--gray)] rounded-xl p-3">
                  <div className="font-bold mb-2">
                    🏆 Example High-Scoring Prompts:
                  </div>
                  <ul className="text-xs space-y-1">
                    <li>
                      "Purple kangaroos bouncing between cars while it's raining
                      jellybeans"
                    </li>
                    <li>
                      "Traffic jam with cars made of ice cream melting in desert
                      heat"
                    </li>
                    <li>
                      "Intersection where gravity works sideways and cars drive
                      on walls"
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          )}
          {activeTab === "goal" && (
            <div className="h-[410px] w-full overflow-y-auto custom-scrollbar p-2 space-y-4 text-sm text-light">
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
            <div className="h-[410px] w-full overflow-y-auto custom-scrollbar p-2 space-y-6 text-sm text-light">
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
