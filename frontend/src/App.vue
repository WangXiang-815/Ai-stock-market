<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand">
        <div class="logo-box">▣</div>
        <span>Stock Predictor</span>
      </div>

      <nav class="nav-links">
        <RouterLink to="/dashboard">Dashboard</RouterLink>
        <RouterLink to="/chat">AI Chat</RouterLink>
      </nav>
    </header>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: #f7f7f8;
}

.topbar {
  height: 64px;
  background: #f4b51d;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  color: white;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 30px;
  font-weight: 600;
}

.logo-box {
  font-size: 22px;
}

.nav-links {
  display: flex;
  gap: 24px;
}

.nav-links a {
  color: white;
  text-decoration: none;
  font-weight: 600;
}

.nav-links a.router-link-active {
  border-bottom: 2px solid white;
}

.main-content {
  padding: 24px;
}
</style>