<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiGet } from '../api'
import DespesasBarChart from '../components/DespesasBarChart.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const error = ref('')

const operadora = ref(null)
const despesas = ref([])

const cnpj = computed(() => String(route.params.cnpj ?? ''))

const brl = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
function fmtMoney(v) {
  return brl.format(Number(v ?? 0))
}

// Ordena: mais recente primeiro (ano desc, trimestre desc)
const despesasSorted = computed(() => {
  return [...despesas.value].sort((a, b) => {
    const ay = Number(a?.ano ?? 0)
    const by = Number(b?.ano ?? 0)
    if (by !== ay) return by - ay
    const at = Number(a?.trimestre ?? 0)
    const bt = Number(b?.trimestre ?? 0)
    return bt - at
  })
})

const availableYears = computed(() => {
  const years = new Set(despesasSorted.value.map(d => Number(d?.ano ?? 0)).filter(Boolean))
  return [...years].sort((a, b) => b - a)
})

// Filtros (0 = "todos")
const yearFilter = ref(0)
const triFilter = ref(0)

// Trimestres existentes conforme dados disponíveis:
// - Se ano específico: trimestres que existem naquele ano
// - Se "Todos os anos": trimestres que existem no dataset inteiro
const trimestresForYear = computed(() => {
  const base = yearFilter.value
    ? despesasSorted.value.filter(d => Number(d?.ano ?? 0) === Number(yearFilter.value))
    : despesasSorted.value

  const tris = new Set(
    base.map(d => Number(d?.trimestre ?? 0)).filter(Boolean)
  )

  return [...tris].sort((a, b) => a - b)
})

// Se trimestre selecionado não existir para o ano atual, reseta para "Todos os trimestres"
watch([yearFilter, trimestresForYear], () => {
  if (triFilter.value && !trimestresForYear.value.includes(Number(triFilter.value))) {
    triFilter.value = 0
  }
})

const despesasFiltered = computed(() => {
  return despesasSorted.value.filter(d => {
    const okYear = !yearFilter.value || Number(d?.ano ?? 0) === Number(yearFilter.value)
    const okTri = !triFilter.value || Number(d?.trimestre ?? 0) === Number(triFilter.value)
    return okYear && okTri
  })
})

const totalDespesasFiltered = computed(() =>
  despesasFiltered.value.reduce((acc, d) => acc + Number(d.valor_despesas ?? 0), 0)
)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const c = cnpj.value
    operadora.value = await apiGet(`/api/operadoras/${c}`)
    despesas.value = await apiGet(`/api/operadoras/${c}/despesas`)

    yearFilter.value = 0
    triFilter.value = 0
  } catch (e) {
    error.value = e?.message ?? String(e)
    operadora.value = null
    despesas.value = []
  } finally {
    loading.value = false
  }
}

function goBack() {
  if (window.history.length > 1) router.back()
  else router.push('/')
}

onMounted(load)
watch(() => route.params.cnpj, () => load())
</script>

