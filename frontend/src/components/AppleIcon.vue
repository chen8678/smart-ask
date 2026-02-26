<script setup lang="ts">
import { computed } from 'vue'
import { appleIcons, type AppleIconName } from '@/icons/apple'

interface Props {
  name: AppleIconName
  size?: number
  strokeWidth?: number
  spin?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 20,
  strokeWidth: 1.6,
  spin: false
})

const iconDef = computed(() => appleIcons[props.name])
</script>

<template>
  <svg
    v-if="iconDef"
    :width="size"
    :height="size"
    :viewBox="iconDef.viewBox"
    fill="none"
    stroke="currentColor"
    :stroke-width="strokeWidth"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="apple-icon"
    :class="{ 'apple-icon--spin': spin }"
  >
    <path
      v-for="(path, index) in iconDef.paths"
      :key="index"
      :d="path.d"
      :fill="path.fill || 'none'"
    />
  </svg>
  <svg
    v-else
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    :stroke-width="strokeWidth"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="apple-icon"
  >
    <circle cx="12" cy="12" r="9" />
    <path d="M9 12h6M12 9v6" />
  </svg>
</template>

<style scoped>
.apple-icon {
  display: inline-block;
}

.apple-icon--spin {
  animation: apple-spin 1.2s linear infinite;
}

@keyframes apple-spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>

