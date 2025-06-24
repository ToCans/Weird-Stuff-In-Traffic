# Weird Stuff In Traffic - Backend

This directory contains the necessary backend code for running the generation and detection processes, and interacting with the user interface.

## 📁 Backend Structure

-   **`images/`** - The images directory for storing background images used during generation and storing images where detection failed.
-   **`models/`** - Used for storing the detection model weights and the configuration file.

### API Integration and User Interaction Flow

The frontend interacted with backend services via RESTful API endpoints exposed through Next.js API routes. Two primary endpoints were utilized: `/api/generate` for synthetic image generation and `/api/detect` for anomaly detection based on user input.

The `/api/generate` route accepted a user-provided textual prompt and returned an array of Base64 encoded images:

```typescript
// POST /api/generate

// Request body
const requestBody = {
	prompt: 'textual prompt provided by the user',
};

// Type for a single generated image
export interface GeneratedImage {
	prompt: string;
	imageBase64: string;
}

// Response containing multiple generated images
export interface GeneratedImages {
	images: GeneratedImage[];
}
```

After image selection, the `/api/detect` endpoint was called with both the original prompt and the selected image. The response included a similarity score and a processed image, also Base64 encoded:

```typescript
// POST /api/detect

// Request body
const requestBody = {
	prompt: 'Associated textual prompt',
	imageBase64: '...', // selectedImage
};

// Response type
export interface DetectApiResponse {
	prompt: string; // The prompt used for detection
	score: number;
	imageBase64: string; // detectedImage
}
```

## Learn More

To learn more about Next.js, take a look at the following resources:

-   [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
-   [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
