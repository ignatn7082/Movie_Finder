import React, { useState, useEffect } from "react";

export default function AdminPanel() {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // 🔹 Dùng admin_token thay vì token chung
  const adminToken = localStorage.getItem("admin_token");

  useEffect(() => {
    const fetchUsers = async () => {
      try {
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
          throw new Error(`Không thể tải danh sách người dùng (${res.status}): ${err}`);
        }

        const data = await res.json();
        setUsers(data);
      } catch (err) {
        console.error(err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, [adminToken]);

  const handleRoleChange = async (userId, newRole) => {
    try {
      if (!adminToken) throw new Error("Thiếu token quản trị!");

      const res = await fetch(`http://localhost:8000/api/admin/users/${userId}/role`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${adminToken}`,
        },
        body: JSON.stringify({ role: newRole }),
      });

      if (!res.ok) throw new Error("Không thể cập nhật vai trò!");

      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, role: newRole } : u))
      );
    } catch (err) {
      alert(err.message);
    }
  };

  const handleToggleActive = async (userId, newStatus) => {
    try {
      const token = localStorage.getItem("admin_token");
      await fetch(`http://localhost:8000/api/admin/users/${userId}/active`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ is_active: newStatus }),
      });
      setUsers((prev) =>
        prev.map((u) =>
          u.id === userId ? { ...u, is_active: newStatus } : u
        )
      );
    } catch {
      alert("Lỗi khi thay đổi trạng thái tài khoản!");
    }
  };


  if (loading) return <p className="text-gray-500">Đang tải...</p>;
  if (error) return <p className="text-red-500">{error}</p>;

  return (
    <div className="p-6 bg-white dark:bg-gray-900 rounded-xl shadow-lg">
      <h1 className="text-2xl font-bold mb-6 text-gray-800 dark:text-gray-100">
        🎬 Quản lý người dùng
      </h1>

      <table className="min-w-full border border-gray-200 dark:border-gray-700">
        <thead className="bg-gray-100 dark:bg-gray-800">
        <tr>
          <th className="px-4 py-2 text-left text-gray-600 dark:text-gray-300">Tên</th>
          <th className="px-4 py-2 text-left text-gray-600 dark:text-gray-300">Email</th>
          <th className="px-4 py-2 text-left text-gray-600 dark:text-gray-300">Vai trò</th>
          <th className="px-4 py-2 text-left text-gray-600 dark:text-gray-300">Trạng thái</th>
          <th className="px-4 py-2 text-left text-gray-600 dark:text-gray-300">Thao tác</th>
        </tr>
      </thead>
      <tbody>
        {users.map((u) => (
          <tr
            key={u.id}
            className="border-t border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800"
          >
            <td className="px-4 py-2 text-gray-700 dark:text-gray-200">{u.username}</td>
            <td className="px-4 py-2 text-gray-700 dark:text-gray-200">{u.email || "—"}</td>
            <td className="px-4 py-2 text-gray-700 dark:text-gray-200">{u.role}</td>
        
            {/*  Trạng thái active */}
            <td className="px-4 py-2">
              <button
                onClick={() => handleToggleActive(u.id, !u.is_active)}
                className={`px-3 py-1 rounded text-sm ${
                  u.is_active ? "bg-green-500 text-white" : "bg-red-500 text-white"
                }`}
              >
                {u.is_active ? "Đang hoạt động" : "Bị khóa"}
              </button>
            </td>
              
            {/* Vai trò */}
            <td className="px-4 py-2">
              <select
                className="border border-gray-300 rounded-md px-2 py-1 dark:bg-gray-800 dark:text-gray-100"
                value={roles[u.id] || u.role}
                onChange={(e) => handleRoleChange(u.id, e.target.value)}
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
