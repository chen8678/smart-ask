<template>
  <div
    class="brand-mark"
    :class="{ 'brand-mark--flat': !padded, 'brand-mark--circle': circular }"
    :style="{
      width: `${size}px`,
      height: `${size}px`,
      borderRadius: circular ? `${size}px` : `${Math.round(size * 0.35)}px`
    }"
  >
    <img :src="logo" alt="智库通 Logo" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import LogoImage from '@/logo/Logo.png'

const props = withDefaults(
  defineProps<{
    size?: number
    padded?: boolean
    circular?: boolean
  }>(),
  {
    size: 56,
    padded: true,
    circular: false
  }
)

const padded = computed(() => props.padded)
const circular = computed(() => props.circular)
const size = computed(() => props.size)
const logo = LogoImage
</script>

<style scoped>
.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: transparent;
  border: none;
  box-shadow: none;
}

.brand-mark--flat {
  background: transparent;
  border: none;
  box-shadow: none;
}

.brand-mark.padded {
  padding: 10px;
}

.brand-mark img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.brand-mark--circle {
  border-radius: 999px !important;
}
</style>

