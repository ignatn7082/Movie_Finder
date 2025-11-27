// components/search/SearchSidebar.jsx
import { Sparkles, Image, Type } from "lucide-react";

const searchExamples = {
  text: [
    { title: "Tìm theo tên/mô tả", query: "Phim về người lính sau chiến tranh" },
    { title: "Tìm theo đạo diễn", query: "Đạo diễn Bùi Thạc Chuyên" },
    { title: "Tìm theo thể loại", query: "Phim tâm lý xã hội" },
    { title: "Tìm theo diễn viên/vai diễn", query: "Diễn viên Thái Hòa" },
  ],
  image: [
    { title: "Tìm bằng poster phim", info: "Tải lên poster phim 'Hai Phượng'" },
    { title: "Tìm bằng ảnh diễn viên", info: "Tải lên ảnh Trấn Thành" },
    { title: "Tìm bằng ảnh một cảnh phim", info: "Tải lên ảnh một cảnh trong 'Mắt Biếc'" },
  ]
};

export default function SearchSidebar({ tab, onExampleClick }) {
  const isTextTab = tab === 'text';
  const examples = isTextTab ? searchExamples.text : searchExamples.image;

  return (
    <div className="p-6 bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-gray-900 dark:to-gray-800 rounded-2xl shadow-xl border border-indigo-200 dark:border-indigo-900 h-full overflow-y-auto">
      <div className="flex items-center mb-6">
        <div className="p-3 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl shadow-lg mr-4">
          <Sparkles className="w-6 h-6 text-white" />
        </div>
        <h3 className="text-2xl font-extrabold text-indigo-700 dark:text-indigo-400">
          Hướng Dẫn {isTextTab ? "Tìm Văn Bản" : "Tìm Bằng Ảnh"}
        </h3>
      </div>

      <div className="space-y-6">
        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl shadow-md border border-indigo-100 dark:border-indigo-800">
          <ul className="space-y-3 text-sm">
            {isTextTab ? (
              <>
                <li className="flex items-start"><span className="text-indigo-600 mr-2">•</span> <strong>Tìm bằng mô tả tự nhiên</strong> – "Phim buồn về tình yêu tuổi trẻ"</li>
                <li className="flex items-start"><span className="text-indigo-600 mr-2">•</span> Hỗ trợ tìm đạo diễn, diễn viên, thể loại</li>
                <li className="flex items-start"><span className="text-indigo-600 mr-2">•</span> Công nghệ tìm kiếm ngữ nghĩa AI</li>
              </>
            ) : (
              <>
                <li className="flex items-start"><span className="text-purple-600 mr-2">•</span> <strong>Poster, ảnh diễn viên hoặc cảnh phim</strong></li>
                <li className="flex items-start"><span className="text-purple-600 mr-2">•</span> Hỗ trợ 2 mô hình AI: CLIP & ResNet50</li>
                <li className="flex items-start"><span className="text-purple-600 mr-2">•</span> Nhận diện cả diễn viên trong ảnh</li>
              </>
            )}
          </ul>
        </div>

        <div>
          <h4 className="text-lg font-bold text-gray-800 dark:text-gray-200 mb-4 flex items-center">
            {isTextTab ? <Type className="w-5 h-5 mr-2 text-indigo-600" /> : <Image className="w-5 h-5 mr-2 text-purple-600" />}
            Ví dụ {isTextTab ? "tìm kiếm" : "hình ảnh"}
          </h4>
          <div className="space-y-3">
            {examples.map((example, index) => (
              <div 
                key={index}
                onClick={isTextTab ? () => onExampleClick(example.query) : undefined}
                className={`p-4 rounded-xl border-2 transition-all transform hover:scale-105 ${
                  isTextTab 
                    ? 'bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 border-blue-300 dark:border-blue-700 cursor-pointer shadow-md hover:shadow-xl' 
                    : 'bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600'
                }`}
              >
                <p className="font-bold text-gray-800 dark:text-gray-200">{example.title}</p>
                <p className={`text-sm mt-1 ${isTextTab ? 'text-indigo-600 dark:text-indigo-400 font-medium' : 'text-gray-600 dark:text-gray-400 italic'}`}>
                  {isTextTab ? `“${example.query}”` : example.info}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}