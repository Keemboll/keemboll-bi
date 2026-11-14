// Loaded in <head>, blocking, so the stored theme is applied before first paint.
(() => {
  const root = document.documentElement;
  root.classList.add("js");
  try {
    const saved = localStorage.getItem("theme");
    if (saved) root.dataset.theme = saved;
  } catch {}

  addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("theme-toggle");
    const dark = () => (root.dataset.theme || "dark") === "dark";
    const paint = () => { btn.textContent = dark() ? "☀" : "☾"; btn.setAttribute("aria-label", dark() ? "Switch to light theme" : "Switch to dark theme"); };
    paint();
    btn.addEventListener("click", () => {
      root.dataset.theme = dark() ? "light" : "dark";
      try { localStorage.setItem("theme", root.dataset.theme); } catch {}
      paint();
    });
  });
})();
