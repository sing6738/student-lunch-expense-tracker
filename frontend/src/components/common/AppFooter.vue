<template>
  <footer class="app-footer">
    <div class="footer-content">
      <p class="footer-copy">🍱 LunchTrack • เพื่อนคู่ใจมื้อเที่ยงนักเรียน</p>
      <p class="footer-sub">&copy; 2026 Student Lunch Expense Tracker</p>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  text-align: center;
  padding: 1.5rem 1rem;
  color: var(--text-muted);
  font-size: 0.8rem;
  margin-top: auto;
  border-top: 1px solid var(--surface-border);
  background-color: transparent;
  display: none;
}

@media (min-width: 768px) {
  .app-footer {
    display: block;
  }
}

.footer-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.footer-copy {
  font-weight: 500;
  color: var(--text-main);
  margin: 0;
}

.footer-sub {
  margin: 0;
  font-size: 0.75rem;
}
</style>
