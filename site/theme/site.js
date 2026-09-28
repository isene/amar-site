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

// A video shows as a still picture; the YouTube player loads only when tapped.
for (const a of document.querySelectorAll("a.video[data-yt]")) {
  a.addEventListener("click", e => {
    e.preventDefault();
    const f = document.createElement("iframe");
    f.src = `https://www.youtube-nocookie.com/embed/${a.dataset.yt}?autoplay=1`;
    f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
    f.allowFullscreen = true;
    f.title = a.querySelector("img").alt;
    f.className = "video";
    a.replaceWith(f);
  });
}

// The light/dark switch: overrides the device setting and is remembered.
const mode = document.querySelector(".mode");
if (mode) mode.addEventListener("click", () => {
  const dark = getComputedStyle(document.documentElement).colorScheme.includes("dark");
  document.documentElement.dataset.theme = dark ? "light" : "dark";
  try { localStorage.setItem("theme", dark ? "light" : "dark"); } catch (e) {}
});

// The easy-reading font and the edit links: on or off, remembered like light/dark
for (const [sel, key, on] of [[".font-btn", "font", "sans"], [".pen", "edit", "on"]]) {
  const b = document.querySelector(sel), root = document.documentElement;
  if (!b) continue;
  b.setAttribute("aria-pressed", String(root.dataset[key] === on));
  b.addEventListener("click", () => {
    const next = root.dataset[key] === on ? null : on;
    if (next) root.dataset[key] = next; else delete root.dataset[key];
    b.setAttribute("aria-pressed", String(Boolean(next)));
    try { if (next) localStorage.setItem(key, next); else localStorage.removeItem(key); } catch (e) {}
  });
}
