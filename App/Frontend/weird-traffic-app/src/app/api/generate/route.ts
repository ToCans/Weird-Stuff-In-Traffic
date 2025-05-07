import { NextResponse } from "next/server";
import path from "path";
import fs from "fs/promises";

// Helper function to convert image to base64
async function imageToBase64(filePath: string): Promise<string | null> {
  try {
    const fullPath = path.join(process.cwd(), "public", filePath);
    const imageBuffer = await fs.readFile(fullPath);
    const base64String = imageBuffer.toString("base64");
    // Determine image type from file extension
    const ext = path.extname(filePath).slice(1);
    const mimeType = `image/${ext === "jpg" ? "jpeg" : ext}`; // Basic type mapping
    return `data:${mimeType};base64,${base64String}`;
  } catch (error) {
    console.error(`Error reading or converting image ${filePath}:`, error);
    return null; // Return null if file reading fails
  }
}

// Helper function to introduce delay
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export async function POST(request: Request) {
  try {
    // Although we receive the prompt, we don't use it for simulation
    // const { prompt } = await request.json();
    // console.log("Received prompt for generation:", prompt);

    console.log("Simulating generation delay..."); // Log delay start
    await delay(7000); // Add 7 seconds delay
    console.log("Generation delay finished."); // Log delay end

    const placeholderImagePaths = [
      "placeholder_1.png",
      "placeholder_2.png",
      "placeholder_3.png",
      "placeholder_4.png",
    ];

    const base64Images = await Promise.all(
      placeholderImagePaths.map(imageToBase64)
    );

    // Filter out any null results in case of errors
    const validBase64Images = base64Images.filter(
      (img): img is string => img !== null
    );

    if (validBase64Images.length < placeholderImagePaths.length) {
      // Handle case where some images couldn't be processed
      console.warn("Could not process all placeholder images.");
      // Decide response: return partial data or error
    }

    // Return the base64 image data URIs
    return NextResponse.json({ images: validBase64Images });
  } catch (error) {
    console.error("Error in generate API:", error);
    return NextResponse.json(
      { message: "Internal Server Error" },
      { status: 500 }
    );
  }
}
