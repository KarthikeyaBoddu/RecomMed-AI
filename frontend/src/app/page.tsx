
"use client";

import { useState } from "react";
import {
  searchMedicine,
  type MedicineCandidate,
} from "@/lib/api";

interface SelectedMedicine {
  rxcui: string;
  name: string;
}

export default function Home() {
  const [input, setInput] = useState("");
  const [results, setResults] = useState<MedicineCandidate[]>([]);
  const [medicines, setMedicines] = useState<SelectedMedicine[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch() {
    if (!input.trim()) return;

    setLoading(true);
    setError("");
    setResults([]);

    try {
      const data = await searchMedicine(input.trim());

      if (data.status === "service_unavailable") {
        throw new Error("The medicine data service is unavailable.");
      }

      setResults(data.results);

      if (data.results.length === 0) {
        setError("No matching medicine concepts were found.");
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }

  function addMedicine(medicine: SelectedMedicine) {
    setMedicines((current) => {
      if (current.some((item) => item.rxcui === medicine.rxcui)) {
        return current;
      }

      return [...current, medicine];
    });

    setResults([]);
    setInput("");
    setError("");
  }

  function removeMedicine(rxcui: string) {
    setMedicines((current) =>
      current.filter((medicine) => medicine.rxcui !== rxcui)
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 px-6 py-5">
        <div className="mx-auto flex max-w-5xl items-center justify-between">
          <h1 className="text-2xl font-bold">
            RecomMed<span className="text-teal-400"> AI</span>
          </h1>
          <span className="rounded-full border border-teal-900 px-3 py-1 text-xs text-teal-300">
            Medication Safety
          </span>
        </div>
      </header>

      <section className="mx-auto max-w-5xl px-6 py-16">
        <p className="mb-4 text-sm font-semibold uppercase tracking-[0.2em] text-teal-400">
          Your medication companion
        </p>

        <h2 className="max-w-3xl text-4xl font-bold leading-tight md:text-5xl">
          Understand your medicines.
          <span className="text-teal-400">
            {" "}Make informed decisions.
          </span>
        </h2>

        <p className="mt-5 max-w-2xl leading-7 text-slate-400">
          Search medicine concepts and build a medication list for
          evidence-based safety screening.
        </p>

        <div className="mt-10 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h3 className="text-xl font-semibold">Your medication list</h3>

          <div className="mt-5 flex flex-col gap-3 sm:flex-row">
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") void handleSearch();
              }}
              placeholder="Search a medicine, e.g. cetirizine"
              className="min-w-0 flex-1 rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-teal-400"
            />

            <button
              onClick={() => void handleSearch()}
              disabled={loading || !input.trim()}
              className="rounded-lg bg-teal-500 px-6 py-3 font-semibold text-slate-950 disabled:opacity-50"
            >
              {loading ? "Searching..." : "Search medicine"}
            </button>
          </div>

          {error && (
            <p role="alert" className="mt-4 text-sm text-amber-300">
              {error}
            </p>
          )}

          {results.length > 0 && (
            <div className="mt-5 space-y-3">
              <h4 className="font-medium">Select a matching concept</h4>

              {results.map((result) => (
                <div
                  key={result.rxcui}
                  className="flex flex-col gap-3 rounded-lg border border-slate-700 p-4 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div>
                    <p className="font-medium">{result.name}</p>
                    <p className="mt-1 text-xs text-slate-400">
                      RxCUI: {result.rxcui}
                    </p>
                  </div>

                  <button
                    onClick={() =>
                      addMedicine({
                        rxcui: result.rxcui,
                        name: result.name,
                      })
                    }
                    className="rounded-lg border border-teal-700 px-4 py-2 text-sm text-teal-300 hover:bg-teal-950"
                  >
                    Add
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="mt-8 space-y-3">
            <h4 className="font-medium">
              Selected medicines ({medicines.length})
            </h4>

            {medicines.map((medicine) => (
              <div
                key={medicine.rxcui}
                className="flex items-center justify-between rounded-lg border border-slate-800 px-4 py-3"
              >
                <div>
                  <p>{medicine.name}</p>
                  <p className="text-xs text-slate-500">
                    RxCUI: {medicine.rxcui}
                  </p>
                </div>

                <button
                  onClick={() => removeMedicine(medicine.rxcui)}
                  className="text-sm text-slate-400 hover:text-red-400"
                >
                  Remove
                </button>
              </div>
            ))}

            {medicines.length === 0 && (
              <p className="rounded-lg border border-dashed border-slate-700 p-5 text-center text-sm text-slate-500">
                Search for a medicine and add it here.
              </p>
            )}
          </div>

          <button
            disabled={medicines.length < 2}
            onClick={() =>
              alert("Interaction checking will be implemented next.")
            }
            className="mt-6 w-full rounded-lg bg-slate-100 px-5 py-3 font-semibold text-slate-950 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Prepare safety check
          </button>

          <p className="mt-4 text-xs leading-5 text-slate-500">
            Medicine search identifies candidate concepts only. Interaction
            checking is not yet implemented. Do not use this prototype to
            make medical decisions.
          </p>
        </div>
      </section>
    </main>
  );
}
