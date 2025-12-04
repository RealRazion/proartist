import { reactive } from "vue";

const state = reactive({
  message: "",
  type: "info",
  visible: false,
  timeout: null,
});

export function useToast() {
  function showToast(message, type = "info", duration = 2500) {
    clearTimeout(state.timeout);
    state.message = message;
    state.type = type;
    state.visible = true;
    state.timeout = setTimeout(() => (state.visible = false), duration);
  }
  function hideToast() {
    clearTimeout(state.timeout);
    state.visible = false;
  }
  return { toast: state, showToast, hideToast };
}
