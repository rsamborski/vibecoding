'use client';

import { useEffect, useState } from 'react';

interface NewsItem {
  id: number;
  date: string;
  text: string;
  author: string;
}

export default function Home() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const response = await fetch('http://localhost:5001/api/news');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setNews(data);
      } catch (error) {
        if (error instanceof Error) {
          setError(error.message);
        } else {
          setError('An unknown error occurred');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      <div className="container mx-auto p-8">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
            Latest News
          </h1>
          <p className="mt-2 text-lg text-gray-400">Your daily dose of updates</p>
        </header>

        <div className="max-w-3xl mx-auto">
          {loading && <p className="text-center text-gray-400">Loading news...</p>}
          {error && <p className="text-center text-red-400">Error: {error}</p>}
          {!loading && !error && (
            <div className="space-y-6">
              {news.map((item, index) => {
                const bgColor = index % 2 === 0 ? 'bg-gray-800 bg-opacity-50' : 'bg-blue-900 bg-opacity-50';
                return (
                  <div
                    key={item.id}
                    className={`border border-gray-700 rounded-xl shadow-lg overflow-hidden transform hover:scale-105 transition-transform duration-300 ${bgColor}`}
                  >
                    <div className="p-6">
                      <div className="flex justify-between items-center mb-4">
                        <p className="text-sm text-gray-400">{new Date(item.date).toLocaleDateString()}</p>
                        <p className="text-xs font-semibold text-purple-400 uppercase tracking-wider">By {item.author}</p>
                      </div>
                      <p className="text-xl font-medium text-gray-100">{item.text}</p>
                    </div>
                    {index < news.length - 1 && <hr className="border-gray-700" />}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}