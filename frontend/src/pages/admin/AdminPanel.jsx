import React, { useState, useEffect } from "react";
import { Loader2, RefreshCcw } from "lucide-react";

export default function AdminPanel() {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updating, setUpdating] = useState(false);

  // 🔹 Dùng admin_token thay vì token chung
  const adminToken = localStorage.getItem("admin_token");

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError("");

      if (!adminToken) {
        setError("Vui lòng đăng nhập với tài khoản admin!");
        setLoading(false);
        return;
      }

      const res = await fetch("http://localhost:8000/api/admin/users", {
        headers: {
          Authorization: `Bearer ${adminToken}`,
          "Content-Type": "application/json",
        },
      });

      if (!res.ok) {
        const err = await res.text();
        throw new Error(
          `Không thể tải danh sách người dùng (${res.status}): ${err}`
        );
      }

    const data = await res.json();
    const normalized = data.map((u) => ({
      ...u,
      is_active: u.is_active !== undefined ? u.is_active : true,
    }));

    setUsers(normalized);
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [adminToken]);

  const handleRoleChange = async (userId, newRole) => {
    try {
      setUpdating(true);
      if (!adminToken) throw new Error("Thiếu token quản trị!");

      const res = await fetch(
        `http://localhost:8000/api/admin/users/${userId}/role`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${adminToken}`,
          },
          body: JSON.stringify({ role: newRole }),
        }
      );

      if (!res.ok) throw new Error("Không thể cập nhật vai trò!");

      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, role: newRole } : u))
      );
    } catch (err) {
      alert(err.message);
    } finally {
      setUpdating(false);
    }
  };

const handleToggleActive = async (userId, newStatus, username) => {
  if (!adminToken) {
    alert("Thiếu token quản trị!");
    return;
  }

  // Chặn admin tự vô hiệu hóa chính mình
  const currentAdmin = localStorage.getItem("admin_username");
  if (username === currentAdmin) {
    alert("Không thể vô hiệu hóa tài khoản admin đang đăng nhập!");
    return;
  }

  const confirmAction = window.confirm(
    newStatus
      ? `Kích hoạt lại tài khoản "${username}"?`
      : `Vô hiệu hóa tài khoản "${username}"?`
  );
  if (!confirmAction) return;

  try {
    setUpdating(true);

    const res = await fetch(
      `http://localhost:8000/api/admin/users/${userId}/active`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${adminToken}`,
        },
        body: JSON.stringify({ is_active: newStatus }),
      }
    );

    if (!res.ok) {
      throw new Error("Không thể cập nhật trạng thái tài khoản!");
    }

    // Cập nhật ngay trên UI
    setUsers((prev) =>
      prev.map((u) =>
        u.id === userId ? { ...u, is_active: newStatus } : u
      )
    );
  } catch (err) {
    alert(err.message);
  } finally {
    setUpdating(false);
  }
};


  if (loading)
    return (
      <div className="flex justify-center items-center h-64 text-gray-400">
        <Loader2 className="animate-spin mr-2" /> Đang tải dữ liệu...
      </div>
    );

  if (error)
    return (
      <div className="text-center mt-10 text-red-400 font-medium">
        ⚠️ {error}
      </div>
    );

  return (
<div className="bg-[#0f172a] border border-gray-700 rounded-xl p-6 shadow-lg">
  <div className="flex justify-between items-center mb-6">
    <h1 className="text-xl font-bold text-blue-400 flex items-center gap-2">
      🎬 Quản lý người dùng
    </h1>
    <button
      onClick={fetchUsers}
      className="bg-gray-800 hover:bg-gray-700 px-3 py-1.5 rounded text-gray-200 text-sm transition"
    >
      Làm mới
    </button>
  </div>

  <table className="min-w-full border border-gray-700 rounded-lg overflow-hidden">
    <thead className="bg-gray-800 text-gray-300 text-sm uppercase">
      <tr>
        <th className="px-4 py-2 text-left">Tên</th>
        <th className="px-4 py-2 text-left">Email</th>
        <th className="px-4 py-2 text-left">Vai trò</th>
        <th className="px-4 py-2 text-left">Trạng thái</th>
        <th className="px-4 py-2 text-left">Thao tác</th>
      </tr>
    </thead>
   <tbody>
  {users.map((u) => (
    <tr
      key={u.id}
      className="border-t border-gray-700 hover:bg-gray-800 transition"
    >
      <td className="px-4 py-2 text-gray-200">{u.username}</td>
      <td className="px-4 py-2 text-gray-400">{u.email || "—"}</td>
      <td className="px-4 py-2 text-gray-300 capitalize">{u.role}</td>

      {/* Trạng thái */}
      <td className="px-4 py-2 text-center">
        <button
          onClick={() => handleToggleActive(u.id, !u.is_active)}
          className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold transition-all duration-200
            ${
              u.is_active
                ? "bg-emerald-600/90 hover:bg-emerald-700 text-white shadow-md shadow-emerald-900/40"
                : "bg-rose-600/90 hover:bg-rose-700 text-white shadow-md shadow-rose-900/40"
            }`}
          title={
            u.is_active
              ? "Tài khoản đang hoạt động. Nhấn để vô hiệu hóa."
              : "Tài khoản bị khóa. Nhấn để kích hoạt lại."
          }
        >
          <span
            className={`w-2.5 h-2.5 rounded-full ${
              u.is_active ? "bg-green-300" : "bg-red-300"
            }`}
          ></span>
          {u.is_active ? "Đang hoạt động" : "Bị khóa"}
        </button>
      </td>

      {/* Vai trò */}
      <td className="px-4 py-2">
        <select
          value={roles[u.id] || u.role}
          onChange={(e) => handleRoleChange(u.id, e.target.value)}
          className="border border-gray-600 bg-gray-800 text-gray-200 rounded-md px-2 py-1 text-sm focus:ring focus:ring-blue-500/30 focus:border-blue-400"
        >
          <option value="user">User</option>
          <option value="editor">Editor</option>
          <option value="admin">Admin</option>
        </select>
      </td>
    </tr>
  ))}
</tbody>

  </table>
</div>

  );
}
