import React from "react";
import { Navigate } from "react-router-dom";

/**
 * ProtectedRoute kiểm tra quyền người dùng trước khi hiển thị trang.
 * - roles: mảng các quyền được phép (["admin"], ["user","editor"], ...)
 * - Lưu ý: role của user được lấy từ localStorage (ví dụ "user","editor","admin")
 */
export default function ProtectedRoute({ roles, children }) {
  const token = localStorage.getItem("token");
  const userRole = localStorage.getItem("role"); // 🧠 giá trị được lưu khi đăng nhập

  if (!token) {
    // chưa đăng nhập
    return <Navigate to="/login" replace />;
  }

  if (roles && !roles.includes(userRole)) {
    // không đủ quyền
    return <Navigate to="/403" replace />;
  }

  return children;
}
