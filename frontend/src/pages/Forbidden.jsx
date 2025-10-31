import React from "react";
import { Link } from "react-router-dom";

export default function Forbidden() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen text-center bg-gray-50 dark:bg-gray-900">
      <h1 className="text-6xl font-bold text-red-600 mb-4">403</h1>
      <p className="text-xl text-gray-700 dark:text-gray-300 mb-6">
        🚫 Bạn không có quyền truy cập trang này.
      </p>
      <Link
        to="/"
        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition"
      >
        Quay về trang chủ
      </Link>
    </div>
  );
}
