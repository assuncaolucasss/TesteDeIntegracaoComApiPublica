<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const props = defineProps({
  rows: { type: Array, default: () => [] }, // [{ uf: 'SP', total_uf: 123 }, ...]
  topN: { type: Number, default: 10 },
})

const brlFull = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

function fmtCompactAxis(value) {
  const n = Number(value ?? 0)
  const abs = Math.abs(n)
  let div = 1
  let suf = ''
  if (abs >= 1e9) { div = 1e9; suf = ' bi' }
  else if (abs >= 1e6) { div = 1e6; suf = ' mi' }
  else if (abs >= 1e3) { div = 1e3; suf = ' mil' }
  const scaled = n / div
  const num = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 }).format(scaled)
  return `${num}${suf}`
}

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

const labels = computed(() => reduced.value.map(r => r.uf))
const values = computed(() => reduced.value.map(r => r.total_uf))

const chartData = computed(() => ({
  labels: labels.value,
  datasets: [
    {
      label: `Total por UF (Top ${Math.max(1, props.topN)} + Outros)`,
      data: values.value,
      backgroundColor: 'rgba(75, 192, 192, 0.35)',
      borderColor: 'rgba(75, 192, 192, 1)',
      borderWidth: 1,
    },
  ],
}))

const chartOptions = computed(() => ({
  responsive: true,
  indexAxis: 'y',
  plugins: {
    legend: { display: true },
    title: { display: true, text: 'Total de despesas por UF' },
    tooltip: {
      callbacks: {
        label: (ctx) => ` ${ctx.label}: ${brlFull.format(ctx.parsed.x)}`,
      },
    },
  },
  scales: {
    x: {
      title: { display: true, text: 'R$ (mil/mi/bi)' },
      ticks: {
        callback: (value) => fmtCompactAxis(value),
      },
    },
  },
}))
</script>

<template>
  <div class="w-full">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>
