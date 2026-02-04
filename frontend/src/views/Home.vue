<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()

function go(path) {
  router.push(path)
}
</script>

<template>
  <section class="space-y-8">
    <header class="space-y-2">
      <h1 class="text-3xl font-semibold tracking-tight sm:text-4xl">Teste de Integração</h1>
      <p class="text-sm text-slate-600 dark:text-slate-400 sm:text-base">
        Explore operadoras e despesas consolidadas com filtros, ranking e visualizações responsivas.
      </p>
    </header>

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
  </section>
</template>
