'use client';

import { useEffect, useState } from 'react';

type News = {
  id: number;
  date: string;
  text: string;
  author: string;
};

export default function Home() {
  const [news, setNews] = useState<News[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const response = await fetch('http://localhost:8080/api/news');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        data.sort((a: News, b: News) => new Date(b.date).getTime() - new Date(a.date).getTime());
        setNews(data);
      } catch (err) {
        if (err instanceof Error) {
            setError(`Failed to fetch news: ${err.message}. Please ensure the backend is running.`);
        } else {
            setError("An unknown error occurred.");
        }
      }
    };

    fetchNews();
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center p-12 bg-gray-900 text-white">
      <div className="w-full max-w-4xl">
        <header className="text-center mb-8 flex flex-col items-center">
          <img src="/imagen-imagen-3.0-generate-002-20250923-141133-0.png" alt="News Feed Logo" style={{ maxHeight: '100px' }} className="mb-4" />
          <h1 className="text-5xl font-bold text-white">News Feed</h1>
          <p className="text-gray-400">Latest updates from our team</p>
        </header>
        
        {error && (
          <div className="bg-red-800 border border-red-600 text-white px-4 py-3 rounded-lg relative mb-6" role="alert">
            <strong className="font-bold">Error:</strong>
            <span className="block sm:inline ml-2">{error}</span>
          </div>
        )}

        <div className="bg-gray-800 shadow-lg rounded-lg h-[70vh] overflow-y-auto">
          <ul className="divide-y divide-gray-700">
            {news.length > 0 ? (
              news.map((item) => (
                <li key={item.id} className="p-6 hover:bg-gray-700 transition-colors duration-200">
                  <p className="text-gray-300 mb-3 text-lg">{item.text}</p>
                  <div className="flex justify-between items-center text-sm text-gray-500">
                    <span>{item.author}</span>
                    <span>{new Date(item.date).toLocaleString()}</span>
                  </div>
                </li>
              ))
            ) : (
              !error && <li className="p-6 text-center text-gray-500">Loading news...</li>
            )}
          </ul>
        </div>
      </div>
    </main>
  );
}