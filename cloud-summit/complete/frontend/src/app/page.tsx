'use client';

import { useEffect, useState } from 'react';

interface News {
  id: number;
  date: string;
  text: string;
  author: string;
}

export default function Home() {
  const [news, setNews] = useState<News[]>([]);

  useEffect(() => {
    fetch('http://localhost:5001/news')
      .then((res) => res.json())
      .then((data) => setNews(data));
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 bg-gray-100">
      <div className="w-full max-w-2xl">
        <div className="flex justify-center mb-4">
          <img src="/logo.png" alt="Logo" width="100" height="50" />
        </div>
        <h1 className="text-4xl font-bold text-center mb-8 text-black">Newsfeed</h1>
        <div className="space-y-4">
          {news.map((item) => (
            <div key={item.id} className="bg-white p-6 rounded-lg shadow-md">
              <p className="text-gray-800">{item.text}</p>
              <div className="text-right text-gray-500 text-sm mt-4">
                <p>{item.author}</p>
                <p>{new Date(item.date).toLocaleString()}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}