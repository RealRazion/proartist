<template>
  <div></div>
</template>

<script>
export default {
  name: "ArturRedirect",
  mounted() {
    // Resolve backend URL from environment or fallback
    let backendUrl = (import.meta.env.VITE_API_BASE_URL || "").trim();
    if (!backendUrl) {
      backendUrl = "https://proartist.onrender.com";
    }
    // Remove /api/ suffix if present
    backendUrl = backendUrl.replace(/\/api\/?$/, "");
    
    // Navigate to the Artur page on backend
    const path = this.$route.path;
    window.location.href = `${backendUrl}${path}`;
  },
};
</script>
