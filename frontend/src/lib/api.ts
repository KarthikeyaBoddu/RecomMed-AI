
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export interface MedicineCandidate {
  rxcui: string;
  name: string;
  score: string | null;
}

export interface MedicineSearchResponse {
  query: string;
  results: MedicineCandidate[];
  status: string;
}

export async function searchMedicine(
  name: string
): Promise<MedicineSearchResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/medicines/search`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name }),
    }
  );

  if (!response.ok) {
    throw new Error(`Medicine search failed (${response.status})`);
  }

  return response.json();
}
