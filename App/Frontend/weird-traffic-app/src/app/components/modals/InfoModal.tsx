import React, { useState, KeyboardEvent, MouseEvent } from "react";
import { X } from "lucide-react";
import { Button } from "../ui/Button";
import { IconButton } from "../ui/IconButton";

interface InfoModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type TabId = "scoring" | "tips" | "goal" | "about";

interface Tab {
  id: TabId;
  label: string;
}

const tabs: Tab[] = [
  { id: "scoring", label: "Scoring" },
  { id: "tips", label: "Tips" },
  { id: "goal", label: "Our Goal" },
  { id: "about", label: "About Us" },
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
        className="relative bg-[var(--dark-gray)] text-white rounded-2xl shadow-lg p-10 w-full max-w-[700px] font-mono"
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
            <div>
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
            <p className="text-sm">Here are some useful tips...</p> // Yer tutucu
          )}
          {activeTab === "goal" && (
            <p className="text-sm">Our goal is to...</p> // Yer tutucu
          )}
          {activeTab === "about" && (
            <p className="text-sm">Learn more about us...</p> // Yer tutucu
          )}
        </div>
      </div>
    </div>
  );
};

// Make sure to install lucide-react if you haven't: npm install lucide-react or yarn add lucide-react
