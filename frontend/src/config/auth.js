// services/auth.js
export const login = async (username, password) => {
  const res = await fetch("http://localhost:8000/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json();
  if (res.ok) {
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("role", data.role);
  }
  return data;
};
