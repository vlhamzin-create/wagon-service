<template>
  <div class="dashboard-layout">
    <header class="dashboard-layout__header">
      <h1 class="dashboard-layout__title">Дашборд</h1>
      <div class="dashboard-layout__filter">
        <slot name="filter" />
      </div>
    </header>

    <main class="dashboard-layout__content">
      <slot name="content" />
    </main>

    <footer class="dashboard-layout__footer">
      <slot name="footer" />
    </footer>
  </div>
</template>

<style scoped>
.dashboard-layout {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-layout__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.dashboard-layout__title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.dashboard-layout__content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.dashboard-layout__footer {
  font-size: 13px;
  color: #999;
}
</style>
