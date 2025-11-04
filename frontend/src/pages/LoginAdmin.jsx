import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

export default function LoginAdmin() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const res = await fetch("http://localhost:8000/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Đăng nhập thất bại");

      if (data.role !== "admin") {
        throw new Error("Tài khoản này không có quyền Admin!");
      }

      localStorage.removeItem("user_token");
      localStorage.removeItem("user_username");

      localStorage.setItem("admin_token", data.access_token);
      localStorage.setItem("admin_username", data.username);
      alert("Đăng nhập thành công (Admin)!");
      
      navigate("/admin");
      window.location.reload();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-red-50 to-red-100 dark:from-gray-900 dark:to-gray-800">
      <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-8 w-full max-w-md border-t-4 border-red-500">
        <h2 className="text-2xl font-bold text-center text-red-600 mb-6">
          🛡️ Đăng nhập Quản trị viên
        </h2>

        {error && <p className="text-red-500 text-sm text-center mb-3">{error}</p>}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm mb-1">Tên đăng nhập</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full p-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
              required
            />
          </div>

          <div>
            <label className="block text-sm mb-1">Mật khẩu</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-2 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-red-600 text-white py-2 rounded-lg hover:bg-red-700 transition"
          >
            Đăng nhập Admin
          </button>
        </form>

        <p className="text-center text-sm mt-4 text-gray-600 dark:text-gray-400">
          👤 <Link to="/login/user" className="text-blue-600 hover:underline">Đăng nhập User</Link>
        </p>
      </div>
    </div>
  );
}
