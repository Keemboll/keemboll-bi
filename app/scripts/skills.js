// Live filter on the skills list; stages with no match are hidden.
const input = document.getElementById("skill-search");
const stages = [...document.querySelectorAll(".stage")];
const empty = document.getElementById("skill-empty");

input?.addEventListener("input", () => {
  const q = input.value.trim().toLowerCase();
  let shown = 0;
  for (const stage of stages) {
    const stageHit = stage.querySelector("h3").textContent.toLowerCase().includes(q);
    let any = false;
    for (const li of stage.querySelectorAll("li")) {
      li.hidden = !(stageHit || li.textContent.toLowerCase().includes(q));
      any ||= !li.hidden;
    }
    stage.hidden = !any;
    shown += any;
  }
  empty.hidden = shown > 0;
});
