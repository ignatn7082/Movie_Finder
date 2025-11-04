// src/components/ProtectedRoute.jsx
import { Navigate } from "react-router-dom";

export default function ProtectedRoute({ roles = [], children }) {
  const userToken = localStorage.getItem("user_token");
  const adminToken = localStorage.getItem("admin_token");

  if (roles.includes("admin") && !adminToken)
    return <Navigate to="/login/admin" replace />;

  if (roles.includes("user") && !userToken)
    return <Navigate to="/login/user" replace />;

  return children;
}
