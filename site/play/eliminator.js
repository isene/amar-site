// The Eliminator game page: the game, keys on the screen for phones, and
// full screen. The game itself is funkey's eliminator (funkey.js).
(async function () {
  "use strict";
  const MOVE = [["y", "↖"], ["ArrowUp", "↑"], ["u", "↗"], ["ArrowLeft", "←"], ["s", "wait"],
    ["ArrowRight", "→"], ["b", "↙"], ["ArrowDown", "↓"], ["n", "↘"]];
  const KEYS = [["1", "1", "normal"], ["2", "2", "offence"], ["3", "3", "defence"], ["4", "4", "guard"],
    ["5", "5", "power"], ["6", "6", "double"], ["f", "F", "fire"], ["p", "P", "potion"], ["m", "M", "bandage"],
    ["r", "R", "rest"], ["t", "T", "light"], ["g", "G", "take"], ["<", "<", "climb"], ["?", "?", "rules"],
    ["i", "I", "intro"], ["Enter", "Enter", ""], [" ", "Space", ""], ["Escape", "Esc", ""], ["Tab", "Tab", ""]];

  const box = document.querySelector(".game");
  const pad = document.getElementById("pad");
  const button = ([k, label, small]) => {
    const b = document.createElement("button");
    b.type = "button";
    b.dataset.key = k;
    b.textContent = label;
    if (small) { const s = document.createElement("small"); s.textContent = small; b.append(s); }
    return b;
  };
  const move = document.createElement("div");
  move.className = "pad-move";
  move.append(...MOVE.map(button));
  const keys = document.createElement("div");
  keys.className = "pad-keys";
  keys.append(...KEYS.map(button));
  pad.append(move, keys);
  pad.hidden = !(window.matchMedia && matchMedia("(pointer: coarse)").matches);
  document.getElementById("pad-toggle").addEventListener("click", () => { pad.hidden = !pad.hidden; });

  const full = document.getElementById("full");
  if (!document.fullscreenEnabled) full.hidden = true;
  full.addEventListener("click", () => box.requestFullscreen().catch(() => {}));

  // The page names the game file with the build's version tag, so a new game is never taken from the cache.
  const canvas = document.getElementById("eliminator");
  const game = await funkey.play(canvas, canvas.dataset.wasm);
  funkey.pad(pad, game);
})();
