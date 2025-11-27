// components/search/ImageSearchInput.jsx
import { Upload, Image } from "lucide-react";

export default function ImageSearchInput({ file, preview, selectedImageModel, setFile, setPreview, setSelectedImageModel }) {
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
    }
  };

  return (
    <div className="relative group">
      <label htmlFor="image-upload" className="block cursor-pointer">
        <input id="image-upload" type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
        <div className={`border-4 border-dashed rounded-3xl p-12 text-center transition-all duration-300 ${preview ? "border-indigo-400 bg-indigo-50/50" : "border-gray-300 hover:border-indigo-500"}`}>
          {preview ? (
            <div className="space-y-6">
              <img src={preview} alt="Preview" className="mx-auto max-h-96 rounded-2xl shadow-2xl border-4 border-white" />
              <p className="text-indigo-600 font-bold text-lg animate-pulse">
                <Upload className="inline w-5 h-5 mr-2" /> Nhấn để thay đổi ảnh
              </p>
            </div>
          ) : (
            <div>
              <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center shadow-2xl">
                <Image className="w-12 h-12 text-white" />
              </div>
              <p className="text-2xl font-bold text-gray-700 mb-2">Tải lên Poster, Ảnh Diễn Viên hoặc Cảnh Phim</p>
              <p className="text-gray-500">Kéo thả hoặc nhấn để chọn ảnh</p>
            </div>
          )}
        </div>
      </label>

      <div className="mt-6 flex justify-center items-center space-x-4">
        <span className="text-lg font-medium text-gray-700">Mô hình AI:</span>
        <select
          value={selectedImageModel}
          onChange={(e) => setSelectedImageModel(e.target.value)}
          className="px-6 py-3 bg-gradient-to-r from-indigo-100 to-purple-100 dark:from-indigo-900 dark:to-purple-900 rounded-xl font-bold text-indigo-700 shadow-lg"
        >
          <option value="two_steps_clip">CLIP (Thông minh hơn)</option>
          <option value="two_steps_resnet">ResNet50 (Nhanh hơn)</option>
        </select>
      </div>
    </div>
  );
}