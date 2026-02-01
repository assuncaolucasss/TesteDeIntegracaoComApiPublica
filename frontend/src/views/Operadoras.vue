<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { apiGet } from '../api'

const operadoras = ref([])
const loading = ref(false)
const error = ref('')

const q = ref('')
const page = ref(1)
const pageSize = ref(10)

const total = computed(() => operadoras.value.length)

const filtered = computed(() => {
  const term = q.value.trim().toLowerCase()
  if (!term) return operadoras.value
  return operadoras.value.filter(o =>
    String(o.razao_social ?? '').toLowerCase().includes(term) ||
    String(o.cnpj ?? '').includes(term) ||
    String(o.uf ?? '').toLowerCase().includes(term) ||
    String(o.modalidade ?? '').toLowerCase().includes(term)
  )
})

const pageCount = computed(() => Math.max(1, Math.ceil(filtered.value.length / pageSize.value)))

const paged = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filtered.value.slice(start, start + pageSize.value)
})

function go(p) {
  page.value = Math.min(pageCount.value, Math.max(1, p))
}

watch([q, pageSize], () => go(1))

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await apiGet('/api/operadoras')
    operadoras.value = Array.isArray(data) ? data : (data.items ?? data.data ?? [])
  } catch (e) {
    error.value = e?.message ?? String(e)
    operadoras.value = []
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
        <h1 class="text-2xl font-semibold tracking-tight">Operadoras</h1>
        <p class="text-sm text-slate-600 dark:text-slate-400">
          Busque por razão social, CNPJ, UF ou modalidade.
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

    <!-- Filtros -->
    <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-slate-900">
      <div class="grid gap-3 md:grid-cols-3">
        <div class="md:col-span-2">
          <label for="q" class="block text-sm font-medium text-slate-700 dark:text-slate-200">
            Buscar
          </label>
          <input
            id="q"
            v-model="q"
            type="text"
            inputmode="search"
            autocomplete="off"
            placeholder="Ex.: UNIMED, 123..., SP, Autogestão…"
            class="mt-1 h-11 w-full rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-900 placeholder:text-slate-400 shadow-sm
                   focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400
                   dark:border-white/10 dark:bg-slate-950 dark:text-slate-100 dark:placeholder:text-slate-500"
          />
        </div>

        <div>
          <label for="pageSize" class="block text-sm font-medium text-slate-700 dark:text-slate-200">
            Itens por página
          </label>
          <select
            id="pageSize"
            v-model.number="pageSize"
            class="mt-1 h-11 w-full rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-900 shadow-sm
                   focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400
                   dark:border-white/10 dark:bg-slate-950 dark:text-slate-100"
          >
            <option :value="5">5</option>
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
          </select>
        </div>
      </div>

      <div class="mt-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <p class="text-sm text-slate-600 dark:text-slate-400">
          Mostrando <span class="font-medium text-slate-900 dark:text-slate-100">{{ paged.length }}</span>
          de <span class="font-medium text-slate-900 dark:text-slate-100">{{ filtered.length }}</span>
          (total: {{ total }})
        </p>

        <div class="flex items-center justify-between gap-2 sm:justify-end">
          <button
            type="button"
            @click="go(page - 1)"
            :disabled="page <= 1 || loading"
            class="inline-flex h-11 items-center justify-center rounded-md border border-slate-200 bg-white px-4 text-sm font-medium text-slate-800 hover:bg-slate-50
                   disabled:cursor-not-allowed disabled:opacity-60 dark:border-white/10 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800"
          >
            Anterior
          </button>

          <span class="text-sm text-slate-600 dark:text-slate-400">
            Página <span class="font-medium text-slate-900 dark:text-slate-100">{{ page }}</span> / {{ pageCount }}
          </span>

          <button
            type="button"
            @click="go(page + 1)"
            :disabled="page >= pageCount || loading"
            class="inline-flex h-11 items-center justify-center rounded-md border border-slate-200 bg-white px-4 text-sm font-medium text-slate-800 hover:bg-slate-50
                   disabled:cursor-not-allowed disabled:opacity-60 dark:border-white/10 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800"
          >
            Próxima
          </button>
        </div>
      </div>
    </div>

    <!-- Estados -->
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
      <div class="font-semibold">Erro ao carregar operadoras</div>
      <div class="mt-1 break-words">{{ error }}</div>
    </div>

    <template v-else>
      <!-- MOBILE: Cards (sm <) -->
      <div class="space-y-3 sm:hidden">
        <article
          v-for="o in paged"
          :key="o.cnpj"
          class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-slate-900"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <div class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                Razão social
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
          </div>

          <router-link
            :to="`/operadoras/${o.cnpj}`"
            class="mt-4 inline-flex h-11 w-full items-center justify-center rounded-md bg-slate-900 px-4 text-sm font-medium text-white hover:bg-slate-800
                   focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400
                   dark:bg-white dark:text-slate-900 dark:hover:bg-slate-200"
          >
            Ver detalhes
          </router-link>
        </article>

        <div v-if="paged.length === 0" class="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-700 shadow-sm dark:border-white/10 dark:bg-slate-900 dark:text-slate-200">
          Nenhum resultado para o filtro atual.
        </div>
      </div>

      <!-- DESKTOP/TABLET: Tabela (sm+) -->
      <div class="hidden sm:block rounded-xl border border-slate-200 bg-white shadow-sm dark:border-white/10 dark:bg-slate-900">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 dark:divide-white/10">
            <thead class="bg-slate-50 dark:bg-slate-950">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">
                  CNPJ
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">
                  Razão social
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">
                  UF
                </th>
                <th class="hidden md:table-cell px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">
                  Modalidade
                </th>
                <th class="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400">
                  Ações
                </th>
              </tr>
            </thead>

            <tbody class="divide-y divide-slate-200 dark:divide-white/10">
              <tr v-for="o in paged" :key="o.cnpj" class="hover:bg-slate-50 dark:hover:bg-white/5">
                <td class="whitespace-nowrap px-4 py-3 text-sm font-medium text-slate-900 dark:text-slate-100">
                  {{ o.cnpj }}
                </td>
                <td class="px-4 py-3 text-sm text-slate-800 dark:text-slate-200">
                  {{ o.razao_social }}
                </td>
                <td class="px-4 py-3 text-sm text-slate-800 dark:text-slate-200">
                  <span class="inline-flex min-w-10 justify-center rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700 dark:bg-white/10 dark:text-slate-200">
                    {{ o.uf }}
                  </span>
                </td>
                <td class="hidden md:table-cell px-4 py-3 text-sm text-slate-800 dark:text-slate-200">
                  {{ o.modalidade }}
                </td>
                <td class="whitespace-nowrap px-4 py-3 text-right text-sm">
                  <router-link
                    :to="`/operadoras/${o.cnpj}`"
                    class="inline-flex h-10 items-center rounded-md bg-slate-900 px-4 text-sm font-medium text-white hover:bg-slate-800
                           focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400
                           dark:bg-white dark:text-slate-900 dark:hover:bg-slate-200"
                  >
                    Ver detalhes
                  </router-link>
                </td>
              </tr>

              <tr v-if="paged.length === 0">
                <td colspan="5" class="px-4 py-8 text-center text-sm text-slate-600 dark:text-slate-400">
                  Nenhum resultado para o filtro atual.
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="flex flex-col gap-2 border-t border-slate-200 p-3 text-sm text-slate-600 dark:border-white/10 dark:text-slate-400 sm:flex-row sm:items-center sm:justify-between">
          <div>
            Página <span class="font-medium text-slate-900 dark:text-slate-100">{{ page }}</span> de {{ pageCount }}
          </div>

          <div class="flex items-center justify-between gap-2 sm:justify-end">
            <button
              type="button"
              @click="go(1)"
              :disabled="page === 1 || loading"
              class="inline-flex h-11 items-center justify-center rounded-md border border-slate-200 bg-white px-4 text-sm font-medium text-slate-800 hover:bg-slate-50
                     disabled:cursor-not-allowed disabled:opacity-60 dark:border-white/10 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800"
            >
              Primeira
            </button>

            <button
              type="button"
              @click="go(pageCount)"
              :disabled="page === pageCount || loading"
              class="inline-flex h-11 items-center justify-center rounded-md border border-slate-200 bg-white px-4 text-sm font-medium text-slate-800 hover:bg-slate-50
                     disabled:cursor-not-allowed disabled:opacity-60 dark:border-white/10 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800"
            >
              Última
            </button>
          </div>
        </div>
      </div>
    </template>
  </section>
</template>
