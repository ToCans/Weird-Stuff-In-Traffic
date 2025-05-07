import { NextResponse } from "next/server";

const backendUrl = process.env.BACKEND_API_BASE_URL;

export async function POST(request: Request) {
  if (!backendUrl) {
    console.error("BACKEND_API_BASE_URL environment variable is not set.");
    return NextResponse.json(
      { message: "Backend API URL is not configured." },
      { status: 500 }
    );
  }

  try {
    // Get the prompt and imageBase64 from the incoming request
    const { prompt, imageBase64 } = await request.json();

    // Basic validation
    if (!prompt || !imageBase64) {
      return NextResponse.json(
        { message: "Missing prompt or imageBase64" },
        { status: 400 }
      );
    }

    console.log(
      `Forwarding detect request for prompt: "${prompt}" to ${backendUrl}/detect`
    );

    // Forward the request to the actual backend API
    const backendResponse = await fetch(`${backendUrl}/detect`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // Forward any other necessary headers if needed
      },
      body: JSON.stringify({ prompt, imageBase64 }), // Send both prompt and image
    });

    // Check if the backend request was successful
    if (!backendResponse.ok) {
      const errorData = await backendResponse.text();
      console.error(
        `Backend API /detect error: ${backendResponse.status}`,
        errorData
      );
      return NextResponse.json(
        { message: `Backend error: ${errorData}` },
        { status: backendResponse.status }
      );
    }

    // Get the response data (assuming it's JSON with { similarityScore: ... })
    const data = await backendResponse.json();

    // Return the response from the backend to the frontend
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error forwarding request to /detect backend:", error);
    // Handle potential network errors or JSON parsing errors
    if (error instanceof SyntaxError) {
      return NextResponse.json(
        {
          message: "Invalid JSON received from backend or invalid request body",
        },
        { status: 500 }
      );
    }
    return NextResponse.json(
      { message: "Internal Server Error while contacting backend" },
      { status: 500 }
    );
  }
}
