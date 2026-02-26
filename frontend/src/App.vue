<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
// Application shell only renders router-view
</script>

<style>
:root {
  --apple-background: #f5f5f7;
  --apple-surface: #ffffff;
  --apple-elevated: #f9fafc;
  --apple-border: rgba(0, 0, 0, 0.08);
  --apple-overlay: rgba(15, 15, 15, 0.03);
  --apple-glass: rgba(255, 255, 255, 0.45);
  --apple-text-primary: #1f1f1f;
  --apple-text-secondary: #6d6d72;
  --apple-text-tertiary: #8e8e93;
  --apple-brand-blue: #0a84ff;
  --apple-brand-blue-hover: #0060df;
  --apple-success: #30d158;
  --apple-warning: #ff9f0a;
  --apple-danger: #ff453a;
  --apple-card-radius: 24px;
  --apple-control-radius: 14px;
  --apple-pill-radius: 999px;
  --apple-font-family: 'SF Pro Display', 'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
  --apple-spacing-xs: 6px;
  --apple-spacing-sm: 12px;
  --apple-spacing-md: 18px;
  --apple-spacing-lg: 24px;
  --apple-chart-blue: #0a84ff;
  --apple-chart-blue-soft: rgba(10, 132, 255, 0.18);
  --apple-chart-green: #30d158;
  --apple-chart-green-soft: rgba(48, 209, 88, 0.18);
  --apple-chart-orange: #ff9500;
  --apple-chart-orange-soft: rgba(255, 149, 0, 0.18);
  --apple-chart-purple: #bf5af2;
  --apple-chart-purple-soft: rgba(191, 90, 242, 0.2);
  --apple-chart-grid: rgba(120, 120, 128, 0.25);
  --apple-chart-surface: rgba(10, 10, 15, 0.05);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: var(--apple-font-family);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--apple-text-primary);
  line-height: 1.6;
  background: var(--apple-background);
  min-height: 100vh;
}

body {
  margin: 0;
  background: var(--apple-background);
  color: var(--apple-text-primary);
}

::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.25);
  border-radius: 3px;
}

.ghost-btn {
  border-radius: var(--apple-pill-radius) !important;
  border: 1px solid rgba(0, 0, 0, 0.08) !important;
  background: rgba(255, 255, 255, 0.85) !important;
  color: var(--apple-text-primary) !important;
  padding: 0 18px !important;
  display: inline-flex !important;
  align-items: center;
  gap: 6px;
}

.ghost-btn:hover {
  background: rgba(242, 242, 247, 0.85) !important;
}

.el-card {
  border-radius: var(--apple-card-radius) !important;
  border: 1px solid var(--apple-border) !important;
  background: var(--apple-surface) !important;
  box-shadow: none !important;
  transition: border-color 0.2s ease, transform 0.2s ease !important;
}

.el-card:hover {
  border-color: rgba(0, 0, 0, 0.12) !important;
  transform: translateY(-2px);
}

.el-divider {
  border-top-color: var(--apple-border) !important;
}

.el-button {
  border-radius: var(--apple-pill-radius) !important;
  font-weight: 500 !important;
  border: 1px solid transparent !important;
  box-shadow: none !important;
  padding: 10px 20px !important;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease !important;
}

.el-button--primary {
  background: var(--apple-brand-blue) !important;
  border-color: var(--apple-brand-blue) !important;
  color: #fff !important;
}

.el-button--primary:hover {
  background: var(--apple-brand-blue-hover) !important;
  border-color: var(--apple-brand-blue-hover) !important;
}

.el-button--success {
  background: var(--apple-success) !important;
  border-color: var(--apple-success) !important;
  color: #fff !important;
}

.el-button--warning {
  background: var(--apple-warning) !important;
  border-color: var(--apple-warning) !important;
  color: var(--apple-text-primary) !important;
}

.el-button--danger {
  background: var(--apple-danger) !important;
  border-color: var(--apple-danger) !important;
  color: #fff !important;
}

.el-button--info,
.el-button--default {
  background: transparent !important;
  border-color: var(--apple-border) !important;
  color: var(--apple-text-primary) !important;
}

.el-button--info:hover,
.el-button--default:hover {
  border-color: var(--apple-brand-blue) !important;
  color: var(--apple-brand-blue) !important;
}

.el-button--text,
.el-button.is-text {
  background: transparent !important;
  border: none !important;
  color: var(--apple-brand-blue) !important;
  padding: 8px 12px !important;
}

.el-button--text:hover,
.el-button.is-text:hover {
  background: rgba(10, 132, 255, 0.08) !important;
}

.el-input__wrapper,
.el-select .el-input__wrapper,
.el-textarea__inner {
  border-radius: var(--apple-control-radius) !important;
  border: 1px solid var(--apple-border) !important;
  background: var(--apple-surface) !important;
  box-shadow: none !important;
}

.el-input__wrapper.is-focus,
.el-select .el-input.is-focus .el-input__wrapper,
.el-textarea__inner:focus {
  border-color: var(--apple-brand-blue) !important;
  box-shadow: 0 0 0 3px rgba(10, 132, 255, 0.1) !important;
}

.el-tag {
  border-radius: var(--apple-pill-radius) !important;
  border: 1px solid var(--apple-border) !important;
  background: transparent !important;
  color: var(--apple-text-secondary) !important;
}

.el-dialog {
  border-radius: 28px !important;
  padding: 12px 0 24px !important;
}

.el-dialog__header {
  padding: 24px 32px 12px !important;
  border-bottom: 1px solid var(--apple-border);
}

.el-dialog__body {
  padding: 20px 32px !important;
}

.el-dialog__footer {
  padding: 0 32px 24px !important;
  border-top: 1px solid var(--apple-border);
}

.el-table,
.el-table__header-wrapper,
.el-table__body-wrapper {
  background: transparent !important;
}

.el-table th,
.el-table td {
  border-bottom: 1px solid var(--apple-border) !important;
}

.el-table--border {
  border: 1px solid var(--apple-border) !important;
}

.el-message,
.el-notification {
  border-radius: 18px !important;
  border: 1px solid var(--apple-border) !important;
  box-shadow: none !important;
}

.el-empty {
  padding: 32px 16px !important;
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 1rem !important;
  }

  .header-controls {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-end;
  }

  .control-group {
    min-width: 120px;
  }
}
</style>

