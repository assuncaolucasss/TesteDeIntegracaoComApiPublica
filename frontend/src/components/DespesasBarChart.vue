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
  despesas: { type: Array, default: () => [] },
})

// Tooltip em BRL completo
const brlFull = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

// Eixo Y abreviado (sem "R$")
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

// Ordenação garantida (Ano/Trimestre)
const ordered = computed(() =>
  [...props.despesas].sort(
    (a, b) => (Number(a.ano) - Number(b.ano)) || (Number(a.trimestre) - Number(b.trimestre))
  )
)

const labels = computed(() => ordered.value.map(d => `${d.ano} T${d.trimestre}`))
const values = computed(() => ordered.value.map(d => Number(d.valor_despesas ?? 0)))

const chartData = computed(() => ({
  labels: labels.value,
  datasets: [
    {
      label: 'Despesas',
      data: values.value,
      backgroundColor: 'rgba(54, 162, 235, 0.35)',
      borderColor: 'rgba(54, 162, 235, 1)',
      borderWidth: 1,
    },
  ],
}))

const chartOptions = computed(() => ({
  responsive: true,
  plugins: {
    legend: { display: true },
    title: { display: true, text: 'Despesas por trimestre' },
    tooltip: {
      callbacks: {
        label: (ctx) => ` ${ctx.dataset.label}: ${brlFull.format(ctx.parsed.y)}`,
      },
    },
  },
  scales: {
    y: {
      title: {
        display: true,
        text: 'R$ (mil/mi/bi)',
      },
      ticks: {
        callback: (value) => fmtCompactAxis(value),
      },
    },
  },
}))
</script>

<template>
  <div style="max-width: 900px;">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>
