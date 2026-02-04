<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { getTheme, initTheme, toggleTheme } from './theme'

const theme = ref('light')
const tipOpen = ref(false)

function syncTheme() {
  theme.value = getTheme()
}

onMounted(() => {
  initTheme()
  syncTheme()
})

function onToggleTheme() {
  toggleTheme()
  syncTheme()
  tipOpen.value = true
  window.setTimeout(() => (tipOpen.value = false), 1400)
}

const isDark = computed(() => theme.value === 'dark')
const themeAria = computed(() => (isDark.value ? 'Mudar para tema claro' : 'Mudar para tema escuro'))
const tooltipText = computed(() => (isDark.value ? 'Tema escuro (clique para claro)' : 'Tema claro (clique para escuro)'))

const linkBase =
  'inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium ' +
  'text-slate-700 hover:bg-slate-100 ' +
  'focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400 ' +
  'dark:text-slate-200 dark:hover:bg-white/10'

const linkActive = 'bg-slate-100 text-slate-900 dark:bg-white/10 dark:text-white'
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
    <header class="sticky top-0 z-10 border-b border-slate-200/70 bg-white/80 backdrop-blur dark:border-white/10 dark:bg-slate-950/70">
      <div class="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
        <!-- Brand -->
        <div class="flex items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-900 text-white dark:bg-white dark:text-slate-900">
              TI
            </div>
            <div class="leading-tight">
              <div class="text-sm font-semibold">Teste de Integração</div>
              <div class="text-xs text-slate-500 dark:text-slate-400">Operadoras & despesas</div>
            </div>
          </div>

          <!-- Toggle (mobile: fica à direita do brand) -->
          <div class="relative sm:hidden">
            <button
              type="button"
              @click="onToggleTheme"
              @mouseenter="tipOpen = true"
              @mouseleave="tipOpen = false"
              @focus="tipOpen = true"
              @blur="tipOpen = false"
              class="inline-flex h-11 w-11 items-center justify-center rounded-md border border-slate-200 bg-white text-slate-800 shadow-sm
                     transition-colors hover:bg-slate-50
                     focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400
                     dark:border-white/10 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800"
              :aria-label="themeAria"
              :title="themeAria"
              aria-describedby="tip-theme-mobile"
            >
              <Transition name="icon" mode="out-in">
                <svg
                  v-if="isDark"
                  key="sun-m"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="h-5 w-5"
                >
                  <circle cx="12" cy="12" r="4"></circle>
                  <path d="M12 2v2"></path><path d="M12 20v2"></path>
                  <path d="M4.93 4.93l1.41 1.41"></path><path d="M17.66 17.66l1.41 1.41"></path>
                  <path d="M2 12h2"></path><path d="M20 12h2"></path>
                  <path d="M4.93 19.07l1.41-1.41"></path><path d="M17.66 6.34l1.41-1.41"></path>
                </svg>

                <svg
                  v-else
                  key="moon-m"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="h-5 w-5"
                >
                  <path d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79z"></path>
                </svg>
              </Transition>
            </button>

            <Transition name="tip">
              <div
                v-if="tipOpen"
                id="tip-theme-mobile"
                role="tooltip"
                class="pointer-events-none absolute right-0 mt-2 max-w-[220px] rounded-md border border-slate-200 bg-white px-2 py-1 text-xs text-slate-700 shadow-md
                       dark:border-white/10 dark:bg-slate-900 dark:text-slate-200"
              >
                {{ tooltipText }}
              </div>
            </Transition>
          </div>
        </div>

        <!-- Nav + Toggle (desktop) -->
        <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-3">
          <nav class="flex flex-wrap items-center justify-center gap-1">
            <!-- HOME -->
            <RouterLink
              to="/"
              :class="linkBase"
              :active-class="linkActive"
              :exact-active-class="linkActive"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="h-4 w-4">
                <path d="M3 10.5L12 3l9 7.5"></path>
                <path d="M5 10v10h14V10"></path>
              </svg>
              Home
            </RouterLink>

            <!-- OPERADORAS -->
            <RouterLink
              to="/operadoras"
              :class="linkBase"
              :active-class="linkActive"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="h-4 w-4">
                <circle cx="11" cy="11" r="7"></circle>
                <path d="M21 21l-4.3-4.3"></path>
              </svg>
              Operadoras
            </RouterLink>

            <!-- DASHBOARD -->
            <RouterLink
              to="/dashboard"
              :class="linkBase"
              :active-class="linkActive"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="h-4 w-4">
                <path d="M3 3v18h18"></path>
                <path d="M7 14v4"></path>
                <path d="M12 10v8"></path>
                <path d="M17 6v12"></path>
              </svg>
              Dashboard
            </RouterLink>
          </nav>

          <div class="relative hidden sm:block">
            <button
              type="button"
              @click="onToggleTheme"
              @mouseenter="tipOpen = true"
              @mouseleave="tipOpen = false"
              @focus="tipOpen = true"
              @blur="tipOpen = false"
              class="inline-flex h-11 w-11 items-center justify-center rounded-md border border-slate-200 bg-white text-slate-800 shadow-sm
                     transition-colors hover:bg-slate-50
                     focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400
                     dark:border-white/10 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800"
              :aria-label="themeAria"
              :title="themeAria"
              aria-describedby="tip-theme"
            >
              <Transition name="icon" mode="out-in">
                <svg
                  v-if="isDark"
                  key="sun"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="h-5 w-5"
                >
                  <circle cx="12" cy="12" r="4"></circle>
                  <path d="M12 2v2"></path><path d="M12 20v2"></path>
                  <path d="M4.93 4.93l1.41 1.41"></path><path d="M17.66 17.66l1.41 1.41"></path>
                  <path d="M2 12h2"></path><path d="M20 12h2"></path>
                  <path d="M4.93 19.07l1.41-1.41"></path><path d="M17.66 6.34l1.41-1.41"></path>
                </svg>

                <svg
                  v-else
                  key="moon"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="h-5 w-5"
                >
                  <path d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79z"></path>
                </svg>
              </Transition>
            </button>

            <Transition name="tip">
              <div
                v-if="tipOpen"
                id="tip-theme"
                role="tooltip"
                class="pointer-events-none absolute right-0 mt-2 max-w-[240px] rounded-md border border-slate-200 bg-white px-2 py-1 text-xs text-slate-700 shadow-md
                       dark:border-white/10 dark:bg-slate-900 dark:text-slate-200"
              >
                {{ tooltipText }}
              </div>
            </Transition>
          </div>
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-6xl px-4 py-6 sm:px-6">
      <RouterView />
    </main>

    <footer class="border-t border-slate-200/70 py-6 text-center text-xs text-slate-500 dark:border-white/10 dark:text-slate-400">
      &copy; 2026 Teste de Integração com API Pública. Todos os direitos reservados.
    </footer>
  </div>
</template>

<style scoped>
.icon-enter-active,
.icon-leave-active {
  transition: opacity 160ms ease, transform 160ms ease;
}
.icon-enter-from {
  opacity: 0;
  transform: rotate(-12deg) scale(0.92);
}
.icon-leave-to {
  opacity: 0;
  transform: rotate(12deg) scale(0.92);
}

.tip-enter-active,
.tip-leave-active {
  transition: opacity 140ms ease, transform 140ms ease;
}
.tip-enter-from,
.tip-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (prefers-reduced-motion: reduce) {
  .icon-enter-active,
  .icon-leave-active,
  .tip-enter-active,
  .tip-leave-active {
    transition: none !important;
  }
}
</style>
