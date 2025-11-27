// src/pages/admin/AdminPanel.jsx
import React, { useState, useEffect } from "react";
import { Loader2, RefreshCcw, Shield, UserCheck, UserX, Crown } from "lucide-react";

export default function AdminPanel() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updating, setUpdating] = useState(false);

  const adminToken = localStorage.getItem("admin_token");
  const currentAdmin = localStorage.getItem("admin_username");

  const fetchUsers = async () => {
    if (!adminToken) {
      setError("Thiếu quyền truy cập quản trị!");
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError("");

      const res = await fetch("http://localhost:8000/api/admin/users", {
        headers: {
          Authorization: `Bearer ${adminToken}`,
          "Content-Type": "application/json",
        },
      });

      if (!res.ok) throw new Error(`Lỗi ${res.status}: Không thể tải dữ liệu`);

      const data = await res.json();
      const normalized = data.map(u => ({
        ...u,
        is_active: u.is_active ?? true,
      }));

      setUsers(normalized);
    } catch (err) {
      setError(err.message);
      console.error("Fetch users error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [adminToken]);

  const handleRoleChange = async (userId, newRole) => {
    if (!adminToken) return alert("Không có quyền!");

    try {
      setUpdating(true);
      const res = await fetch(`http://localhost:8000/api/admin/users/${userId}/role`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${adminToken}`,
        },
        body: JSON.stringify({ role: newRole }),
      });

      if (!res.ok) throw new Error("Cập nhật thất bại");

      setUsers(prev => prev.map(u => u.id === userId ? { ...u, role: newRole } : u));
    } catch (err) {
      alert(err.message);
    } finally {
      setUpdating(false);
    }
  };

  const handleToggleActive = async (userId, currentStatus, username) => {
    if (username === currentAdmin) {
      alert("Không thể khóa tài khoản Admin đang đăng nhập!");
      return;
    }

    const action = currentStatus ? "khóa" : "kích hoạt lại";
    if (!confirm(`Bạn có chắc muốn ${action} tài khoản "${username}"?`)) return;

    try {
      setUpdating(true);
      const res = await fetch(`http://localhost:8000/api/admin/users/${userId}/active`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${adminToken}`,
        },
        body: JSON.stringify({ is_active: !currentStatus }),
      });

      if (!res.ok) throw new Error("Cập nhật trạng thái thất bại");

      setUsers(prev => prev.map(u => u.id === userId ? { ...u, is_active: !currentStatus } : u));
    } catch (err) {
      alert(err.message);
    } finally {
      setUpdating(false);
    }
  };

  // Loading & Error
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 text-gray-400">
        <Loader2 className="w-12 h-12 animate-spin mb-4" />
        <p className="text-lg">Đang tải danh sách người dùng...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-20">
        <p className="text-red-400 text-xl font-bold mb-4">Lỗi</p>
        <p className="text-gray-400">{error}</p>
        <button
          onClick={fetchUsers}
          className="mt-6 px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-xl text-white font-medium transition"
        >
          Thử lại
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-black bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Quản Lý Người Dùng
          </h1>
          <p className="text-gray-400 mt-2">Tổng cộng: <span className="font-bold text-white">{users.length}</span> tài khoản</p>
        </div>
        <button
          onClick={fetchUsers}
          disabled={updating}
          className="flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl font-bold text-white shadow-lg hover:shadow-purple-500/50 hover:scale-105 transition-all disabled:opacity-70"
        >
          <RefreshCcw className={`w-5 h-5 ${updating ? "animate-spin" : ""}`} />
          Làm mới dữ liệu
        </button>
      </div>

      {/* Table */}
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-3xl border border-gray-800 overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border-b border-gray-800">
                <th className="px-8 py-5 text-left text-sm font-bold text-gray-300">Tên đăng nhập</th>
                <th className="px-8 py-5 text-left text-sm font-bold text-gray-300">Email</th>
                <th className="px-8 py-5 text-center text-sm font-bold text-gray-300">Vai trò</th>
                <th className="px-8 py-5 text-center text-sm font-bold text-gray-300">Trạng thái</th>
                <th className="px-8 py-5 text-center text-sm font-bold text-gray-300">Hành động</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr
                  key={user.id}
                  className="border-b border-gray-800 hover:bg-gray-800/50 transition-all duration-200"
                >
                  {/* Username */}
                  <td className="px-8 py-6">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center font-bold text-white shadow-lg">
                        {user.username.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <p className="font-semibold text-white">{user.username}</p>
                        {user.username === currentAdmin && (
                          <span className="text-xs text-yellow-400 font-bold">★ Bạn đang đăng nhập</span>
                        )}
                      </div>
                    </div>
                  </td>

                  {/* Email */}
                  <td className="px-8 py-6 text-gray-400">
                    {user.email || "—"}
                  </td>

                  {/* Role */}
                  <td className="px-8 py-6 text-center">
                    <select
                      value={user.role}
                      onChange={(e) => handleRoleChange(user.id, e.target.value)}
                      disabled={updating || user.username === currentAdmin}
                      className={`px-4 py-2 rounded-xl font-bold text-sm transition-all ${
                        user.role === "admin"
                          ? "bg-gradient-to-r from-orange-600 to-red-600 text-white"
                          : user.role === "editor"
                          ? "bg-gradient-to-r from-cyan-600 to-blue-600 text-white"
                          : "bg-gray-700 text-gray-300"
                      } cursor-pointer focus:ring-4 focus:ring-purple-500/30`}
                    >
                      <option value="user">User</option>
                      <option value="editor">Editor</option>
                      <option value="admin">Admin</option>
                    </select>
                  </td>

                  {/* Status */}
                  <td className="px-8 py-6 text-center">
                    <button
                      onClick={() => handleToggleActive(user.id, user.is_active, user.username)}
                      disabled={updating || user.username === currentAdmin}
                      className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-full font-bold text-sm transition-all shadow-lg ${
                        user.is_active
                          ? "bg-emerald-600 hover:bg-emerald-700 text-white shadow-emerald-900/50"
                          : "bg-rose-600 hover:bg-rose-700 text-white shadow-rose-900/50"
                      } disabled:opacity-50`}
                    >
                      {user.is_active ? (
                        <>
                          <UserCheck className="w-4 h-4" />
                          Hoạt động
                        </>
                      ) : (
                        <>
                          <UserX className="w-4 h-4" />
                          Bị khóa
                        </>
                      )}
                    </button>
                  </td>

                  {/* Action Icons */}
                  <td className="px-8 py-6 text-center">
                    <div className="flex justify-center gap-3">
                      {user.role === "admin" && (
                        <Crown className="w-6 h-6 text-yellow-500" title="Quyền Admin cao nhất" />
                      )}
                      {user.username === currentAdmin && (
                        <Shield className="w-6 h-6 text-purple-400" title="Tài khoản đang đăng nhập" />
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}