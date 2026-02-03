<script setup>
import { computed } from 'vue'

const props = defineProps({
  rows: { type: Array, default: () => [] }, // [{ uf, total_uf }, ...]
  topN: { type: Number, default: 10 },
})

const brl = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

const ordered = computed(() =>
  [...props.rows]
    .map(r => ({ uf: String(r.uf ?? '').trim(), total_uf: Number(r.total_uf ?? 0) }))
    .filter(r => r.uf)
    .sort((a, b) => b.total_uf - a.total_uf)
)

const reduced = computed(() => {
  const n = Math.max(1, Number(props.topN ?? 10))
  const top = ordered.value.slice(0, n)
  const rest = ordered.value.slice(n)
  const outrosTotal = rest.reduce((acc, r) => acc + r.total_uf, 0)
  return rest.length > 0 ? [...top, { uf: 'Outros', total_uf: outrosTotal }] : top
})

const maxValue = computed(() => Math.max(...reduced.value.map(r => r.total_uf), 1))
</script>

<template>
  <div class="space-y-3">
    <div
      v-for="r in reduced"
      :key="r.uf"
      class="rounded-xl border border-slate-200 bg-white p-3 shadow-sm dark:border-white/10 dark:bg-slate-950"
    >
      <div class="flex items-center justify-between gap-3">
        <div class="text-sm font-semibold text-slate-900 dark:text-slate-100">
          {{ r.uf }}
        </div>
        <div class="text-sm font-semibold text-slate-900 dark:text-slate-100">
          {{ brl.format(r.total_uf) }}
        </div>
      </div>

      <div class="mt-2 h-2 w-full rounded bg-slate-100 dark:bg-white/10">
        <div
          class="h-2 rounded bg-teal-400/60"
          :style="{ width: `${Math.round((r.total_uf / maxValue) * 100)}%` }"
        />
      </div>
    </div>
  </div>
</template>
