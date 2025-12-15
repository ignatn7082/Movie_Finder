// components/search/ImageSearchInput.jsx
import { Upload, User, Film } from "lucide-react";

export default function ImageSearchInput({ 
  file, 
  preview, 
  searchMode, 
  setSearchMode, 
  setFile, 
  setPreview 
}) {
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
    }
  };

  return (
    <div className="space-y-8">
      {/* === CHỌN CHẾ ĐỘ TÌM KIẾM === */}
      <div className="flex justify-center">
        <div className="inline-flex bg-gray-100 dark:bg-gray-800 p-3 rounded-3xl shadow-2xl border border-gray-300 dark:border-gray-700">
          <button
            type ="button"
            onClick={() => setSearchMode("actor")}
            className={`flex items-center gap-4 px-10 py-5 rounded-2xl font-extrabold text-lg transition-all duration-300 shadow-lg ${
              searchMode === "actor"
                ? "bg-gradient-to-r from-orange-500 to-red-600 text-white scale-105"
                : "text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700"
            }`}
          >
            <User className="w-7 h-7" />
            Tìm diễn viên
          </button>
          <button
            type ="button"
            onClick={() => setSearchMode("content")}
            className={`flex items-center gap-4 px-10 py-5 rounded-2xl font-extrabold text-lg transition-all duration-300 shadow-lg ${
              searchMode === "content"
                ? "bg-gradient-to-r from-purple-500 to-indigo-600 text-white scale-105"
                : "text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700"
            }`}
          >
            <Film className="w-7 h-7" />
            Tìm nội dung phim
          </button>
        </div>
      </div>

      {/* === UPLOAD ẢNH === */}
      <label htmlFor="image-upload" className="block cursor-pointer">
        <input 
          id="image-upload" 
          type="file" 
          accept="image/*" 
          onChange={handleFileChange} 
          className="hidden" 
        />
        
        <div className={`relative border-4 border-dashed rounded-3xl p-12 text-center transition-all duration-500 overflow-hidden
          ${preview 
            ? "border-indigo-500 bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/30 dark:to-purple-900/30" 
            : "border-gray-400 hover:border-indigo-600 hover:bg-indigo-50/50 dark:hover:bg-gray-800"
          }`}>
          
          {preview ? (
            <div className="space-y-6">
              <img 
                src={preview} 
                alt="Preview" 
                className="mx-auto max-h-96 rounded-3xl shadow-2xl border-8 border-white dark:border-gray-700"
              />
              <p className="text-xl font-bold text-indigo-700 dark:text-indigo-300 animate-pulse">
                <Upload className="inline w-6 h-6 mr-2" />
                Nhấn để thay đổi ảnh
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              <div className={`w-32 h-32 mx-auto rounded-full flex items-center justify-center shadow-2xl
                ${searchMode === "actor" 
                  ? "bg-gradient-to-br from-orange-500 to-red-600" 
                  : "bg-gradient-to-br from-purple-500 to-indigo-600"
                }`}>
                {searchMode === "actor" ? 
                  <User className="w-16 h-16 text-white" /> : 
                  <Film className="w-16 h-16 text-white" />
                }
              </div>

              <div>
                <p className="text-3xl font-extrabold text-gray-800 dark:text-gray-200 mb-3">
                  {searchMode === "actor" 
                    ? "Tìm kiếm theo khuôn mặt diễn viên" 
                    : "Tìm phim theo cảnh phim"
                  }
                </p>
                <p className="text-lg text-gray-600 dark:text-gray-400">
                  {searchMode === "actor" 
                    ? "Tải lên ảnh diễn viên → Xem tất cả phim đã đóng + vai diễn" 
                    : "Tải lên cảnh phim → Tìm phim tương tự"
                  }
                </p>
              </div>

              <div className="text-sm font-medium text-indigo-600 dark:text-indigo-400">
                Đang chọn chế độ: <span className="font-bold">
                  {searchMode === "actor" ? "Tìm diễn viên" : "Tìm nội dung phim"}
                </span>
              </div>
            </div>
          )}
        </div>
      </label>
    </div>
  );
}