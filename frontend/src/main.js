import { createApp } from "vue";
import router from "./router";
import App from "./App.vue";
import "./assets/styles.css";

const app = createApp(App);
app.use(router);
app.mount("#app");

// Theme init
const saved = localStorage.getItem("theme");
if (saved === "dark") document.documentElement.classList.add("dark");
