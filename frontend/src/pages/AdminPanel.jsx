import React, { useState, useEffect } from "react";

export default function AdminPanel() {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch("http://localhost:8000/api/admin/users", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) throw new Error("Không thể tải danh sách người dùng");
        const data = await res.json();
        setUsers(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  const handleRoleChange = async (userId, newRole) => {
    try {
      const token = localStorage.getItem("token");
      await fetch(`http://localhost:8000/api/admin/users/${userId}/role`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ role: newRole }),
      });
      setUsers(prev =>
        prev.map(u => (u.id === userId ? { ...u, role: newRole } : u))
      );
    } catch (err) {
      alert("Lỗi khi cập nhật vai trò!");
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
            <th className="px-4 py-2 text-left text-gray-600 dark:text-gray-300">Thao tác</th>
          </tr>
        </thead>
        <tbody>
          {users.map(u => (
            <tr
              key={u.id}
              className="border-t border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              <td className="px-4 py-2 text-gray-700 dark:text-gray-200">{u.username}</td>
              <td className="px-4 py-2 text-gray-700 dark:text-gray-200">{u.email || "—"}</td>
              <td className="px-4 py-2 text-gray-700 dark:text-gray-200">{u.role}</td>
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
