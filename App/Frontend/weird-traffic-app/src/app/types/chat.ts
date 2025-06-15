// src/types/chat.ts
// Define view types
export type ActiveView = "chat" | "slotmachine" | "clapwords" | "fillblank";

// Let's define message types
export interface Message {
  id: number;
  type: "user" | "assistant" | "image_grid" | "loading" | "error"; // Include image_grid type and new types
  content: string | string[]; // Content can be string or array of strings (for image URLs)
  isLoading?: boolean; // Loading state, primarily for image_grid
  selectedImageIndex?: number | null; // Index of the image selected by the user
  isDetecting?: boolean; // Indicator for detection loading
  detectedImageUrl?: string | null; //Base64 of the image returned by detection API
  lastDetectionAccuracy?: number | null;
  lastDetectionPoints?: number | null;
}

export interface DetectApiResponse {
  prompt: string; // The prompt used for detection
  score: number;
  imageBase64: string; // Add the detected image base64
}

// Add any other types specific to the chat feature here in the future
// Single generated image
export interface GeneratedImage {
  prompt: string;
  imageBase64: string;
}

// Response containing multiple generated images
export interface GeneratedImages {
  images: GeneratedImage[];
}
