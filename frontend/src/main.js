import { createApp } from "vue";
import router from "./router";
import App from "./App.vue";
import "./assets/styles.css";

const app = createApp(App);
app.use(router);
app.mount("#app");

// Theme init (UNYQ Studio defaults to dark mode)
const saved = localStorage.getItem("theme");
const isDark = saved === "light" ? false : true;
document.documentElement.classList.toggle("dark", isDark);
document.documentElement.classList.toggle("light", !isDark);
document.documentElement.style.colorScheme = isDark ? "only dark" : "only light";

