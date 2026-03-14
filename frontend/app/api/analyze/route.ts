import { NextResponse } from "next/server";
import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI(
  process.env.GEMINI_API_KEY as string
);

export async function POST(req: Request) {
  try {

    const { idea } = await req.json();

    if (!idea || idea.trim().length === 0) {
      return NextResponse.json(
        { error: "Idea is required" },
        { status: 400 }
      );
    }

    const prompt = `
You are a startup analyst.

Your task is to INTERPRET the idea clearly.

Do NOT validate or judge the idea.
Do NOT suggest improvements.

Return ONLY valid JSON in this format:

{
  "problem_statement": "",
  "solution_summary": "",
  "target_user": "",
  "assumptions": []
}

Startup idea:
"${idea}"
`;

    const model = genAI.getGenerativeModel({
      model: "gemini-2.5-flash",
    });

    const result = await model.generateContent(prompt);
    const text = result.response.text();

    const cleanedText = text
      .replace(/```json/g, "")
      .replace(/```/g, "")
      .trim();

    let interpretation;

    try {
      interpretation = JSON.parse(cleanedText);
    } catch (err) {
      console.error("Gemini parsing error:", cleanedText);

      return NextResponse.json(
        { error: "AI response parsing failed" },
        { status: 500 }
      );
    }

    let mlData = null;

    try {

      const mlResponse = await fetch(
        "http://127.0.0.1:8000/market-category",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ idea }),
        }
      );

      if (mlResponse.ok) {
        mlData = await mlResponse.json();
      }

    } catch (err) {
      console.error("ML service error:", err);
    }


    return NextResponse.json({
      success: true,
      interpretation,
      market_category: mlData?.category ?? null,
      similarity_score: mlData?.similarity ?? null,
    });

  } catch (err) {

    console.error("API error:", err);

    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}