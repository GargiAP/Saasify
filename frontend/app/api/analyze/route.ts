import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const { idea } = await req.json();

    if (!idea || idea.trim().length === 0) {
      return NextResponse.json(
        { error: "Idea is required" },
        { status: 400 }
      );
    }

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 120000); // 2 min timeout

    try {
      const mlResponse = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ idea }),
        signal: controller.signal,
      });

      clearTimeout(timeout);

      if (!mlResponse.ok) {
        const error = await mlResponse.text();
        console.error("ML service error:", error);
        return NextResponse.json(
          { error: "ML service failed" },
          { status: 500 }
        );
      }

      const data = await mlResponse.json();
      return NextResponse.json(data);

    } catch (fetchErr: any) {
      clearTimeout(timeout);
      if (fetchErr.name === "AbortError") {
        return NextResponse.json(
          { error: "Analysis timed out. Please try again." },
          { status: 504 }
        );
      }
      throw fetchErr;
    }

  } catch (err) {
    console.error("API error:", err);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

export const maxDuration = 120;