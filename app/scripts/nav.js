// Scroll-spy for the header links + fade-in of sections.
const links = new Map([...document.querySelectorAll("nav a[href^='#']")].map((a) => [a.hash.slice(1), a]));

const spy = new IntersectionObserver((entries) => {
  for (const e of entries) {
    if (!e.isIntersecting) continue;
    links.forEach((a) => a.removeAttribute("aria-current"));
    links.get(e.target.id)?.setAttribute("aria-current", "true");
  }
}, { rootMargin: "-40% 0px -55% 0px" });
links.forEach((_, id) => { const s = document.getElementById(id); if (s) spy.observe(s); });

const reveal = new IntersectionObserver((entries, obs) => {
  for (const e of entries) if (e.isIntersecting) { e.target.classList.add("in"); obs.unobserve(e.target); }
}, { threshold: 0.12 });
document.querySelectorAll(".reveal").forEach((el) => reveal.observe(el));
