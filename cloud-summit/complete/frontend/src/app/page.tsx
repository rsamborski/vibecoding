"use client";

import { useEffect, useState } from 'react';

interface Article {
  id: number;
  date: string;
  text: string;
  author: string;
}

export default function Home() {
  const [articles, setArticles] = useState<Article[]>([]);

  useEffect(() => {
    fetch('http://127.0.0.1:5001/api/news')
      .then((res) => res.json())
      .then((data) => {
        setArticles(data);
      });
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
        <img src="/imagen-imagen-3.0-generate-002-20250909-183923-0.png" alt="News Feed Logo" className="max-w-[200px] max-h-[150px]" />
        <h1 className="text-4xl font-bold text-center text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">News Feed</h1>
      </div>

      <div className="mt-12 w-full max-w-5xl">
        {articles.map((article, index) => (
          <div
            key={article.id}
            className={`p-4 my-4 rounded-lg ${
              index % 2 === 0 ? 'bg-red-900' : 'bg-blue-900'
            }`}
          >
            <p className="text-lg text-white">{article.text}</p>
            <p className="text-sm text-white mt-2">
              By {article.author} on {new Date(article.date).toLocaleDateString()}
            </p>
          </div>
        ))}
      </div>
    </main>
  );
}