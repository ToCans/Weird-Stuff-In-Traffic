import { NextResponse } from "next/server";

const backendUrl = process.env.BACKEND_API_BASE_URL || "http://127.0.0.1:8000";

export async function POST(request: Request) {
  if (!backendUrl) {
    console.error("BACKEND_API_BASE_URL environment variable is not set.");
    return NextResponse.json(
      { message: "Backend API URL is not configured." },
      { status: 500 }
    );
  }

  try {
    // Get the prompt from the incoming request
    const { prompt } = await request.json();

    if (!prompt) {
      return NextResponse.json(
        { message: "Prompt is required" },
        { status: 400 }
      );
    }

    console.log(
      `Forwarding generate request for prompt: "${prompt}" to ${backendUrl}/generate`
    );

    // Forward the request to the actual backend API
    const backendResponse = await fetch(`${backendUrl}/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // Forward any other necessary headers from the original request if needed
        // 'Authorization': request.headers.get('Authorization') || '',
      },
      body: JSON.stringify({ prompt }),
    });

    // Check if the backend request was successful
    if (!backendResponse.ok) {
      const errorData = await backendResponse.text();
      console.error(
        `Backend API /generate error: ${backendResponse.status}`,
        errorData
      );
      // Return the error status and message from the backend
      return NextResponse.json(
        { message: `Backend error: ${errorData}` },
        { status: backendResponse.status }
      );
    }

    // Get the response data (assuming it's JSON with { images: [...] })
    const data = await backendResponse.json();

    // Return the response from the backend to the frontend
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error forwarding request to /generate backend:", error);
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
