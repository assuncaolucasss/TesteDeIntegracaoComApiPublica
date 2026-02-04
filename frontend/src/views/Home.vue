<!-- Home.vue -->
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiGet } from '../api'

const router = useRouter()

function go(path) {
  router.push(path)
}

const statsState = ref('loading') // 'loading' | 'ok' | 'unavailable'
const stats = ref(null)

const brl = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }) // [web:2896]

const hasStats = computed(() => statsState.value === 'ok' && !!stats.value)

const totalDespesas = computed(() => Number(stats.value?.total_despesas ?? 0))
const mediaDespesas = computed(() => Number(stats.value?.media_despesas ?? 0))
const top1 = computed(() => stats.value?.top5_operadoras?.[0] ?? null)

async function loadStats() {
  statsState.value = 'loading'
  try {
    const res = await apiGet('/api/estatisticas')
    stats.value = res ?? null
    statsState.value = stats.value ? 'ok' : 'unavailable'
  } catch {
    stats.value = null
    statsState.value = 'unavailable'
  }
}

onMounted(loadStats) // [web:2889]
</script>

<template>
  <section class="space-y-8">
    <header class="space-y-2">
      <h1 class="text-3xl font-semibold tracking-tight sm:text-4xl">Teste de Integração</h1>
      <p class="text-sm text-slate-600 dark:text-slate-400 sm:text-base">
        Explore operadoras e despesas consolidadas com filtros, ranking e visualizações responsivas.
      </p>
    </header>

    <!-- Mini-métricas -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <!-- Total -->
      <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-white/10 dark:bg-slate-900">
        <div class="flex items-start justify-between gap-3">
          <div class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Total de despesas
          </div>

          <button
            v-if="statsState === 'unavailable'"
            type="button"
            @click="loadStats"
            class="inline-flex h-8 items-center justify-center rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold text-slate-700 shadow-sm hover:bg-slate-50
                   focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400
                   dark:border-white/10 dark:bg-slate-950 dark:text-slate-200 dark:hover:bg-slate-800"
          >
            Tentar novamente
          </button>
        </div>

        <div class="mt-1 text-xl font-semibold text-slate-900 dark:text-slate-100">
          <span v-if="statsState === 'loading'">Carregando…</span>
          <span v-else-if="hasStats">{{ brl.format(totalDespesas) }}</span>
          <span v-else>—</span>
        </div>

        <p v-if="statsState === 'unavailable'" class="mt-1 text-xs text-slate-500 dark:text-slate-400">
          Indicadores indisponíveis (backend offline).
        </p>
      </article>

      <!-- Média -->
      <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-white/10 dark:bg-slate-900">
        <div class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
          Média por operadora
        </div>

        <div class="mt-1 text-xl font-semibold text-slate-900 dark:text-slate-100">
          <span v-if="statsState === 'loading'">Carregando…</span>
          <span v-else-if="hasStats">{{ brl.format(mediaDespesas) }}</span>
          <span v-else>—</span>
        </div>

        <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
          Baseado nos dados consolidados.
        </p>
      </article>

      <!-- Top operadora -->
      <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-white/10 dark:bg-slate-900">
        <div class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
          Top operadora
        </div>

        <div class="mt-1 text-sm font-semibold text-slate-900 dark:text-slate-100">
          <span v-if="statsState === 'loading'">Carregando…</span>
          <span v-else-if="hasStats">{{ top1?.razao_social ?? '—' }}</span>
          <span v-else>—</span>
        </div>

        <div class="mt-1 text-xs text-slate-500 dark:text-slate-400">
          <span v-if="hasStats && top1">CNPJ: {{ top1.cnpj }} • UF: {{ top1.uf }}</span>
          <span v-else-if="statsState === 'unavailable'">Indicadores indisponíveis (backend offline).</span>
        </div>
      </article>
    </div>

    <!-- Cards principais -->
    <div class="grid grid-cols-1 gap-5 lg:grid-cols-2">
      <!-- Card Operadoras -->
      <article
        class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:shadow-md
               dark:border-white/10 dark:bg-slate-900 sm:p-7"
      >
        <div class="flex items-start gap-4">
          <div
            class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-slate-900 text-white
                   dark:bg-white dark:text-slate-900"
            aria-hidden="true"
          >
            <!-- ícone lupa -->
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="h-6 w-6">
              <circle cx="11" cy="11" r="7"></circle>
              <path d="M21 21l-4.3-4.3"></path>
            </svg>
          </div>

          <div class="min-w-0">
            <h2 class="text-xl font-semibold text-slate-900 dark:text-slate-100">Operadoras</h2>
            <p class="mt-1 text-sm text-slate-600 dark:text-slate-400">
              Pesquise por razão social ou CNPJ e veja detalhes e histórico de despesas.
            </p>
          </div>
        </div>

        <div class="mt-6">
          <button
            type="button"
            @click="go('/operadoras')"
            class="inline-flex h-11 w-full items-center justify-center rounded-md bg-slate-900 px-4 text-sm font-medium text-white hover:bg-slate-800
                   focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400
                   dark:bg-white dark:text-slate-900 dark:hover:bg-slate-200"
          >
            Ir para Operadoras
          </button>
        </div>
      </article>

      <!-- Card Dashboard -->
      <article
        class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:shadow-md
               dark:border-white/10 dark:bg-slate-900 sm:p-7"
      >
        <div class="flex items-start gap-4">
          <div
            class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-900
                   dark:border-white/10 dark:bg-slate-950 dark:text-slate-100"
            aria-hidden="true"
          >
            <!-- ícone gráfico -->
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="h-6 w-6">
              <path d="M3 3v18h18"></path>
              <path d="M7 14v4"></path>
              <path d="M12 10v8"></path>
              <path d="M17 6v12"></path>
            </svg>
          </div>

          <div class="min-w-0">
            <h2 class="text-xl font-semibold text-slate-900 dark:text-slate-100">Dashboard</h2>
            <p class="mt-1 text-sm text-slate-600 dark:text-slate-400">
              Veja indicadores consolidados e panorama por UF.
            </p>
          </div>
        </div>

        <div class="mt-6">
          <button
            type="button"
            @click="go('/dashboard')"
            class="inline-flex h-11 w-full items-center justify-center rounded-md border border-slate-200 bg-white px-4 text-sm font-medium text-slate-800 shadow-sm hover:bg-slate-50
                   focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400
                   dark:border-white/10 dark:bg-slate-950 dark:text-slate-100 dark:hover:bg-slate-800"
          >
            Ir para Dashboard
          </button>
        </div>
      </article>
    </div>

    <!-- Ações rápidas -->
    <div class="flex flex-col gap-2 sm:flex-row">
      <button
        type="button"
        @click="go('/operadoras')"
        class="inline-flex h-11 w-full items-center justify-center rounded-md border border-slate-200 bg-white px-4 text-sm font-medium text-slate-800 shadow-sm hover:bg-slate-50
               focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400
               dark:border-white/10 dark:bg-slate-950 dark:text-slate-100 dark:hover:bg-slate-800"
      >
        Buscar operadora
      </button>

      <button
        type="button"
        @click="go('/dashboard')"
        class="inline-flex h-11 w-full items-center justify-center rounded-md bg-slate-900 px-4 text-sm font-medium text-white hover:bg-slate-800
               focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400
               dark:bg-white dark:text-slate-900 dark:hover:bg-slate-200"
      >
        Ver insights do Dashboard
      </button>
    </div>
  </section>
</template>
