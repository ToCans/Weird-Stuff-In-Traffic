"use client";

// Type for the structured result message
export type DetectionResultPayload = {
  type: "detectionResult"; // Add a type identifier
  baseMessageInitial: string;
  baseMessageExpanded: string;
  score: number;
  points: number;
};

// Dialog message types - Allow 'expanded' to hold the structured payload
export type DialogSequence = {
  initial: string;
  expanded: string | DetectionResultPayload; // Allow string or the payload
};

// Dialog categories
export const DialogMessages = {
  welcome: {
    initial: "Hellooo! Got a weird idea?\nHit me with your wildest prompt!",
    expanded:
      "Hellooo! Got a weird idea?\nHit me with your wildest prompt!\n\nNeed ideas? Just click one of those chips in the textfield – they're mini-games to spark your genius!",
  },
  loading: {
    initial:
      "Thanks for your prompt — you're helping make the roads a little safer, one idea at a time.\nJust a sec while we cook up some weirdness...",
    expanded:
      "Thanks for your prompt — you're helping make the roads a little safer, one idea at a time.\nJust a sec while we cook up some weirdness...",
  },
  completed: {
    initial:
      "Nice!\n\nPick the image that best matches your prompt — or regenerate if you want something different.",
    expanded:
      "Nice!\n\nPick the image that best matches your prompt — or regenerate if you want something different.",
  },

  // New section: Message to show when image is selected
  imageSelected: {
    initial: "Interesting choice!",
    expanded: `Sending it to the other model... though I wouldn't get my hopes up. I'm still the sharpest mind in the room.`,
  },

  slotMachineWelcome: {
    initial: "Welcome to Slot Machine!",
    expanded:
      "Welcome to Slot Machine!\n\nJust hit Spin and let the crazy prompts roll, or click a word to add it!",
  },

  // New section: Clap Words Welcome Message
  clapWordsWelcome: {
    initial: "Welcome to clap words!",
    expanded:
      "Welcome to clap words!\n\nClick on the words, and watch the weird prompts come to life!",
  },

  // New section: Fill in the Blank Welcome Message
  fillBlankWelcome: {
    initial: "Welcome to fill in the blank!",
    expanded:
      "Welcome to fill in the blank!\n\nTime to get creative – just fill in the blanks and watch the madness unfold!",
  },

  // For error state
  error: {
    initial:
      "Hmm, something didn't work right.\nWant to try again with a different prompt?",
    expanded:
      "Hmm, something didn't work right.\nWant to try again with a different prompt?\n\nSometimes being a bit more specific helps!",
  },
};
// Function to dynamically create the detection result message OBJECT
export const updateDialogMessages = {
  detectionResult: (score: number, points: number): DialogSequence => ({
    initial: "Analysis Complete!", // Initial part remains simple
    expanded: {
      // Return the structured object
      type: "detectionResult",
      baseMessageInitial: `Based on my analysis, the similarity score is...`, // Short initial part for animation if needed
      baseMessageExpanded: `Based on my analysis, the similarity score between your prompt and the selected image is `, // Base message for animation
      score: score,
      points: points,
    },
  }),
};
