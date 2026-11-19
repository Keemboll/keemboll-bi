// Adds a "Copy" button to every .codeblock.
for (const block of document.querySelectorAll(".codeblock")) {
  const btn = Object.assign(document.createElement("button"), { className: "copy", type: "button", textContent: "Copy" });
  btn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(block.querySelector("code").innerText);
      btn.textContent = "Copied ✓";
    } catch {
      btn.textContent = "Press Ctrl+C"; // clipboard API needs https or localhost
    }
    setTimeout(() => (btn.textContent = "Copy"), 1800);
  });
  block.append(btn);
}
