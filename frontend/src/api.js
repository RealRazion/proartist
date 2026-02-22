import axios from "axios";
import { useToast } from "./composables/useToast";

const baseURL =
  (import.meta.env.VITE_API_BASE_URL && import.meta.env.VITE_API_BASE_URL.trim()) ||
  "http://127.0.0.1:8000/api/";

const api = axios.create({ baseURL });
const { showToast } = useToast();
let lastToastAt = 0;

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config || {};
    const status = error?.response?.status;

    if (status === 401 && !original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem("refresh");
      if (!refresh) {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        return Promise.reject(error);
      }
      try {
        const { data } = await axios.post(`${baseURL}token/refresh/`, { refresh });
        localStorage.setItem("access", data.access);
        original.headers = original.headers || {};
        original.headers.Authorization = `Bearer ${data.access}`;
        return api(original);
      } catch (refreshError) {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        return Promise.reject(refreshError);
      }
    }

    if (status && status !== 401) {
      const now = Date.now();
      if (now - lastToastAt > 1200) {
        const message =
          error?.response?.data?.detail ||
          error?.response?.data?.message ||
          `Fehler (${status})`;
        showToast(message, "error");
        lastToastAt = now;
      }
    }

    if (!status) {
      const now = Date.now();
      if (now - lastToastAt > 1200) {
        showToast("Netzwerkfehler. Bitte Verbindung pruefen.", "error");
        lastToastAt = now;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
