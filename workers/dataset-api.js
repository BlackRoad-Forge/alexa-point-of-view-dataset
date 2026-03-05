/**
 * Cloudflare Worker — POV Dataset API
 *
 * Provides a lightweight REST API for querying dataset metadata and samples.
 * Deploy with: wrangler deploy
 *
 * Endpoints:
 *   GET /              — API info and available endpoints
 *   GET /stats         — Dataset statistics
 *   GET /sample?n=5    — Random sample rows (default 5, max 50)
 *   GET /health        — Health check
 */

const DATASET_META = {
  name: "Point of View Message Conversion Dataset",
  version: "1.0",
  total_pairs: 46562,
  splits: {
    train: 32593,
    dev: 6984,
    test: 6985,
  },
  columns: ["input", "output"],
  placeholders: {
    "@CN@": "Contact Name (receiver)",
    "@SCN@": "Source Contact Name (sender)",
  },
  paper: "https://arxiv.org/abs/2010.02600",
  repository: "https://github.com/blackboxprogramming/alexa-point-of-view-dataset",
};

const SAMPLE_DATA = [
  { input: "tell @CN@ that i'll be late", output: "hi @CN@ , @SCN@ would like you to know that they'll be late." },
  { input: "ask @CN@ if he wants anything from trader joe's", output: "hi @CN@ , @SCN@ wants to know if you want anything from trader joe's?" },
  { input: "ask @CN@ what time is the meeting", output: "hey @CN@ , @SCN@ would like to know what time is the meeting" },
  { input: "tell @CN@ i miss them", output: "hi @CN@ , @SCN@ wanted you to know that they miss you" },
  { input: "ask @CN@ to pick up milk", output: "hey @CN@ , @SCN@ would like you to pick up milk" },
  { input: "tell @CN@ happy birthday", output: "hi @CN@ , @SCN@ says happy birthday!" },
  { input: "ask @CN@ did they finish the report", output: "hey @CN@ , @SCN@ wants to know if you finished the report" },
  { input: "tell @CN@ that the meeting is canceled", output: "hi @CN@ , @SCN@ would like you to know that the meeting is canceled" },
  { input: "ask @CN@ about the weekend plans", output: "hey @CN@ , @SCN@ is asking about the weekend plans" },
  { input: "tell @CN@ i said thank you", output: "hi @CN@ , @SCN@ wanted to say thank you" },
];

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Cache-Control": "public, max-age=300",
    },
  });
}

async function handleRequest(request) {
  const url = new URL(request.url);
  const path = url.pathname.replace(/\/+$/, "") || "/";

  if (request.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
    });
  }

  if (request.method !== "GET") {
    return jsonResponse({ error: "Method not allowed" }, 405);
  }

  switch (path) {
    case "/":
      return jsonResponse({
        api: "POV Dataset API",
        version: "1.0.0",
        endpoints: {
          "/": "API information",
          "/stats": "Dataset statistics",
          "/sample?n=5": "Random sample rows",
          "/health": "Health check",
        },
      });

    case "/stats":
      return jsonResponse(DATASET_META);

    case "/sample": {
      const n = Math.min(Math.max(parseInt(url.searchParams.get("n") || "5", 10), 1), 50);
      const shuffled = [...SAMPLE_DATA].sort(() => Math.random() - 0.5);
      return jsonResponse({
        count: Math.min(n, shuffled.length),
        samples: shuffled.slice(0, n),
      });
    }

    case "/health":
      return jsonResponse({
        status: "healthy",
        timestamp: new Date().toISOString(),
        version: "1.0.0",
      });

    default:
      return jsonResponse({ error: "Not found", path }, 404);
  }
}

export default {
  async fetch(request) {
    return handleRequest(request);
  },
};
