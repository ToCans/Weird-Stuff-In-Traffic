"use client";

import Joyride, { Step, CallBackProps } from "react-joyride";
import { useState, useEffect } from "react";

const TutorialTour: React.FC = () => {
  const [runTour, setRunTour] = useState(false);

  useEffect(() => {
    // Start the tour
    setRunTour(true);

    // Disable body scroll when tour starts
    document.body.style.overflow = "hidden";
    document.body.style.position = "relative";

    // Re-enable body scroll when component unmounts (e.g., navigation)
    return () => {
      document.body.style.overflow = "";
      document.body.style.position = "";
    };
  }, []);

  const tourSteps: Step[] = [
    {
      target: "#game-header-info-button",
      content: (
        <div className="text-sm font-mono max-w-xs text-light">
          <ul className="list-disc list-inside space-y-1">
            <li>Scoring: Point systems and bonuses.</li>
            <li>Tips: Prompt creation advice.</li>
            <li>Our Goal: Purpose behind the game.</li>
            <li>Instructions: How to play.</li>
          </ul>
        </div>
      ),
      placement: "bottom-end",
      title: "Access Game Details",
      spotlightPadding: 5,
      disableBeacon: true,
    },
    {
      target: "#score-display-container",
      content: (
        <div className="text-sm font-mono text-light">
          Displays your current score and model training progress. The more
          creative and unpredictable your prompts, the higher your score. The
          percentage shows how well the model is learning from the collected
          data.
        </div>
      ),
      placement: "bottom",
      title: "Scoring System",
      spotlightPadding: 5,
      disableBeacon: true,
    },
    {
      target: "#avatar-dialog-container",
      content: (
        <div className="text-sm font-mono text-light">
          Your digital co-pilot. It provides hints, comments, and feedback as
          you play.
        </div>
      ),
      placement: "right-start",
      title: "Avatar Chat Bubble",
      spotlightPadding: 10,
      disableBeacon: true,
    },
    {
      target: "#inspiration-options-container",
      content: (
        <div className="text-sm font-mono text-light">
          <ul className="list-disc list-inside space-y-1">
            <li>Slot Machine: Get three random words to spark ideas.</li>
            <li>Clap Words: Tap floating words to build prompts.</li>
            <li>
              Fill in the Blank: Complete sentences for unpredictable results.
            </li>
          </ul>
        </div>
      ),
      placement: "top-start",
      title: "Inspiration Options",
      spotlightPadding: 5,
      disableBeacon: true,
    },
    {
      target: "#creative-prompt-input",
      content: (
        <div className="text-sm font-mono text-light">
          Enter your own prompts to confuse the AI. Be as creative as possible!
        </div>
      ),
      placement: "top-end",
      title: "Creative Prompt Input",
      spotlightPadding: 5,
      disableBeacon: true,
    },
  ];

  const handleJoyrideCallback = (data: CallBackProps) => {
    const { status, lifecycle } = data;
    const finishedStatuses: string[] = ["finished", "skipped"];

    if (finishedStatuses.includes(status)) {
      setRunTour(false);
      // Re-enable body scroll when tour finishes or is skipped
      document.body.style.overflow = "";
      document.body.style.position = "";
    }

    // Handle beacon click if needed - sometimes interaction with overlay can be tricky
    // if (lifecycle === 'beacon' && type === 'beacon:click') {
    //   // custom logic
    // }
  };

  if (!runTour) {
    return null; // Don't render Joyride if the tour is not supposed to run
  }

  return (
    <Joyride
      steps={tourSteps}
      run={runTour}
      continuous
      showProgress
      showSkipButton
      scrollToFirstStep
      disableOverlayClose={false}
      callback={handleJoyrideCallback}
      floaterProps={{
        disableAnimation: true,
        hideArrow: true, // hide arrow
      }}
      styles={{
        options: {
          backgroundColor: "var(--dark-gray)",
          overlayColor: "rgba(0, 0, 0, 0.7)",
          primaryColor: "var(--weird-green)",
          textColor: "#FFFFFF",
          zIndex: 10000,
        },
        tooltip: {
          borderRadius: "1.5rem",
          padding: "1rem",
          border: "2px solid transparent",
          backgroundImage:
            "linear-gradient(var(--dark-gray), var(--dark-gray)), linear-gradient(to right, #B9E55A, #1FBC4E)",
          backgroundOrigin: "border-box",
          backgroundClip: "padding-box, border-box",
        },
        tooltipContainer: {
          textAlign: "left",
        },
        tooltipTitle: {
          margin: 0,
          paddingBottom: "0.5rem",
          color: "#FFFFFF",
          fontSize: "1rem",
          fontWeight: "bold",
        },
        spotlight: {
          borderRadius: "inherit",
        },
      }}
    />
  );
};

export default TutorialTour;
