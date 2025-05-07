// src/types/chat.ts
// Define view types
export type ActiveView = "chat" | "slotmachine" | "clapwords" | "fillblank";

// Let's define message types
export type Message = {
  id: number;
  type: "user" | "assistant" | "image_grid"; // Include image_grid type
  content: string | string[]; // Content can be string or array of strings (for image URLs)
  isLoading?: boolean; // Optional loading state, primarily for image_grid
  selectedImageIndex?: number | null; // Optional: Index of the image selected by the user
  isDetecting?: boolean; // Optional: Indicator for detection loading
  detectedImageUrl?: string; // Optional: Base64 of the image returned by detection API
};

// Add any other types specific to the chat feature here in the future
