export default function SearchTabs({ mode, setMode }) {
  return (
    <div className="flex bg-gray-100 dark:bg-gray-800 rounded-xl p-1 w-fit mx-auto mb-6">
      {["image", "text"].map((type) => (
        <button
          key={type}
          onClick={() => setMode(type)}
          className={`px-5 py-2 rounded-lg transition ${
            mode === type
              ? "bg-blue-600 text-white"
              : "hover:bg-gray-200 dark:hover:bg-gray-700"
          }`}
        >
          {type === "image" ? "📸 Tìm theo Ảnh" : "📝 Tìm theo Mô tả"}
        </button>
      ))}
    </div>
  );
}
