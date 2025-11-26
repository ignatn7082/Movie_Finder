import React from 'react';
import { Image, Type } from 'lucide-react';

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

const SidebarGuide = ({ tab, handleExampleClick }) => {
    const isTextTab = tab === 'text';
    const examples = isTextTab ? searchExamples.text : searchExamples.image;

    return (
        <div className="p-4 rounded-xl bg-white dark:bg-gray-800 shadow-lg">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                {isTextTab ? "📚 Gợi ý tìm kiếm văn bản" : "📸 Gợi ý tìm kiếm bằng ảnh"}
            </h3>
            <ul className="space-y-3">
                {examples.map((example, index) => (
                    <li key={index} className="text-sm">
                        <p className="font-medium text-indigo-600 dark:text-indigo-400 mb-1">{example.title}</p>
                        <button
                            onClick={() => isTextTab ? handleExampleClick(example.query) : null}
                            className={`text-left w-full p-2 rounded-lg transition-colors ${
                                isTextTab ? "bg-gray-100 dark:bg-gray-700 hover:bg-indigo-100 dark:hover:bg-indigo-600/50 text-gray-700 dark:text-gray-300 cursor-pointer" : "bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-default"
                            }`}
                        >
                            {isTextTab ? `"${example.query}"` : example.info}
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default SidebarGuide;