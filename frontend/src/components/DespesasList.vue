<script setup>
import { computed } from 'vue'

const props = defineProps({
  rows: { type: Array, default: () => [] }, // [{ ano, trimestre, valor_despesas }, ...]
})

const brl = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

function money(v) {
  return brl.format(Number(v ?? 0))
}

// Mantém a ordenação "mais recente primeiro" que já chega da página (mas garante)
const ordered = computed(() =>
  [...props.rows].sort((a, b) => {
    const ay = Number(a?.ano ?? 0)
    const by = Number(b?.ano ?? 0)
    if (by !== ay) return by - ay
    const at = Number(a?.trimestre ?? 0)
    const bt = Number(b?.trimestre ?? 0)
    return bt - at
  })
)

const maxValue = computed(() => {
  const vals = ordered.value.map(r => Number(r?.valor_despesas ?? 0))
  return Math.max(...vals, 1)
})
</script>

<template>
  <div class="space-y-3">
    <article
      v-for="d in ordered"
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
            {{ money(d.valor_despesas) }}
          </div>
        </div>
      </div>

      <div class="mt-3 h-2 w-full rounded bg-slate-100 dark:bg-white/10">
        <div
          class="h-2 rounded bg-sky-400/60"
          :style="{ width: `${Math.round((Number(d.valor_despesas ?? 0) / maxValue) * 100)}%` }"
        />
      </div>
    </article>
  </div>
</template>
