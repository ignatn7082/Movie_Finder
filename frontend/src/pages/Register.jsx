// src/pages/auth/Register.jsx
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Mail, User, Lock, CheckCircle, AlertCircle, Sparkles, Eye, EyeOff } from "lucide-react";

export default function Register() {
  const [formData, setFormData] = useState({
    email: "",
    username: "",
    password: "",
    confirm: ""
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError("");
  };

  const validateForm = () => {
    const { email, username, password, confirm } = formData;

    if (!email.includes("@") || !email.includes(".")) {
      setError("Email không hợp lệ!");
      return false;
    }
    if (username.length < 3) {
      setError("Tên đăng nhập phải ít nhất 3 ký tự!");
      return false;
    }
    if (password.length < 6) {
      setError("Mật khẩu phải ít nhất 6 ký tự!");
      return false;
    }
    if (password !== confirm) {
      setError("Mật khẩu xác nhận không khớp!");
      return false;
    }
    return true;
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const res = await fetch("http://localhost:8000/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: formData.email.trim(),
          username: formData.username.trim(),
          password: formData.password
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Đăng ký thất bại. Vui lòng thử lại!");
      }

      setSuccess("Đăng ký thành công! Chuyển hướng đến đăng nhập...");
      
      setTimeout(() => {
        navigate("/login/user", { replace: true });
      }, 2000);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-600 via-pink-500 to-orange-400 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-black/50 backdrop-blur-3xl" />
        <div className="absolute top-0 left-0 w-96 h-96 bg-purple-600/40 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-pink-600/40 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-orange-500/30 rounded-full blur-3xl animate-ping" />
      </div>

      {/* Register Card */}
      <div className="relative z-10 w-full max-w-lg mx-4">
        <div className="bg-white/10 backdrop-blur-2xl rounded-3xl shadow-2xl border border-white/20 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-10 text-center relative">
            <div className="absolute inset-0 bg-black/20" />
            <div className="relative z-10">
              <div className="flex justify-center mb-6">
                <div className="p-6 bg-white/20 backdrop-blur-md rounded-full shadow-2xl animate-bounce">
                  <Sparkles className="w-16 h-16 text-white" />
                </div>
              </div>
              <h1 className="text-5xl font-black text-white tracking-widest drop-shadow-2xl">
                JOIN MOVIEFINDER
              </h1>
              <p className="text-white/90 mt-3 text-lg font-medium">Tham gia cộng đồng phim hay ngay hôm nay!</p>
            </div>
          </div>

          {/* Form */}
          <div className="p-8 space-y-6">
            {/* Success Message */}
            {success && (
              <div className="flex items-center gap-3 p-5 bg-green-600/20 border border-green-500/50 rounded-2xl text-green-200 animate-bounce">
                <CheckCircle className="w-8 h-8 flex-shrink-0" />
                <p className="font-bold text-lg">{success}</p>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="flex items-center gap-3 p-5 bg-red-600/20 border border-red-500/50 rounded-2xl text-red-200 animate-shake">
                <AlertCircle className="w-8 h-8 flex-shrink-0" />
                <p className="font-bold">{error}</p>
              </div>
            )}

            <form onSubmit={handleRegister} className="space-y-6">
              {/* Email */}
              <div>
                <label className="flex items-center gap-2 text-white font-bold text-sm mb-3">
                  <Mail className="w-5 h-5" />
                  EMAIL
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-6 py-4 bg-white/10 border border-white/30 rounded-2xl text-white placeholder-white/50 focus:outline-none focus:ring-4 focus:ring-purple-500/50 focus:border-purple-400 transition-all duration-300"
                  placeholder="you@example.com"
                  disabled={loading}
                  required
                />
              </div>

              {/* Username */}
              <div>
                <label className="flex items-center gap-2 text-white font-bold text-sm mb-3">
                  <User className="w-5 h-5" />
                  TÊN ĐĂNG NHẬP
                </label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className="w-full px-6 py-4 bg-white/10 border border-white/30 rounded-2xl text-white placeholder-white/50 focus:outline-none focus:ring-4 focus:ring-purple-500/50 focus:border-purple-400 transition-all duration-300"
                  placeholder="Tên đẹp của bạn..."
                  disabled={loading}
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
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full px-6 py-4 pr-16 bg-white/10 border border-white/30 rounded-2xl text-white placeholder-white/50 focus:outline-none focus:ring-4 focus:ring-purple-500/50 focus:border-purple-400 transition-all duration-300"
                  placeholder="Mật khẩu mạnh (tối thiểu 6 ký tự)"
                  disabled={loading}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-5 top-11 text-white/70 hover:text-white transition"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>

              {/* Confirm Password */}
              <div className="relative">
                <label className="flex items-center gap-2 text-white font-bold text-sm mb-3">
                  <Lock className="w-5 h-5" />
                  XÁC NHẬN MẬT KHẨU
                </label>
                <input
                  type={showConfirm ? "text" : "password"}
                  name="confirm"
                  value={formData.confirm}
                  onChange={handleChange}
                  className="w-full px-6 py-4 pr-16 bg-white/10 border border-white/30 rounded-2xl text-white placeholder-white/50 focus:outline-none focus:ring-4 focus:ring-purple-500/50 focus:border-purple-400 transition-all duration-300"
                  placeholder="Nhập lại mật khẩu"
                  disabled={loading}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowConfirm(!showConfirm)}
                  className="absolute right-5 top-11 text-white/70 hover:text-white transition"
                >
                  {showConfirm ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-6 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:from-gray-600 disabled:to-gray-500 text-white font-black text-2xl rounded-2xl shadow-2xl hover:shadow-purple-500/50 transform hover:scale-105 transition-all duration-300 flex items-center justify-center gap-4 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <div className="w-8 h-8 border-4 border-white/30 border-t-white rounded-full animate-spin" />
                    Đang tạo tài khoản...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-8 h-8" />
                    TẠO TÀI KHOẢN NGAY
                  </>
                )}
              </button>
            </form>

            {/* Login Link */}
            <div className="text-center pt-6 border-t border-white/10">
              <p className="text-white/80 text-lg">
                Đã có tài khoản?{" "}
                <Link
                  to="/login"
                  className="font-black text-yellow-400 hover:text-yellow-300 underline decoration-2 underline-offset-4 transition"
                >
                  Đăng nhập ngay
                </Link>
              </p>
            </div>

            <p className="text-center text-white/60 text-xs mt-8">
              © 2025 MovieFinder • Phim hay mỗi ngày • Miễn phí vĩnh viễn
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}