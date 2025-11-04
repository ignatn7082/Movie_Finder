import React from "react";
import { Navigate } from "react-router-dom";

/**
 * ProtectedRoute kiểm tra quyền người dùng trước khi hiển thị trang.
 * - roles: mảng quyền được phép (["admin"], ["user"])
 * - Hỗ trợ 2 loại token riêng biệt: admin_token & user_token
 */
export default function ProtectedRoute({ roles = [], children }) {
  // Lấy token và role hiện tại từ localStorage
  const userToken = localStorage.getItem("user_token");
  const adminToken = localStorage.getItem("admin_token");

  let currentRole = null;
  let token = null;

  if (adminToken) {
    currentRole = "admin";
    token = adminToken;
  } else if (userToken) {
    currentRole = "user";
    token = userToken;
  }

  //  Chưa đăng nhập
  if (!token) {
    // Nếu route yêu cầu admin → chuyển về login admin, ngược lại về login user
    const redirectPath = roles.includes("admin")
      ? "/login/admin"
      : "/login/user";
    return <Navigate to={redirectPath} replace />;
  }

  //  Nếu role hiện tại không nằm trong roles cho phép
  if (roles.length > 0 && !roles.includes(currentRole)) {
    return <Navigate to="/403" replace />;
  }

  //  Có quyền, render nội dung con
  return children;
}
