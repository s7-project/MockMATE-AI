
import axios from "axios";

// FastAPI backend URL
const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

// Axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Register new user
export const registerUser = async (userData) => {
  const response = await api.post(
    "/auth/register",
    userData
  );

  return response.data;
};

// Login user
export const loginUser = async (credentials) => {
  const response = await api.post(
    "/auth/login",
    credentials
  );

  return response.data;
};

// Get logged-in user profile
export const getCurrentUser = async (token) => {
  const response = await api.get(
    "/auth/me",
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};

export default api;
