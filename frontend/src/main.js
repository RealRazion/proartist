import { createApp } from "vue";
import router from "./router";
import App from "./App.vue";
import "./assets/styles.css";

const app = createApp(App);
app.use(router);
app.mount("#app");

// Theme init
const saved = localStorage.getItem("theme");
if (saved === "dark" || saved === "light") {
	document.documentElement.classList.toggle("dark", saved === "dark");
} else {
	const prefersDark = typeof window !== "undefined" && window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
	document.documentElement.classList.toggle("dark", prefersDark);
}
