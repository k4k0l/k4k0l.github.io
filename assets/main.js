/* kakol.pro — the modern layer hiding under the retro surface.
   Everything here is progressive enhancement: the site is fully readable with JS off. */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---- ask-the-page chatbot endpoint (Cloudflare Worker). Empty = feature dormant (button hidden). ---- */
  var CHAT_ENDPOINT = "https://chat.kakol.workers.dev"; /* Cloudflare Worker (Workers AI) — repo: ~/Documents/Play/kakol-chat */
  var TURNSTILE_SITEKEY = ""; /* Cloudflare Turnstile sitekey — set to activate the invisible bot check (empty = off) */

  /* ---- theme toggle (lights). Respects prefers-color-scheme by default ---- */
  try {
    var saved = localStorage.getItem("kp-theme");
    if (saved) document.documentElement.setAttribute("data-theme", saved);
  } catch (e) {}
  function toggleTheme() {
    var cur = document.documentElement.getAttribute("data-theme");
    var sysDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    var next = cur ? (cur === "dark" ? "light" : "dark") : (sysDark ? "light" : "dark");
    document.documentElement.setAttribute("data-theme", next);
    try { localStorage.setItem("kp-theme", next); } catch (e) {}
  }

  /* ---- retro hit counter, computed client-side (no server, no tracker) ---- */
  function paintCounter() {
    var el = $("#hitcounter"); if (!el) return;
    var base = 13370, n;
    try {
      n = parseInt(localStorage.getItem("kp-hits") || "0", 10) || 0;
      if (!sessionStorage.getItem("kp-counted")) { n += 1; localStorage.setItem("kp-hits", String(n)); sessionStorage.setItem("kp-counted", "1"); }
    } catch (e) { n = 1; }
    var total = base + n;
    el.textContent = ("000000" + total).slice(-6);
  }

  /* ---- site index for palette + search (written by _build.py) ---- */
  var INDEX = [];
  function loadIndex() {
    return fetch("/assets/index.json").then(function (r) { return r.json(); })
      .then(function (j) { INDEX = j || []; }).catch(function () { INDEX = []; });
  }
  function score(q, t) { t = t.toLowerCase(); q = q.toLowerCase(); if (!q) return 1;
    if (t.indexOf(q) >= 0) return 2; var i = 0, j = 0; while (i < q.length && j < t.length) { if (q[i] === t[j]) i++; j++; } return i === q.length ? 0.5 : 0; }

  /* ---- command palette ( / or Cmd/Ctrl-K ) ---- */
  function buildPalette() {
    var p = document.createElement("div"); p.id = "palette"; p.setAttribute("role", "dialog"); p.setAttribute("aria-modal", "true"); p.setAttribute("aria-label", "Command palette");
    p.innerHTML = '<div class="box"><input type="text" placeholder="jump to… (type a page or note)" aria-label="Search pages"><ul role="listbox"></ul><div class="hint">↑↓ to move · ↵ to open · Esc to close — (yes, this 1996 page has a command palette)</div></div>';
    document.body.appendChild(p);
    var input = $("input", p), list = $("ul", p), sel = 0, items = [], prevFocus = null;
    function render() {
      var q = input.value.trim();
      items = INDEX.map(function (e) { return { e: e, s: Math.max(score(q, e.title), score(q, e.kind || "")) }; })
        .filter(function (x) { return x.s > 0; }).sort(function (a, b) { return b.s - a.s; }).slice(0, 8).map(function (x) { return x.e; });
      list.innerHTML = items.map(function (e, i) { return '<li role="option" data-url="' + e.url + '" aria-selected="' + (i === sel) + '">' + (e.kind === "note" ? "✎ " : "» ") + e.title + "</li>"; }).join("");
      sel = Math.min(sel, Math.max(0, items.length - 1));
      $$("li", list).forEach(function (li, i) { li.setAttribute("aria-selected", i === sel); li.onclick = function () { go(i); }; });
    }
    function go(i) { if (items[i]) location.href = items[i].url; }
    function open() { prevFocus = document.activeElement; p.classList.add("open"); input.value = ""; sel = 0; render(); input.focus(); }
    function close() { p.classList.remove("open"); if (prevFocus && prevFocus.focus) prevFocus.focus(); }
    input.addEventListener("input", function () { sel = 0; render(); });
    input.addEventListener("keydown", function (ev) {
      if (ev.key === "ArrowDown") { sel = Math.min(sel + 1, items.length - 1); render(); ev.preventDefault(); }
      else if (ev.key === "ArrowUp") { sel = Math.max(sel - 1, 0); render(); ev.preventDefault(); }
      else if (ev.key === "Enter") { go(sel); }
      else if (ev.key === "Escape") { close(); }
    });
    p.addEventListener("click", function (ev) { if (ev.target === p) close(); });
    document.addEventListener("keydown", function (ev) {
      var typing = /^(input|textarea)$/i.test(document.activeElement && document.activeElement.tagName || "");
      if ((ev.key === "/" && !typing) || ((ev.metaKey || ev.ctrlKey) && ev.key.toLowerCase() === "k")) { ev.preventDefault(); open(); }
    });
    return { open: open };
  }

  /* ---- inline site search box (footer-of-masthead) ---- */
  function wireSearch() {
    var box = $("#site-search"), out = $("#search-results"); if (!box || !out) return;
    box.addEventListener("input", function () {
      var q = box.value.trim(); if (!q) { out.innerHTML = ""; return; }
      var hits = INDEX.map(function (e) { return { e: e, s: score(q, e.title) }; }).filter(function (x) { return x.s > 0; })
        .sort(function (a, b) { return b.s - a.s; }).slice(0, 6);
      out.innerHTML = hits.map(function (x) { return '<li><a href="' + x.e.url + '">' + (x.e.kind === "note" ? "✎ " : "") + x.e.title + "</a></li>"; }).join("");
    });
  }

  /* ---- Konami code -> "1996 mode" (CRT scanlines) ---- */
  (function () {
    var seq = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65], pos = 0;
    document.addEventListener("keydown", function (ev) {
      pos = (ev.keyCode === seq[pos]) ? pos + 1 : 0;
      if (pos === seq.length) { document.body.classList.toggle("crt"); pos = 0;
        var m = $("#konami-note"); if (m) m.hidden = !document.body.classList.contains("crt"); }
    });
  })();

  /* ---- chiptune theme (Web Audio, click-to-play, never autoplay) ---- */
  function playTheme(btn) {
    try {
      var AC = window.AudioContext || window.webkitAudioContext; if (!AC) return;
      var ac = new AC(), now = ac.currentTime;
      var notes = [392, 523, 659, 784, 659, 523, 587, 494]; // a little arpeggio
      notes.forEach(function (f, i) {
        var o = ac.createOscillator(), g = ac.createGain(); o.type = "square"; o.frequency.value = f;
        var t = now + i * 0.16; g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.12, t + 0.02);
        g.gain.exponentialRampToValueAtTime(0.0001, t + 0.15); o.connect(g); g.connect(ac.destination); o.start(t); o.stop(t + 0.16);
      });
    } catch (e) {}
  }

  /* ---- Cloudflare Turnstile: mint a fresh single-use token per message (invisible). Dormant if no sitekey. ---- */
  var _tsLoaded = false;
  function loadTurnstile() {
    if (_tsLoaded) return; _tsLoaded = true;
    var s = document.createElement("script");
    s.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
    s.async = true; s.defer = true; document.head.appendChild(s);
  }
  function turnstileReady(cb, tries) {
    if (window.turnstile && window.turnstile.render) return cb(true);
    if ((tries || 0) > 60) return cb(false);
    setTimeout(function () { turnstileReady(cb, (tries || 0) + 1); }, 100);
  }
  function mintToken() {
    return new Promise(function (resolve) {
      if (!TURNSTILE_SITEKEY) { resolve(""); return; }
      loadTurnstile();
      turnstileReady(function (ok) {
        if (!ok) { resolve(""); return; }
        var holder = document.createElement("div");
        holder.style.position = "absolute"; holder.style.left = "-9999px"; holder.style.top = "0";
        document.body.appendChild(holder);
        var wid, settled = false;
        function done(tok) { if (settled) return; settled = true; try { window.turnstile.remove(wid); } catch (e) {} try { holder.remove(); } catch (e) {} resolve(tok || ""); }
        try {
          wid = window.turnstile.render(holder, {
            sitekey: TURNSTILE_SITEKEY, action: "chat", size: "invisible",
            callback: function (t) { done(t); },
            "error-callback": function () { done(""); },
            "timeout-callback": function () { done(""); },
            "expired-callback": function () { done(""); }
          });
        } catch (e) { done(""); }
        setTimeout(function () { done(""); }, 8000);
      });
    });
  }

  /* ---- ask-the-page chatbot (green CRT terminal -> Cloudflare Worker -> Workers AI) ---- */
  function buildChat() {
    var btn = $("#askbtn"); if (btn) btn.hidden = false;
    var panel = document.createElement("div"); panel.id = "chat"; panel.setAttribute("role", "dialog"); panel.setAttribute("aria-modal", "true"); panel.setAttribute("aria-label", "Ask the page");
    panel.innerHTML = '<div class="cbox">'
      + '<div class="chead"><span>kakol.pro :: ask the page</span><button class="cx" type="button" aria-label="close">×</button></div>'
      + '<div class="clog" aria-live="polite"></div>'
      + '<form class="cform"><span class="cp">&gt;</span><input class="cin" type="text" autocomplete="off" placeholder="ask about Michał, his work, the notes…" aria-label="message"></form>'
      + '<div class="chint">a small AI on a free Cloudflare Worker — it can be wrong. Esc to close.</div>'
      + '</div>';
    document.body.appendChild(panel);
    var log = $(".clog", panel), input = $(".cin", panel), form = $(".cform", panel);
    var history = [], busy = false, prevFocus = null;
    var GREETING = "Hi — I'm the little assistant on Michał's homepage. Ask me about his work, the field notes, or how this site is built.";
    function add(role, text) {
      var line = document.createElement("div"); line.className = "cmsg c-" + role;
      var who = document.createElement("span"); who.className = "who"; who.textContent = (role === "user" ? "you:" : "kakol.pro:");
      line.appendChild(who); line.appendChild(document.createTextNode(" " + text));
      log.appendChild(line); log.scrollTop = log.scrollHeight; return line;
    }
    function open() { prevFocus = document.activeElement; panel.classList.add("open"); if (!log.childNodes.length) add("bot", GREETING); input.focus(); }
    function close() { panel.classList.remove("open"); if (prevFocus && prevFocus.focus) prevFocus.focus(); }
    if (btn) btn.addEventListener("click", open);
    $(".cx", panel).addEventListener("click", close);
    panel.addEventListener("click", function (ev) { if (ev.target === panel) close(); });
    document.addEventListener("keydown", function (ev) { if (ev.key === "Escape" && panel.classList.contains("open")) close(); });
    function submit(q) {
      q = (q || "").trim(); if (!q || busy) return;
      open();
      input.value = ""; add("user", q); history.push({ role: "user", content: q });
      var pending = add("bot", "…"); pending.classList.add("pending"); busy = true;
      mintToken().then(function (token) {
        return fetch(CHAT_ENDPOINT, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ messages: history.slice(-8), cf_token: token }) });
      })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          pending.remove();
          if (res.ok && res.j && res.j.reply) { add("bot", res.j.reply); history.push({ role: "assistant", content: res.j.reply }); }
          else { add("bot", (res.j && res.j.error) ? ("(" + res.j.error + ")") : "(something went wrong)"); }
        })
        .catch(function () { pending.remove(); add("bot", "(offline — couldn't reach the assistant)"); })
        .then(function () { busy = false; input.focus(); });
    }
    form.addEventListener("submit", function (ev) { ev.preventDefault(); submit(input.value); });

    /* persistent corner launcher (all pages) */
    var fab = document.createElement("button");
    fab.id = "ask-fab"; fab.type = "button"; fab.setAttribute("aria-label", "Ask the page (AI)");
    fab.innerHTML = '<span class="fab-star" aria-hidden="true">✦</span> ask <span class="fab-caret" aria-hidden="true">▸</span>';
    document.body.appendChild(fab);
    fab.addEventListener("click", open);

    /* home hero terminal prompt -> opens chat with the typed question */
    var hero = $("#ask-hero");
    if (hero) {
      hero.hidden = false;
      var heroIn = $("#ask-hero-in", hero);
      hero.addEventListener("submit", function (ev) { ev.preventDefault(); var v = heroIn.value; heroIn.value = ""; submit(v); });
    }
  }

  /* ---- wire up ---- */
  document.addEventListener("DOMContentLoaded", function () {
    paintCounter();
    var lights = $("#lights"); if (lights) lights.addEventListener("click", toggleTheme);
    var snd = $("#sound"); if (snd) snd.addEventListener("click", function () { playTheme(snd); });
    var pal = buildPalette();
    var palBtn = $("#palbtn"); if (palBtn) palBtn.addEventListener("click", pal.open);
    loadIndex().then(function () { wireSearch(); });
    if (CHAT_ENDPOINT) buildChat();
  });

  /* ---- service worker (offline) ---- */
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () { navigator.serviceWorker.register("/sw.js").catch(function () {}); });
  }
})();
