"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API = "http://localhost:3001/api";

const MOOD_CLASSES = {
  happy: "bg-green-100 text-green-800",
  neutral: "bg-yellow-100 text-yellow-800",
  sad: "bg-blue-100 text-blue-800",
};

export default function DashboardPage() {
  const router = useRouter();
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/auth/me`, { credentials: "include" })
      .then((res) => {
        if (!res.ok) { router.replace("/login"); return null; }
        return fetch(`${API}/entries`, { credentials: "include" });
      })
      .then((res) => res && res.json())
      .then((data) => {
        if (data) setEntries(data);
        setLoading(false);
      })
      .catch(() => router.replace("/login"));
  }, [router]);

  const handleLogout = async () => {
    await fetch(`${API}/auth/logout`, { method: "POST", credentials: "include" });
    router.replace("/login");
  };

  if (loading) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">My Diary</h1>
        <button
          data-testid="logout-btn"
          onClick={handleLogout}
          className="text-sm text-gray-600 hover:text-gray-900"
        >
          Log out
        </button>
      </nav>
      <main className="max-w-2xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-800">Entries</h2>
          <Link
            href="/entries/new"
            data-testid="new-entry-btn"
            className="bg-blue-600 text-white rounded px-4 py-2 text-sm font-medium hover:bg-blue-700"
          >
            New entry
          </Link>
        </div>
        {entries.length === 0 ? (
          <p data-testid="empty-state" className="text-gray-500 text-center py-12">
            No entries yet. Write your first one!
          </p>
        ) : (
          <ul data-testid="entry-list" className="space-y-3">
            {entries.map((entry) => (
              <li key={entry.id}>
                <Link href={`/entries/${entry.id}`}>
                  <div
                    data-testid="entry-card"
                    className="bg-white rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow cursor-pointer"
                  >
                    <div className="flex items-center justify-between">
                      <span
                        data-testid="entry-card-title"
                        className="font-medium text-gray-900"
                      >
                        {entry.title}
                      </span>
                      <span
                        data-testid="entry-card-mood"
                        className={`text-xs px-2 py-1 rounded-full font-medium ${MOOD_CLASSES[entry.mood] || ""}`}
                      >
                        {entry.mood}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      {new Date(entry.created_at).toLocaleDateString("en-US", {
                        year: "numeric", month: "short", day: "numeric",
                      })}
                    </p>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  );
}
