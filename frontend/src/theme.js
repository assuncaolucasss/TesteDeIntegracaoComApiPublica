const KEY = 'theme' // 'light' | 'dark'

export function initTheme() {
  const saved = localStorage.getItem(KEY)
  const theme = (saved === 'dark' || saved === 'light') ? saved : 'light'
  applyTheme(theme)
}

export function applyTheme(theme) {
  const root = document.documentElement
  root.classList.toggle('dark', theme === 'dark')
  localStorage.setItem(KEY, theme)
}

export function getTheme() {
  return document.documentElement.classList.contains('dark') ? 'dark' : 'light'
}

export function toggleTheme() {
  applyTheme(getTheme() === 'dark' ? 'light' : 'dark')
}
