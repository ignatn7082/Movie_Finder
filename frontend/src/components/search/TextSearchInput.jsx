// components/search/TextSearchInput.jsx
import { Search as SearchIcon } from "lucide-react";

export default function TextSearchInput({ query, setQuery }) {
  return (
    <div className="relative">
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ví dụ: Phim về người lính trở về từ chiến tranh, đạo diễn Victor Vũ, diễn viên Lan Ngọc..."
        className="w-full p-6 pr-16 text-lg bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-gray-700 dark:to-gray-800 rounded-2xl border-2 border-indigo-200 dark:border-indigo-700 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-300 dark:focus:ring-indigo-800 shadow-xl resize-none transition-all"
        rows="5"
      />
      <SearchIcon className="absolute right-6 top-6 w-8 h-8 text-indigo-500" />
    </div>
  );
}