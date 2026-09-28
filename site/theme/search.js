// Search by title and heading first, then by the words of each section.
// The index loads on the first focus only.
(() => {
  const q = document.getElementById("q"), hits = document.getElementById("hits");
  let data = null;
  const load = () => data || (data = fetch("search.json").then(r => r.json()));
  const esc = s => s.replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
  q.addEventListener("focus", load, {once: true});
  q.addEventListener("input", async () => {
    const all = await load(), s = q.value.trim().toLowerCase();
    if (s.length < 2) { hits.hidden = true; return; }
    const words = s.split(/\s+/), found = [];
    for (const p of all) {
      const t = p.t.toLowerCase(), where = t + " " + p.s.toLowerCase(), body = " " + p.w;
      let rank;
      if (words.every(w => where.includes(w)))
        rank = t === s ? 0 : t.startsWith(s) ? 1 : t.includes(s) ? 2 : words.every(w => t.includes(w)) ? 3 : 4;
      else if (words.every(w => where.includes(w) || body.includes(" " + w)))
        // words are stored most frequent first: an early match means the section is about it
        rank = 6 + Math.min(...words.map(w => { const i = body.indexOf(" " + w); return i < 0 ? 1 : i / body.length; }));
      else continue;
      found.push([rank, p]);
    }
    found.sort((a, b) => a[0] - b[0] || a[1].t.length - b[1].t.length);
    hits.innerHTML = found.slice(0, 14).map(([, p]) =>
      `<li><a href="${p.u}">${esc(p.t)}</a>${p.s ? `<span>${esc(p.s)}</span>` : ""}</li>`).join("")
      || '<li class="none">Nothing matches. Try a shorter word.</li>';
    hits.hidden = false;
  });
  q.addEventListener("keydown", e => {
    if (e.key === "Enter") { const a = hits.querySelector("a"); if (a) location.href = a.href; }
    if (e.key === "Escape") { q.value = ""; hits.hidden = true; }
  });
  document.addEventListener("click", e => { if (!e.target.closest(".search")) hits.hidden = true; });
})();
