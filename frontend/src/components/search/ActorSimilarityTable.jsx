// components/search/ActorSimilarityTable.jsx
import { User } from "lucide-react";

export default function ActorSimilarityTable({ actors }) {
  return (
    <div className="lg:w-80">
      <h5 className="text-xl font-bold text-gray-800 dark:text-gray-200 mb-4 flex items-center">
        <User className="w-6 h-6 mr-2 text-purple-600" />
        Diễn viên khớp theo ảnh
      </h5>
      <div className="bg-gray-50 dark:bg-gray-700/50 rounded-2xl border border-gray-200 dark:border-gray-600 overflow-hidden">
        <div className="max-h-64 overflow-y-auto scrollbar-thin scrollbar-thumb-indigo-500">
          <table className="w-full text-sm">
            <thead className="bg-indigo-100 dark:bg-indigo-900/50 sticky top-0">
              <tr>
                <th className="px-4 py-3 text-left font-bold text-indigo-700 dark:text-indigo-300">Diễn viên</th>
                <th className="px-4 py-3 text-right font-bold text-green-600 dark:text-green-400">Độ tương đồng</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-600">
              {actors.map((a, i) => (
                <tr key={i} className="hover:bg-indigo-50 dark:hover:bg-indigo-900/30 transition-colors">
                  <td className="px-4 py-3 font-medium text-gray-800 dark:text-gray-200 truncate">{a.actor}</td>
                  <td className="px-4 py-3 text-right">
                    <span className="inline-block px-3 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-full font-bold text-sm">
                      {(a.similarity * 100).toFixed(1)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">{actors.length} diễn viên được phát hiện</p>
    </div>
  );
}