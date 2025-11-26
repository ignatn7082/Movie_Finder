import React from 'react';
import { X, Calendar, Clapperboard } from 'lucide-react';

const MovieDetailsModal = ({ selected, BaseURL, setSelected }) => {
    if (!selected) {
        return null;
    }

    return (
        <div className="sticky top-4 bg-white dark:bg-gray-800 p-6 rounded-xl shadow-xl border border-indigo-200 dark:border-indigo-700">
            <div className="flex justify-between items-start mb-4">
                <h2 className="text-xl font-bold text-indigo-600 dark:text-indigo-400">
                    Chi tiết Phim
                </h2>
                <button onClick={() => setSelected(null)} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                    <X className="w-6 h-6" />
                </button>
            </div>

            <div className="flex space-x-4">
                <img 
                    src={selected.poster && selected.poster.startsWith('http') ? selected.poster : `${BaseURL}${selected.poster}`}
                    alt={selected.title} 
                    className="w-24 h-36 object-cover rounded-lg flex-shrink-0 shadow-md"
                    onError={(e) => { e.target.onerror = null; e.target.src = "placeholder.jpg"; }}
                />
                
                <div className="flex-grow min-w-0">
                    <h3 className="text-2xl font-extrabold text-gray-900 dark:text-white leading-tight">
                        {selected.original_title || selected.title}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 italic mb-3">
                        {selected.title !== selected.original_title && selected.title}
                    </p>
                    
                    <div className="space-y-2 text-sm">
                        <p className="text-gray-600 dark:text-gray-400 flex items-center">
                            <Calendar className="w-4 h-4 mr-2 text-indigo-500" />
                            <b>Năm:</b> <span className="ml-1 text-gray-800 dark:text-gray-200">{selected.release_date ? selected.release_date.split('-')[0] : 'N/A'}</span>
                        </p>
                        <p className="text-gray-600 dark:text-gray-400 flex items-center">
                            <Clapperboard className="w-4 h-4 mr-2 text-indigo-500" />
                            <b>Đạo diễn:</b> <span className="ml-1 text-gray-800 dark:text-gray-200">{selected.director || 'Không rõ'}</span>
                        </p>
                    </div>
                </div>
            </div>
            
            <div className="mt-4 space-y-3">
                <p className="text-gray-600 dark:text-gray-400">
                    <b>Tóm tắt:</b>
                </p>
                <p className="text-sm text-gray-800 dark:text-gray-200 leading-relaxed italic">
                    {selected.overview || "Tóm tắt đang được cập nhật."}
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                    <p className="text-gray-600 dark:text-gray-400">
                        <b>Thể loại:</b> <span className="text-gray-800 dark:text-gray-200">{selected.genres_vn || "Không rõ"}</span>
                    </p>
                    <p className="text-gray-600 dark:text-gray-400">
                        <b>Diễn viên chính:</b> <span className="text-gray-800 dark:text-gray-200">{selected.stars || "Không rõ"}</span>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default MovieDetailsModal;