<template>
  <section class="space-y-4">
    <header class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
      <div class="space-y-1">
        <button
          type="button"
          @click="goBack"
          class="inline-flex h-11 items-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-medium text-slate-800 shadow-sm hover:bg-slate-50
                 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400
                 dark:border-white/10 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800"
        >
          ← Voltar
        </button>

        <h1 class="text-2xl font-semibold tracking-tight">Detalhes da operadora</h1>
        <p class="text-sm text-slate-600 dark:text-slate-400">
          CNPJ: <span class="font-medium text-slate-900 dark:text-slate-100">{{ cnpj }}</span>
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
      <div class="font-semibold">Erro ao carregar detalhes</div>
      <div class="mt-1 break-words">{{ error }}</div>
    </div>

    <template v-else>
      <!-- Card: dados da operadora -->
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-slate-900">
        <div class="grid gap-4 md:grid-cols-3">
          <div class="md:col-span-2">
            <div class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Razão social
            </div>
            <div class="mt-1 text-base font-semibold text-slate-900 dark:text-slate-100">
              {{ operadora?.razao_social ?? '-' }}
            </div>

            <div class="mt-4 grid gap-3 sm:grid-cols-2">
              <div>
                <div class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">CNPJ</div>
                <div class="mt-1 text-sm font-medium text-slate-800 dark:text-slate-200">
                  {{ operadora?.cnpj ?? cnpj }}
                </div>
              </div>

              <div>
                <div class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Modalidade</div>
                <div class="mt-1 text-sm font-medium text-slate-800 dark:text-slate-200">
                  {{ operadora?.modalidade ?? '-' }}
                </div>
              </div>
            </div>
          </div>

          <div class="space-y-3">
            <div>
              <div class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">UF</div>
              <div class="mt-1 inline-flex min-w-12 justify-center rounded-md bg-slate-100 px-2 py-1 text-sm font-semibold text-slate-700 dark:bg-white/10 dark:text-slate-200">
                {{ operadora?.uf ?? '-' }}
              </div>
            </div>

            <div class="rounded-lg border border-slate-200 bg-slate-50 p-3 dark:border-white/10 dark:bg-slate-950">
              <div class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                Total (recorte atual)
              </div>
              <div class="mt-1 text-lg font-semibold text-slate-900 dark:text-slate-100">
                {{ fmtMoney(totalDespesasFiltered) }}
              </div>
              <div class="mt-1 text-xs text-slate-500 dark:text-slate-400">
                Pontos no recorte: {{ despesasFiltered.length }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Card: filtros + gráfico + lista/tabela -->
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-slate-900">
        <div class="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h2 class="text-lg font-semibold">Histórico de despesas</h2>
            <p class="text-sm text-slate-600 dark:text-slate-400">
              Filtre por ano e/ou trimestre (opções refletem os dados existentes).
            </p>
          </div>
        </div>

        <!-- filtros -->
        <div class="mt-4 grid gap-3 sm:grid-cols-2">
          <div>
            <label for="yearFilter" class="block text-sm font-medium text-slate-700 dark:text-slate-200">
              Ano
            </label>
            <select
              id="yearFilter"
              v-model.number="yearFilter"
              class="mt-1 h-11 w-full rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-900 shadow-sm
                     focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400
                     dark:border-white/10 dark:bg-slate-950 dark:text-slate-100"
            >
              <option :value="0">Todos os anos</option>
              <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
            </select>
          </div>

          <div>
            <label for="triFilter" class="block text-sm font-medium text-slate-700 dark:text-slate-200">
              Trimestre
            </label>
            <select
              id="triFilter"
              v-model.number="triFilter"
              :disabled="trimestresForYear.length === 0"
              class="mt-1 h-11 w-full rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-900 shadow-sm
                     focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400
                     disabled:cursor-not-allowed disabled:opacity-60
                     dark:border-white/10 dark:bg-slate-950 dark:text-slate-100"
            >
              <option :value="0">Todos os trimestres</option>
              <option v-for="t in trimestresForYear" :key="t" :value="t">T{{ t }}</option>
            </select>
          </div>
        </div>

        <div
          v-if="despesasFiltered.length === 0"
          class="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700 dark:border-white/10 dark:bg-slate-950 dark:text-slate-200"
        >
          Sem dados para o filtro selecionado.
        </div>

        <div v-else class="mt-4 grid gap-4 lg:grid-cols-5">
          <div class="lg:col-span-3">
            <div class="rounded-lg border border-slate-200 bg-white p-3 dark:border-white/10 dark:bg-slate-950">
              <DespesasBarChart :despesas="despesasFiltered" />
            </div>
          </div>

          <div class="lg:col-span-2">
            <!-- MOBILE: Cards -->
            <div class="space-y-3 sm:hidden">
              <article
                v-for="d in despesasFiltered"
                :key="`${d.ano}-${d.trimestre}`"
                class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-slate-950"
              >
                <div class="flex items-start justify-between gap-3">
                  <div class="min-w-0">
                    <div class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                      Período
                    </div>
                    <div class="mt-1 text-sm font-semibold text-slate-900 dark:text-slate-100">
                      {{ d.ano }} • T{{ d.trimestre }}
                    </div>
                  </div>

                  <div class="text-right">
                    <div class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                      Valor
                    </div>
                    <div class="mt-1 whitespace-nowrap text-sm font-semibold text-slate-900 dark:text-slate-100">
                      {{ fmtMoney(d.valor_despesas) }}
                    </div>
                  </div>
                </div>
              </article>
            </div>

            <!-- TABLET/DESKTOP: Tabela -->
            <div class="hidden overflow-x-auto rounded-lg border border-slate-200 dark:border-white/10 sm:block">
              <table class="min-w-full divide-y divide-slate-200 dark:divide-white/10">
                <thead class="bg-slate-50 dark:bg-slate-950">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">Ano</th>
                    <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">Trimestre</th>
                    <th class="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">Valor</th>
                  </tr>
                </thead>

                <tbody class="divide-y divide-slate-200 bg-white dark:divide-white/10 dark:bg-slate-900">
                  <tr v-for="d in despesasFiltered" :key="`${d.ano}-${d.trimestre}`" class="hover:bg-slate-50 dark:hover:bg-white/5">
                    <td class="px-4 py-3 text-sm text-slate-800 dark:text-slate-200">{{ d.ano }}</td>
                    <td class="px-4 py-3 text-sm text-slate-800 dark:text-slate-200">T{{ d.trimestre }}</td>
                    <td class="whitespace-nowrap px-4 py-3 text-right text-sm font-medium text-slate-900 dark:text-slate-100">
                      {{ fmtMoney(d.valor_despesas) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </template>
  </section>
</template>
