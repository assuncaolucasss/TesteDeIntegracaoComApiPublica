<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiGet } from '../api'
import UFsBarChart from '../components/UFsBarChart.vue'

const loading = ref(false)
const error = ref('')

const stats = ref(null)
const porUF = ref([])

const topNUF = ref(10)

const brl = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
const top5 = computed(() => stats.value?.top5_operadoras ?? [])

async function load() {
  loading.value = true
  error.value = ''
  try {
    stats.value = await apiGet('/api/estatisticas')
    porUF.value = await apiGet('/api/estatisticas/uf')
  } catch (e) {
    error.value = e?.message ?? String(e)
    stats.value = null
    porUF.value = []
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="space-y-4">
    <header class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p class="text-sm text-slate-600 dark:text-slate-400">
          Indicadores consolidados e recortes de maior relevância.
        </p>
      </div>

      <button
        type="button"
        @click="load"
        :disabled="loading"
        class="inline-flex h-11 items-center justify-center rounded-md border border-slate-200 bg-white px-4 text-sm font-medium text-slate-800 shadow-sm hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60
               dark:border-white/10 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800"
      >
        <span v-if="loading">Atualizando…</span>
        <span v-else>Atualizar</span>
      </button>
    </header>

    <div
      v-if="loading"
      class="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-700 shadow-sm dark:border-white/10 dark:bg-slate-900 dark:text-slate-200"
      role="status"
    >
      Carregando…
    </div>

    <div
      v-else-if="error"
      class="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800 shadow-sm dark:border-red-500/30 dark:bg-red-950/40 dark:text-red-200"
      role="alert"
    >
      <div class="font-semibold">Erro ao carregar o dashboard</div>
      <div class="mt-1 break-words">{{ error }}</div>
    </div>

    <template v-else>
      <!-- Métricas -->
      <div class="grid gap-4 md:grid-cols-2">
        <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-slate-900">
          <div class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Despesas totais (consolidado)
          </div>
          <div class="mt-1 text-2xl font-semibold text-slate-900 dark:text-slate-100">
            {{ brl.format(stats?.total_despesas ?? 0) }}
          </div>
          <div class="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Soma geral do conjunto de dados.
          </div>
        </div>

        <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-slate-900">
          <div class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Despesa média por operadora
          </div>
          <div class="mt-1 text-2xl font-semibold text-slate-900 dark:text-slate-100">
            {{ brl.format(stats?.media_despesas ?? 0) }}
          </div>
          <div class="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Média calculada a partir do agregado.
          </div>
        </div>
      </div>

      <!-- Top 5 -->
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-slate-900">
        <div class="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h2 class="text-lg font-semibold">Ranking de operadoras por despesas acumuladas (Top 5)</h2>
            <p class="text-sm text-slate-600 dark:text-slate-400">
              Lista das operadoras com maior volume financeiro no período disponível na base.
            </p>
          </div>
        </div>

        <div v-if="top5.length === 0" class="mt-4 text-sm text-slate-600 dark:text-slate-400">
          Sem dados para exibir.
        </div>

        <template v-else>
          <!-- MOBILE: Cards -->
          <div class="mt-4 space-y-3 sm:hidden">
            <article
              v-for="(o, idx) in top5"
              :key="o.cnpj"
              class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-slate-950"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <div class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                    #{{ idx + 1 }} • Razão social
                  </div>
                  <div class="mt-1 truncate text-sm font-semibold text-slate-900 dark:text-slate-100">
                    {{ o.razao_social }}
                  </div>
                </div>

                <span class="shrink-0 rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700 dark:bg-white/10 dark:text-slate-200">
                  {{ o.uf }}
                </span>
              </div>

              <div class="mt-3 grid gap-2">
                <div class="flex items-center justify-between gap-3">
                  <div class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">CNPJ</div>
                  <div class="text-sm font-medium text-slate-900 dark:text-slate-100">{{ o.cnpj }}</div>
                </div>

                <div class="flex items-start justify-between gap-3">
                  <div class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Modalidade</div>
                  <div class="text-right text-sm text-slate-800 dark:text-slate-200">
                    {{ o.modalidade }}
                  </div>
                </div>

                <div class="flex items-center justify-between gap-3">
                  <div class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Total</div>
                  <div class="text-sm font-semibold text-slate-900 dark:text-slate-100">
                    {{ brl.format(o.total_despesas) }}
                  </div>
                </div>
              </div>
            </article>
          </div>

          <!-- TABLET/DESKTOP: Tabela -->
          <div class="mt-4 hidden overflow-x-auto rounded-lg border border-slate-200 dark:border-white/10 sm:block">
            <table class="min-w-full divide-y divide-slate-200 dark:divide-white/10">
              <thead class="bg-slate-50 dark:bg-slate-950">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">CNPJ</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">Razão social</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">UF</th>
                  <th class="hidden md:table-cell px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">Modalidade</th>
                  <th class="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">Total (R$)</th>
                </tr>
              </thead>

              <tbody class="divide-y divide-slate-200 bg-white dark:divide-white/10 dark:bg-slate-900">
                <tr v-for="o in top5" :key="o.cnpj" class="hover:bg-slate-50 dark:hover:bg-white/5">
                  <td class="whitespace-nowrap px-4 py-3 text-sm font-medium text-slate-900 dark:text-slate-100">{{ o.cnpj }}</td>
                  <td class="px-4 py-3 text-sm text-slate-800 dark:text-slate-200">{{ o.razao_social }}</td>
                  <td class="px-4 py-3 text-sm text-slate-800 dark:text-slate-200">
                    <span class="inline-flex min-w-10 justify-center rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700 dark:bg-white/10 dark:text-slate-200">
                      {{ o.uf }}
                    </span>
                  </td>
                  <td class="hidden md:table-cell px-4 py-3 text-sm text-slate-800 dark:text-slate-200">{{ o.modalidade }}</td>
                  <td class="whitespace-nowrap px-4 py-3 text-right text-sm font-semibold text-slate-900 dark:text-slate-100">
                    {{ brl.format(o.total_despesas) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </div>

      <!-- Despesas por UF -->
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-slate-900">
        <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
          <div class="min-w-0">
            <h2 class="text-lg font-semibold">Panorama geográfico: despesas por UF</h2>
            <p class="text-sm text-slate-600 dark:text-slate-400">
              Comparação do total de despesas por estado; use o filtro abaixo para destacar as UFs mais relevantes e consolidar o restante.
            </p>
          </div>

          <div class="relative mt-1 shrink-0">
            <div class="group inline-flex items-center gap-2">
              <span class="text-xs text-slate-500 dark:text-slate-400">Como funciona “Outros”?</span>

              <button
                type="button"
                class="inline-flex h-11 w-11 items-center justify-center rounded-md border border-slate-200 bg-white text-slate-700 shadow-sm hover:bg-slate-50
                       focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400
                       dark:border-white/10 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
                aria-describedby="tip-outros"
              >
                <span class="sr-only">Informações sobre o agrupamento “Outros”</span>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4">
                  <circle cx="12" cy="12" r="10"></circle>
                  <path d="M12 16v-4"></path>
                  <path d="M12 8h.01"></path>
                </svg>
              </button>

              <div
                id="tip-outros"
                role="tooltip"
                class="pointer-events-none absolute right-0 top-12 hidden w-[280px] rounded-md border border-slate-200 bg-white p-3 text-xs text-slate-700 shadow-md
                       group-hover:block group-focus-within:block
                       dark:border-white/10 dark:bg-slate-900 dark:text-slate-200"
              >
                O gráfico destaca apenas as UFs selecionadas no filtro. Todas as demais UFs são somadas em uma única barra chamada “Outros”, evitando poluição visual.
              </div>
            </div>
          </div>
        </div>

        <div class="mt-3 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div class="w-full sm:w-auto">
            <label for="topNUF" class="block text-sm font-medium text-slate-700 dark:text-slate-200">
              Critério de destaque no gráfico
            </label>
            <select
              id="topNUF"
              v-model.number="topNUF"
              class="mt-1 h-11 w-full rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-900 shadow-sm
                     focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400
                     dark:border-white/10 dark:bg-slate-950 dark:text-slate-100 sm:w-96"
            >
              <option :value="5">Mostrar as 5 UFs com maior despesa</option>
              <option :value="10">Mostrar as 10 UFs com maior despesa</option>
              <option :value="15">Mostrar as 15 UFs com maior despesa</option>
            </select>
          </div>

          <p class="text-xs text-slate-500 dark:text-slate-400">
            Exibição atual: Top {{ topNUF }} + “Outros”.
          </p>
        </div>

        <div v-if="porUF.length === 0" class="mt-4 text-sm text-slate-600 dark:text-slate-400">
          Sem dados para exibir.
        </div>

        <div v-else class="mt-4 rounded-lg border border-slate-200 bg-white p-3 dark:border-white/10 dark:bg-slate-950">
          <div class="w-full overflow-x-auto">
            <div class="min-h-[520px] sm:min-h-[380px]">
              <UFsBarChart :rows="porUF" :topN="topNUF" />
            </div>
          </div>
        </div>
      </div>
    </template>
  </section>
</template>
