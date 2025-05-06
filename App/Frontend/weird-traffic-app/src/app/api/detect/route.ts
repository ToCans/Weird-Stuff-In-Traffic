import { NextResponse } from "next/server";

// Helper function to introduce delay
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export async function POST(request: Request) {
  try {
    const { prompt, imageBase64 } = await request.json();

    // Basic validation
    if (!prompt || !imageBase64) {
      return NextResponse.json(
        { message: "Missing prompt or imageBase64" },
        { status: 400 }
      );
    }

    console.log("Received prompt for detection:", prompt);
    // console.log("Received imageBase64 for detection:", imageBase64.substring(0, 50) + "..."); // Log truncated base64

    console.log("Simulating detection delay..."); // Log delay start
    await delay(7000); // Add delay for the detection
    console.log("Detection delay finished."); // Log delay end

    // Simulate detection processing
    // Generate a random similarity score between 0 and 100
    const similarityScore = Math.floor(Math.random() * 101);

    console.log("Simulated detection score:", similarityScore);

    // Return the similarity score and the original image base64
    return NextResponse.json({ similarityScore, detectedImage: imageBase64 });
  } catch (error) {
    console.error("Error in detect API:", error);
    if (error instanceof SyntaxError) {
      // Handle JSON parsing error
      return NextResponse.json(
        { message: "Invalid JSON body" },
        { status: 400 }
      );
    }
    return NextResponse.json(
      { message: "Internal Server Error" },
      { status: 500 }
    );
  }
}
