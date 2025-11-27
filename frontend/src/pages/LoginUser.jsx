// src/pages/auth/LoginUser.jsx
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { User, Eye, EyeOff, LogIn, Sparkles, AlertCircle } from "lucide-react";

export default function LoginUser() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password) {
      setError("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await fetch("http://localhost:8000/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username.trim(), password }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Đăng nhập thất bại. Vui lòng thử lại!");
      }

      // Cho phép cả user và editor đăng nhập (không bắt buộc phải role = "user")
      if (data.role === "admin") {
        throw new Error("Tài khoản Admin không được phép đăng nhập ở đây!");
      }

      // Xóa token admin nếu có
      localStorage.removeItem("admin_token");
      localStorage.removeItem("admin_username");

      // Lưu thông tin user
      localStorage.setItem("user_token", data.access_token);
      localStorage.setItem("user_username", data.username);

      // Thành công → chuyển về trang chủ mượt mà
      setTimeout(() => {
        navigate("/", { replace: true });
      }, 1000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-black/40 backdrop-blur-3xl" />
        <div className="absolute top-0 left-0 w-96 h-96 bg-blue-500/30 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-purple-500/30 rounded-full blur-3xl animate-pulse delay-700" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-pink-500/20 rounded-full blur-3xl animate-ping" />
      </div>

      {/* Login Card */}
      <div className="relative z-10 w-full max-w-md mx-4">
        <div className="bg-white/10 backdrop-blur-2xl rounded-3xl shadow-2xl border border-white/20 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-700 p-10 text-center relative">
            <div className="absolute inset-0 bg-black/20" />
            <div className="relative z-10">
              <div className="flex justify-center mb-5">
                <div className="p-6 bg-white/20 backdrop-blur-md rounded-full shadow-2xl animate-bounce">
                  <Sparkles className="w-14 h-14 text-white" />
                </div>
              </div>
              <h1 className="text-5xl font-black text-white tracking-wider drop-shadow-2xl">
                MovieFinder
              </h1>
              <p className="text-blue-100 mt-3 text-lg font-medium">Chào mừng trở lại!</p>
            </div>
          </div>

          {/* Form */}
          <div className="p-8 space-y-7">
            {/* Error Alert */}
            {error && (
              <div className="flex items-center gap-3 p-4 bg-red-600/20 border border-red-500/50 rounded-xl text-red-200 animate-shake">
                <AlertCircle className="w-6 h-6 flex-shrink-0" />
                <p className="text-sm font-medium">{error}</p>
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-6">
              {/* Username */}
              <div>
                <label className="flex items-center gap-2 text-blue-200 font-bold text-sm mb-2">
                  <User className="w-5 h-5" />
                  TÊN ĐĂNG NHẬP
                </label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-6 py-4 bg-white/10 border border-white/30 rounded-2xl text-white placeholder-blue-200/60 focus:outline-none focus:ring-4 focus:ring-blue-500/50 focus:border-blue-400 transition-all duration-300 placeholder:font-light"
                  placeholder="Nhập tên đăng nhập của bạn..."
                  disabled={loading}
                  autoFocus
                />
              </div>

              {/* Password */}
              <div className="relative">
                <label className="flex items-center gap-2 text-blue-200 font-bold text-sm mb-2">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M10 2a4 4 0 00-4 4v2H5a1 1 0 00-1 1v8a1 1 0 001 1h10a1 1 0 001-1V9a1 1 0 00-1-1h-1V6a4 4 0 00-4-4zM8 6a2 2 0 114 0v2H8V6z"/></svg>
                  MẬT KHẨU
                </label>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-6 py-4 pr-16 bg-white/10 border border-white/30 rounded-2xl text-white placeholder-blue-200/60 focus:outline-none focus:ring-4 focus:ring-blue-500/50 focus:border-blue-400 transition-all duration-300"
                  placeholder="Nhập mật khẩu..."
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-5 top-11 text-blue-300 hover:text-white transition"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || !username.trim() || !password}
                className="w-full py-5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:from-gray-600 disabled:to-gray-500 text-white font-black text-xl rounded-2xl shadow-2xl hover:shadow-blue-500/50 transform hover:scale-105 transition-all duration-300 flex items-center justify-center gap-3 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <div className="w-7 h-7 border-4 border-white/30 border-t-white rounded-full animate-spin" />
                    Đang đăng nhập...
                  </>
                ) : (
                  <>
                    <LogIn className="w-7 h-7" />
                    ĐĂNG NHẬP NGAY
                  </>
                )}
              </button>
            </form>

            {/* Links */}
            <div className="text-center space-y-4 pt-6 border-t border-white/10">
              <p className="text-blue-200">
                Chưa có tài khoản?{" "}
                <Link
                  to="/register"
                  className="font-bold text-yellow-400 hover:text-yellow-300 underline decoration-2 underline-offset-2 transition"
                >
                  Đăng ký miễn phí
                </Link>
              </p>
              <p className="text-blue-300 text-sm">
                Bạn là quản trị viên?{" "}
                <Link
                  to="/login/admin"
                  className="font-bold text-red-400 hover:text-red-300 underline decoration-wavy"
                >
                  Đăng nhập Admin
                </Link>
              </p>
            </div>

            <p className="text-center text-blue-300/70 text-xs mt-8">
              © 2025 MovieFinder • Phim hay mỗi ngày
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}