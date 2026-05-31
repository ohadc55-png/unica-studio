(function () {
  "use strict";

  var STATIC = "/static/";

  /* ---------- scroll reveal ---------- */
  var revealEls = document.querySelectorAll(".reveal, .reveal-lines");
  var noAnim = /(?:[?&])noanim/.test(location.search);
  if (noAnim) {
    revealEls.forEach(function (el) { el.classList.add("in-view"); });
    document.querySelectorAll('img[loading="lazy"]').forEach(function (i) { i.loading = "eager"; });
  } else if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add("in-view");
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.16, rootMargin: "0px 0px -8% 0px" });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("in-view"); });
  }

  /* ---------- nav background (always solid for legibility over panels) ---------- */
  var nav = document.getElementById("nav");
  if (nav) nav.classList.add("is-scrolled");

  /* ---------- mobile menu ---------- */
  var toggle = document.getElementById("navToggle");
  var menu = document.getElementById("mobileMenu");
  var setMenu = function (open) {
    nav.classList.toggle("menu-open", open);
    menu.classList.toggle("open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.style.overflow = open ? "hidden" : "";
  };
  if (toggle) toggle.addEventListener("click", function () { setMenu(!menu.classList.contains("open")); });
  menu && menu.querySelectorAll("[data-close]").forEach(function (a) {
    a.addEventListener("click", function () { setMenu(false); });
  });

  /* ---------- hero slideshow (slow ken-burns drift) ---------- */
  var heroFrame = document.getElementById("heroFrame");
  if (heroFrame) {
    var slides = heroFrame.querySelectorAll(".hero__slide");
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (slides.length > 1 && !reduce) {
      var hidx = 0;
      setInterval(function () {
        slides[hidx].classList.remove("is-active");
        hidx = (hidx + 1) % slides.length;
        var img = slides[hidx].querySelector("img");
        if (img) { img.style.animation = "none"; void img.offsetWidth; img.style.animation = ""; }
        slides[hidx].classList.add("is-active");
      }, 8000);
    }
  }

  /* =====================================================
     FULL-PAGE HORIZONTAL PIN
     vertical scroll → horizontal panel travel, with a
     dwell slot on the work panel that drives the card fan.
     ===================================================== */
  var hsite = document.getElementById("hsite");
  if (hsite) {
    var panels = Array.prototype.slice.call(hsite.querySelectorAll(".spanel"));
    var wstack = document.getElementById("wstack");
    var hFill = document.getElementById("hsiteFill");
    var chapEls = Array.prototype.slice.call(hsite.querySelectorAll(".hsite__chapters span"));

    var slots = panels.map(function (p) { return parseFloat(p.dataset.slots) || 1; });
    var workIdx = -1;
    for (var k = 0; k < panels.length; k++) { if (panels[k].dataset.id === "work") { workIdx = k; break; } }
    var workDwell = (workIdx >= 0 ? slots[workIdx] : 1) - 1; // extra slots beyond the default 1
    var sumSlots = slots.reduce(function (a, b) { return a + b; }, 0);
    var N = panels.length;

    hsite.style.setProperty("--total-slots", sumSlots);
    hsite.style.setProperty("--pan", 0);
    if (wstack) wstack.style.setProperty("--fan", 0);

    var lastPanel = -1;
    var lastChap = -1;

    var hsUpdate = function () {
      // mobile fallback — let CSS handle stacked layout, cards in grid
      if (window.innerWidth <= 900) {
        hsite.style.setProperty("--pan", 0);
        if (wstack) wstack.style.setProperty("--fan", 1);
        if (hFill) hFill.style.transform = "scaleX(0)";
        return;
      }
      var rect = hsite.getBoundingClientRect();
      var totalScroll = hsite.offsetHeight - window.innerHeight;
      if (totalScroll <= 0) return;
      var raw = -rect.top / totalScroll;
      var progress = Math.max(0, Math.min(1, raw));

      var slotProgress = progress * (sumSlots - 1);

      var pan, fan = 0;
      if (workIdx < 0 || workDwell <= 0) {
        pan = slotProgress;
      } else if (slotProgress <= workIdx) {
        pan = slotProgress;
      } else if (slotProgress <= workIdx + workDwell) {
        pan = workIdx;
        fan = (slotProgress - workIdx) / workDwell;
      } else {
        pan = slotProgress - workDwell;
      }

      hsite.style.setProperty("--pan", pan.toFixed(5));
      if (wstack) wstack.style.setProperty("--fan", fan.toFixed(4));
      if (hFill) hFill.style.transform = "scaleX(" + progress.toFixed(4) + ")";

      // active panel marker
      var curIdx = Math.round(pan);
      if (curIdx !== lastPanel) {
        panels.forEach(function (p, i) { p.classList.toggle("is-current", i === curIdx); });
        lastPanel = curIdx;
      }

      // chapter HUD: collapse panels into 6 named chapters
      // 0:hero 1:about 2:services 3:process 4:portfolio 5:contact (approx)
      var chap;
      if (curIdx <= 1) chap = 0;
      else if (curIdx === 2) chap = 1;
      else if (curIdx === 3) chap = 2;
      else if (curIdx === 4) chap = 3;
      else if (curIdx <= 7) chap = 4;
      else chap = 5;
      if (chap !== lastChap) {
        chapEls.forEach(function (s, i) { s.classList.toggle("is-active", i === chap); });
        lastChap = chap;
      }
    };

    var hsQueued = false;
    var hsOnScroll = function () {
      if (!hsQueued) {
        hsQueued = true;
        requestAnimationFrame(function () { hsUpdate(); hsQueued = false; });
      }
    };
    window.addEventListener("scroll", hsOnScroll, { passive: true });
    window.addEventListener("resize", hsOnScroll);
    hsUpdate();

    // anchor → scroll the page to the Y position that lands on that panel
    var panAnchors = document.querySelectorAll("[data-pan-href]");
    panAnchors.forEach(function (a) {
      a.addEventListener("click", function (e) {
        var href = a.getAttribute("data-pan-href") || "";
        if (!href || href.charAt(0) !== "#") return;
        var id = href.slice(1);
        var target = null, targetIdx = -1;
        for (var i = 0; i < panels.length; i++) {
          if (panels[i].dataset.id === id) { target = panels[i]; targetIdx = i; break; }
        }
        if (!target) return;
        e.preventDefault();
        if (window.innerWidth <= 900) {
          target.scrollIntoView({ behavior: "smooth", block: "start" });
          return;
        }
        var targetSlot = targetIdx;
        if (workDwell > 0 && targetIdx > workIdx) targetSlot = targetIdx + workDwell;
        var targetProgress = targetSlot / (sumSlots - 1);
        var totalScroll = hsite.offsetHeight - window.innerHeight;
        var targetY = hsite.offsetTop + targetProgress * totalScroll;
        window.scrollTo({ top: targetY, behavior: "smooth" });
      });
    });

    // brand mark → return to start
    var brandEl = document.querySelector(".brand[data-pan]");
    if (brandEl) {
      brandEl.addEventListener("click", function (e) {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
    }
  }

  /* ---------- before / after slider ---------- */
  var baStage = document.getElementById("baStage");
  if (baStage) {
    var dragging = false;
    var setP = function (clientX) {
      var r = baStage.getBoundingClientRect();
      var x = (clientX - r.left) / r.width;
      x = Math.max(0, Math.min(1, x));
      baStage.style.setProperty("--p", (x * 100).toFixed(2) + "%");
    };
    baStage.addEventListener("pointerdown", function (e) {
      dragging = true;
      try { baStage.setPointerCapture(e.pointerId); } catch (err) {}
      setP(e.clientX);
    });
    baStage.addEventListener("pointermove", function (e) { if (dragging) setP(e.clientX); });
    baStage.addEventListener("pointerup", function () { dragging = false; });
    baStage.addEventListener("pointercancel", function () { dragging = false; });
    var baHandle = document.getElementById("baHandle");
    if (baHandle) {
      baHandle.addEventListener("keydown", function (e) {
        var cur = parseFloat(getComputedStyle(baStage).getPropertyValue("--p")) || 50;
        if (e.key === "ArrowLeft") { baStage.style.setProperty("--p", Math.max(0, cur - 4) + "%"); e.preventDefault(); }
        else if (e.key === "ArrowRight") { baStage.style.setProperty("--p", Math.min(100, cur + 4) + "%"); e.preventDefault(); }
      });
    }
  }

  /* ---------- portfolio data ---------- */
  var projects = [];
  try {
    projects = JSON.parse(document.getElementById("pf-data").textContent || "[]");
  } catch (e) { projects = []; }
  var bySlug = {};
  projects.forEach(function (p) { bySlug[p.slug] = p; });

  /* ---------- lightbox ---------- */
  var lb = document.getElementById("lightbox");
  var lbStage = document.getElementById("lbStage");
  var lbTitle = document.getElementById("lbTitle");
  var lbCount = document.getElementById("lbCount");
  var lbThumbs = document.getElementById("lbThumbs");
  var current = null, index = 0, lastFocus = null;

  function preload(src) { var i = new Image(); i.src = src; }

  function render() {
    if (!current) return;
    var imgs = current.images;
    var im = imgs[index];
    lbStage.innerHTML = "";
    var pic = document.createElement("img");
    pic.src = STATIC + im.full;
    pic.alt = current.title + " — תמונה " + (index + 1);
    lbStage.appendChild(pic);
    lbTitle.textContent = current.title;
    lbCount.textContent = (index + 1) + " / " + imgs.length;
    Array.prototype.forEach.call(lbThumbs.children, function (t, i) {
      t.classList.toggle("active", i === index);
      if (i === index) t.scrollIntoView({ block: "nearest", inline: "center", behavior: "smooth" });
    });
    preload(STATIC + imgs[(index + 1) % imgs.length].full);
    preload(STATIC + imgs[(index - 1 + imgs.length) % imgs.length].full);
  }

  function buildThumbs() {
    lbThumbs.innerHTML = "";
    current.images.forEach(function (im, i) {
      var t = document.createElement("img");
      t.src = STATIC + im.thumb;
      t.alt = "תמונה " + (i + 1);
      t.addEventListener("click", function () { index = i; render(); });
      lbThumbs.appendChild(t);
    });
  }

  function open(slug, start) {
    current = bySlug[slug];
    if (!current || !current.images.length) return;
    index = start || 0;
    lastFocus = document.activeElement;
    buildThumbs();
    render();
    lb.classList.add("open");
    lb.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function close() {
    lb.classList.remove("open");
    lb.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    current = null;
    if (lastFocus) lastFocus.focus();
  }

  function step(dir) {
    if (!current) return;
    var n = current.images.length;
    index = (index + dir + n) % n;
    render();
  }

  document.querySelectorAll("[data-open]").forEach(function (btn) {
    btn.addEventListener("click", function () { open(btn.getAttribute("data-open"), 0); });
  });
  document.getElementById("lbClose").addEventListener("click", close);
  document.getElementById("lbPrev").addEventListener("click", function () { step(-1); });
  document.getElementById("lbNext").addEventListener("click", function () { step(1); });
  lb.addEventListener("click", function (e) { if (e.target === lb || e.target === lbStage) close(); });

  document.addEventListener("keydown", function (e) {
    if (!lb.classList.contains("open")) return;
    if (e.key === "Escape") close();
    else if (e.key === "ArrowRight") step(-1);
    else if (e.key === "ArrowLeft") step(1);
  });

  var sx = 0;
  lbStage.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
  lbStage.addEventListener("touchend", function (e) {
    var dx = e.changedTouches[0].clientX - sx;
    if (Math.abs(dx) > 50) step(dx > 0 ? -1 : 1);
  }, { passive: true });
})();
