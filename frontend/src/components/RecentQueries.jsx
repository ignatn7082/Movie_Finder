export default function RecentQueries({ onSelect }) {
  const queries = JSON.parse(localStorage.getItem("recentQueries") || "[]");

  if (!queries.length) return null;
  return (
    <div className="mt-6">
      <h4 className="text-sm font-semibold text-gray-600 mb-2">
        🔁 Lịch sử tìm kiếm gần đây
      </h4>
      <div className="flex flex-wrap gap-2">
        {queries.map((q, i) => (
          <button
            key={i}
            onClick={() => onSelect(q)}
            className="bg-gray-200 dark:bg-gray-800 px-3 py-1 rounded-full text-sm hover:bg-blue-600 hover:text-white"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
