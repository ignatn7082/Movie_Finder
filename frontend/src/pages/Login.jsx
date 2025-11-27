// src/pages/auth/Login.jsx  ← Chỉ cần 1 file này thôi!
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { 
  User, 
  Eye, 
  EyeOff, 
  LogIn, 
  Sparkles, 
  AlertCircle, 
  Lock,
  Shield,
  CheckCircle2 
} from "lucide-react";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password) {
      setError("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

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

      // XÓA HẾT TOKEN CŨ
      localStorage.removeItem("user_token");
      localStorage.removeItem("user_username");
      localStorage.removeItem("admin_token");
      localStorage.removeItem("admin_username");

      // TỰ ĐỘNG ĐIỀU HƯỚNG THEO ROLE
      if (data.role === "admin") {
        localStorage.setItem("admin_token", data.access_token);
        localStorage.setItem("admin_username", data.username);
        setSuccess("Chào mừng Admin!  Chào mừng trở lại");
        setTimeout(() => navigate("/", { replace: true }), 1500);
      } else {
        // user hoặc editor
        localStorage.setItem("user_token", data.access_token);
        localStorage.setItem("user_username", data.username);
        setSuccess("Đăng nhập thành công! Chào mừng trở lại");
        setTimeout(() => navigate("/", { replace: true }), 1500);
      }

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 relative overflow-hidden">
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
          <div className="bg-gradient-to-r from-indigo-600 to-purple-700 p-10 text-center relative">
            <div className="absolute inset-0 bg-black/20" />
            <div className="relative z-10">
              <div className="flex justify-center mb-6">
                <div className="p-6 bg-white/20 backdrop-blur-md rounded-full shadow-2xl animate-bounce">
                  <Sparkles className="w-16 h-16 text-white" />
                </div>
              </div>
              <h1 className="text-5xl font-black text-white tracking-widest drop-shadow-2xl">
                MOVIEFINDER
              </h1>
              <p className="text-white/90 mt-3 text-lg font-medium">
                Đăng nhập để tiếp tục
              </p>
            </div>
          </div>

          {/* Success Message */}
          {success && (
            <div className="mx-8 mt-6 flex items-center gap-3 p-5 bg-green-600/20 border border-green-500/50 rounded-2xl text-green-200 animate-bounce">
              <CheckCircle2 className="w-8 h-8 flex-shrink-0" />
              <p className="font-bold text-lg">{success}</p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mx-8 mt-6 flex items-center gap-3 p-5 bg-red-600/20 border border-red-500/50 rounded-2xl text-red-200 animate-shake">
              <AlertCircle className="w-8 h-8 flex-shrink-0" />
              <p className="font-bold">{error}</p>
            </div>
          )}

          {/* Form */}
          <div className="p-8 space-y-7">
            <form onSubmit={handleLogin} className="space-y-6">
              {/* Username */}
              <div>
                <label className="flex items-center gap-2 text-white font-bold text-sm mb-3">
                  <User className="w-5 h-5" />
                  TÊN ĐĂNG NHẬP
                </label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-6 py-4 bg-white/10 border border-white/30 rounded-2xl text-white placeholder-white/50 focus:outline-none focus:ring-4 focus:ring-purple-500/50 focus:border-purple-400 transition-all duration-300"
                  placeholder="Nhập tên đăng nhập..."
                  disabled={loading}
                  autoFocus
                  required
                />
              </div>

              {/* Password */}
              <div className="relative">
                <label className="flex items-center gap-2 text-white font-bold text-sm mb-3">
                  <Lock className="w-5 h-5" />
                  MẬT KHẨU
                </label>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-6 py-4 pr-16 bg-white/10 border border-white/30 rounded-2xl text-white placeholder-white/50 focus:outline-none focus:ring-4 focus:ring-purple-500/50 focus:border-purple-400 transition-all duration-300"
                  placeholder="Nhập mật khẩu..."
                  disabled={loading}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-5 top-11 text-white/70 hover:text-white transition"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || !username.trim() || !password}
                className="w-full py-6 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:from-gray-600 disabled:to-gray-500 text-white font-black text-2xl rounded-2xl shadow-2xl hover:shadow-purple-500/50 transform hover:scale-105 transition-all duration-300 flex items-center justify-center gap-4 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <div className="w-8 h-8 border-4 border-white/30 border-t-white rounded-full animate-spin" />
                    Đang đăng nhập...
                  </>
                ) : (
                  <>
                    <LogIn className="w-8 h-8" />
                    ĐĂNG NHẬP
                  </>
                )}
              </button>
            </form>

            {/* Footer Links */}
            <div className="text-center space-y-4 pt-6 border-t border-white/10">
              <p className="text-white/80 text-lg">
                Chưa có tài khoản?{" "}
                <Link to="/register" className="font-black text-yellow-400 hover:text-yellow-300 underline decoration-2">
                  Đăng ký miễn phí
                </Link>
              </p>
              <p className="text-white/60 text-sm flex items-center justify-center gap-2">
                <Shield className="w-4 h-4" />
                Admin? Dùng tài khoản admin để vào bảng điều khiển
              </p>
            </div>

            <p className="text-center text-white/60 text-xs mt-8">
              © 2025 MovieFinder • Phim hay mỗi ngày
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}