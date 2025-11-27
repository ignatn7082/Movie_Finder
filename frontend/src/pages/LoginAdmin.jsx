// src/pages/auth/LoginAdmin.jsx
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Shield, Eye, EyeOff, LogIn, AlertCircle } from "lucide-react";

export default function LoginAdmin() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      setError("Vui lòng nhập đầy đủ thông tin!");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await fetch("http://localhost:8000/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Đăng nhập thất bại. Kiểm tra lại thông tin!");
      }

      if (data.role !== "admin") {
        throw new Error("Cảnh báo: Bạn không có quyền truy cập khu vực quản trị!");
      }

      // Xóa token user nếu có
      localStorage.removeItem("user_token");
      localStorage.removeItem("user_username");

      // Lưu token admin
      localStorage.setItem("admin_token", data.access_token);
      localStorage.setItem("admin_username", data.username);

      // Thành công
      setTimeout(() => {
        navigate("/admin", { replace: true });
      }, 800);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-900 via-black to-purple-900 relative overflow-hidden">
      {/* Background effect */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-3xl" />
      <div className="absolute inset-0">
        <div className="absolute top-20 left-20 w-96 h-96 bg-red-600/30 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-purple-600/30 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      {/* Login Card */}
      <div className="relative z-10 w-full max-w-md">
        <div className="bg-black/60 backdrop-blur-2xl rounded-3xl shadow-2xl border border-red-800/50 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-red-600 to-purple-700 p-8 text-center">
            <div className="flex justify-center mb-4">
              <div className="p-5 bg-white/20 backdrop-blur-md rounded-full shadow-2xl">
                <Shield className="w-16 h-16 text-white" />
              </div>
            </div>
            <h1 className="text-4xl font-black text-white tracking-wider">ADMIN PANEL</h1>
            <p className="text-red-200 mt-2 text-sm">Khu vực quản trị hệ thống</p>
          </div>

          {/* Form */}
          <div className="p-8 space-y-6">
            {/* Error Alert */}
            {error && (
              <div className="flex items-center gap-3 p-4 bg-red-900/50 border border-red-700 rounded-xl text-red-200 animate-pulse">
                <AlertCircle className="w-6 h-6 flex-shrink-0" />
                <p className="text-sm">{error}</p>
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-6">
              {/* Username */}
              <div>
                <label className="block text-red-400 font-semibold mb-2 text-sm tracking-wider">
                  TÊN ĐĂNG NHẬP
                </label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value.trim())}
                  className="w-full px-5 py-4 bg-white/10 border border-red-700/50 rounded-xl text-white placeholder-red-300/50 focus:outline-none focus:border-red-500 focus:ring-4 focus:ring-red-500/20 transition-all duration-300"
                  placeholder="Nhập tên đăng nhập admin..."
                  disabled={loading}
                  autoFocus
                />
              </div>

              {/* Password */}
              <div className="relative">
                <label className="block text-red-400 font-semibold mb-2 text-sm tracking-wider">
                  MẬT KHẨU
                </label>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-5 py-4 pr-14 bg-white/10 border border-red-700/50 rounded-xl text-white placeholder-red-300/50 focus:outline-none focus:border-red-500 focus:ring-4 focus:ring-red-500/20 transition-all duration-300"
                  placeholder="Nhập mật khẩu bảo mật..."
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-11 text-red-400 hover:text-white transition"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || !username || !password}
                className="w-full py-5 bg-gradient-to-r from-red-600 to-purple-700 hover:from-red-500 hover:to-purple-600 disabled:from-gray-700 disabled:to-gray-600 text-white font-bold text-lg rounded-xl shadow-2xl hover:shadow-red-500/50 transform hover:scale-105 transition-all duration-300 flex items-center justify-center gap-3 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <div className="w-6 h-6 border-4 border-white/30 border-t-white rounded-full animate-spin" />
                    Đang xác thực...
                  </>
                ) : (
                  <>
                    <LogIn className="w-6 h-6" />
                    ĐĂNG NHẬP QUẢN TRỊ
                  </>
                )}
              </button>
            </form>

            {/* Footer */}
            <div className="text-center pt-6 border-t border-red-800/50">
              <p className="text-red-300 text-sm">
                Bạn là người dùng thông thường?{" "}
                <Link
                  to="/login/user"
                  className="text-cyan-400 font-bold hover:text-cyan-300 hover:underline transition"
                >
                  Đăng nhập User
                </Link>
              </p>
              <p className="text-red-400/60 text-xs mt-4">
                © 2025 MovieFinder • 
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}