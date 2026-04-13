import axios from "axios";
import { useToast } from "./composables/useToast";

function normalizeBaseUrl(value) {
  let url = (value || "").trim();
  if (!url) return "http://127.0.0.1:8000/api/";
  if (!/\/api(\/|$)/i.test(url)) {
    url = url.replace(/\/+$/, "");
    url = `${url}/api/`;
    return url;
  }
  if (!url.endsWith("/")) url += "/";
  return url;
}

const baseURL = normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL);

const api = axios.create({ baseURL });
const { showToast } = useToast();
let lastToastAt = 0;
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function extractApiErrorMessage(error) {
  const data = error?.response?.data;
  if (!data) return null;
  if (typeof data === "string") return data;
  if (Array.isArray(data)) return data.filter(Boolean).join(" ");
  if (data.detail) return data.detail;
  if (data.message) return data.message;

  const fieldMessages = [];
  Object.entries(data).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      fieldMessages.push(value.filter(Boolean).join(" "));
    } else if (typeof value === "object" && value !== null) {
      const nested = Object.values(value)
        .flatMap((item) => (Array.isArray(item) ? item : [item]))
        .filter((item) => typeof item === "string")
        .join(" ");
      if (nested) fieldMessages.push(nested);
    } else if (typeof value === "string") {
      fieldMessages.push(value);
    }
  });
  return fieldMessages.filter(Boolean).join(" ") || null;
}

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

    if (status >= 500 && status < 600 && !original._retryServer && original.method === "get") {
      original._retryServer = true;
      await sleep(600);
      return api(original);
    }

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
        const message = extractApiErrorMessage(error) || `Fehler (${status})`;
        showToast(message, "error");
        lastToastAt = now;
      }
    }

    if (!status) {
      const now = Date.now();
      if (now - lastToastAt > 1200) {
        showToast("Netzwerkfehler. Bitte Verbindung prüfen.", "error");
        lastToastAt = now;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
