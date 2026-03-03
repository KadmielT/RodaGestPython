// static/js/theme.js

document.addEventListener("DOMContentLoaded", () => {
  // 1) Pega o botão
  const btn = document.getElementById("themeToggle");
  if (!btn) return; // agora está dentro de uma função (pode retornar)

  // 2) Pega os spans internos (ícone e texto)
  const iconEl = btn.querySelector(".rg-theme-icon");
  const textEl = btn.querySelector(".rg-theme-text");

  // 3) Tema do sistema
  const media = window.matchMedia("(prefers-color-scheme: dark)");

  // 4) Tema inicial: storage > sistema
  function getInitialTheme() {
    const saved = localStorage.getItem("theme");
    if (saved === "dark" || saved === "light") return saved;
    return media.matches ? "dark" : "light";
  }

  // 5) Lê tema atual
  function getTheme() {
    return document.documentElement.getAttribute("data-theme") || "dark";
  }

  // 6) Atualiza UI do botão
  function updateButtonUI(theme) {
    if (theme === "dark") {
      if (iconEl) iconEl.textContent = "☀️";
      if (textEl) textEl.textContent = "Modo claro";
      btn.setAttribute("aria-label", "Ativar modo claro");
    } else {
      if (iconEl) iconEl.textContent = "🌙";
      if (textEl) textEl.textContent = "Modo escuro";
      btn.setAttribute("aria-label", "Ativar modo escuro");
    }
  }

  // 7) Aplica tema
  function setTheme(theme, save = true) {
    document.documentElement.setAttribute("data-theme", theme);
    updateButtonUI(theme);
    if (save) localStorage.setItem("theme", theme);
  }

  // 8) Toggle
  btn.addEventListener("click", () => {
    const current = getTheme();
    setTheme(current === "dark" ? "light" : "dark", true);
  });

  // 9) Inicializa
  setTheme(getInitialTheme(), false);

  // 10) Se usuário nunca escolheu manualmente, acompanha o sistema
  media.addEventListener("change", (e) => {
    const saved = localStorage.getItem("theme");
    if (saved !== "dark" && saved !== "light") {
      setTheme(e.matches ? "dark" : "light", false);
    }
  });
});