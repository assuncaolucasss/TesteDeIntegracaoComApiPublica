<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <section class="space-y-6">
    <header class="space-y-2">
      <h1 class="text-2xl font-semibold tracking-tight">Teste de Integração</h1>
      <p class="text-sm text-slate-600 dark:text-slate-400">
        Explore operadoras e despesas consolidadas com filtros, ranking e visualizações responsivas.
      </p>
    </header>

    <div class="grid gap-4 md:grid-cols-2">
      <article class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-white/10 dark:bg-slate-900">
        <h2 class="text-lg font-semibold text-slate-900 dark:text-slate-100">Operadoras</h2>
        <p class="mt-1 text-sm text-slate-600 dark:text-slate-400">
          Pesquise por razão social ou CNPJ e veja detalhes e histórico de despesas.
        </p>

        <button
          type="button"
          @click="router.push('/operadoras')"
          class="mt-4 inline-flex h-11 w-full items-center justify-center rounded-md bg-slate-900 px-4 text-sm font-medium text-white hover:bg-slate-800
                 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400
                 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-200"
        >
          Ir para Operadoras
        </button>
      </article>

      <article class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-white/10 dark:bg-slate-900">
        <h2 class="text-lg font-semibold text-slate-900 dark:text-slate-100">Dashboard</h2>
        <p class="mt-1 text-sm text-slate-600 dark:text-slate-400">
          Veja indicadores consolidados e panorama por UF.
        </p>

        <button
          type="button"
          @click="router.push('/dashboard')"
          class="mt-4 inline-flex h-11 w-full items-center justify-center rounded-md border border-slate-200 bg-white px-4 text-sm font-medium text-slate-800 shadow-sm hover:bg-slate-50
                 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400
                 dark:border-white/10 dark:bg-slate-950 dark:text-slate-100 dark:hover:bg-slate-800"
        >
          Ir para Dashboard
        </button>
      </article>
    </div>

    <div class="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700 dark:border-white/10 dark:bg-slate-950 dark:text-slate-200">
      Dica: no mobile, as visualizações usam listas para melhorar legibilidade; no desktop, gráficos e tabelas aparecem completos.
    </div>
  </section>
</template>
