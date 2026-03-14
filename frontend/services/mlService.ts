export async function getMarketCategory(idea: string) {

  const response = await fetch("http://localhost:8000/market-category", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ idea }),
  });

  if (!response.ok) {
    throw new Error("ML service error");
  }

  return response.json();
}