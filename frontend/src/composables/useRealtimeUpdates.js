import { ref, onBeforeUnmount } from "vue";
import api from "../api";

export function useRealtimeUpdates(handler) {
  const wsRef = ref(null);
  const isReady = ref(false);
  let reconnectTimer = null;

  function buildWsUrl() {
    const token = localStorage.getItem("access") || "";
    const base = new URL(api.defaults.baseURL || window.location.origin);
    const wsProto = base.protocol === "https:" ? "wss:" : "ws:";
    const wsHost = base.host;
    const wsPath = base.pathname.replace(/\/api\/?$/, "");
    const cleanedPath = wsPath.endsWith("/") ? wsPath.slice(0, -1) : wsPath;
    return `${wsProto}//${wsHost}${cleanedPath}/ws/updates/?token=${token}`;
  }

  function scheduleReconnect() {
    if (reconnectTimer) return;
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null;
      connect();
    }, 2000);
  }

  function connect() {
    if (wsRef.value) {
      wsRef.value.close();
      wsRef.value = null;
    }
    isReady.value = false;
    try {
      wsRef.value = new WebSocket(buildWsUrl());
    } catch (err) {
      console.error("Realtime Verbindung fehlgeschlagen", err);
      scheduleReconnect();
      return;
    }
    wsRef.value.onopen = () => {
      isReady.value = true;
    };
    wsRef.value.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload && typeof handler === "function") {
          handler(payload);
        }
      } catch (err) {
        console.error("Konnte Echtzeit-Event nicht verarbeiten", err);
      }
    };
    wsRef.value.onclose = () => {
      isReady.value = false;
      scheduleReconnect();
    };
    wsRef.value.onerror = () => {
      isReady.value = false;
      scheduleReconnect();
    };
  }

  onBeforeUnmount(() => {
    if (reconnectTimer) clearTimeout(reconnectTimer);
    if (wsRef.value) {
      wsRef.value.close();
    }
  });

  return {
    connect,
    isReady,
  };
}
