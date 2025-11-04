// src/context/AuthContext.jsx
import { createContext, useContext, useEffect, useState } from "react";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [userSession, setUserSession] = useState(null);
  const [adminSession, setAdminSession] = useState(null);

  useEffect(() => {
    const userToken = localStorage.getItem("user_token");
    const adminToken = localStorage.getItem("admin_token");

    const user = userToken
      ? {
          token: userToken,
          username: localStorage.getItem("user_username"),
          role: "user",
        }
      : null;

    const admin = adminToken
      ? {
          token: adminToken,
          username: localStorage.getItem("admin_username"),
          role: "admin",
        }
      : null;

    setUserSession(user);
    setAdminSession(admin);
  }, []);

  const login = (role, token, username) => {
    if (role === "admin") {
      localStorage.setItem("admin_token", token);
      localStorage.setItem("admin_username", username);
      setAdminSession({ role, token, username });
    } else {
      localStorage.setItem("user_token", token);
      localStorage.setItem("user_username", username);
      setUserSession({ role, token, username });
    }
  };

  const logout = (role) => {
    if (role === "admin") {
      localStorage.removeItem("admin_token");
      localStorage.removeItem("admin_username");
      setAdminSession(null);
    } else {
      localStorage.removeItem("user_token");
      localStorage.removeItem("user_username");
      setUserSession(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        userSession,
        adminSession,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
