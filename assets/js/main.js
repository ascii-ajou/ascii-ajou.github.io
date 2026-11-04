// Mobile navigation toggle
document.addEventListener("DOMContentLoaded", function () {
  var btn = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      nav.classList.toggle("open");
    });
  }

  // News: show the latest 5, fold the rest
  var news = document.querySelector(".news");
  if (news && news.children.length > 5) {
    news.classList.add("collapsed");
    var more = document.createElement("button");
    more.className = "news-toggle";
    more.textContent = "Show more";
    more.addEventListener("click", function () {
      var collapsed = news.classList.toggle("collapsed");
      more.textContent = collapsed ? "Show more" : "Show less";
    });
    news.after(more);
  }

  // Gallery: each year can fold behind a "Show N events" button; the latest year starts open
  document.querySelectorAll(".gallery-fold").forEach(function (g, idx) {
    var n = g.children.length;
    var label = "Show " + n + (n === 1 ? " event" : " events");
    if (idx > 0) g.classList.add("collapsed");
    var btn = document.createElement("button");
    btn.className = "news-toggle gallery-fold-toggle";
    btn.textContent = idx > 0 ? label : "Show less";
    btn.addEventListener("click", function () {
      var collapsed = g.classList.toggle("collapsed");
      btn.textContent = collapsed ? label : "Show less";
    });
    g.after(btn);
  });

  // Research Impact: count numbers up and grow bars when the block scrolls into view
  var animBlocks = document.querySelectorAll("[data-animate]");
  if (animBlocks.length && "IntersectionObserver" in window &&
      !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var countUp = function (el) {
      var end = parseInt(el.getAttribute("data-count"), 10) || 0;
      var t0 = null, dur = 1200;
      var step = function (t) {
        if (t0 === null) t0 = t;
        var p = Math.min((t - t0) / dur, 1);
        el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3)));
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };
    animBlocks.forEach(function (block) {
      block.classList.add("pre");
      block.querySelectorAll("[data-count]").forEach(function (el) { el.textContent = "0"; });
      block.querySelectorAll(".stat, .keywords li").forEach(function (el, i) { el.style.transitionDelay = (i * 60) + "ms"; });
      block.querySelectorAll(".bars .b").forEach(function (el, i) { el.style.transitionDelay = (i * 70) + "ms"; });
      block.querySelectorAll(".keywords li").forEach(function (el, i) {
        el.style.setProperty("--d", (i * 60) + "ms");
      });
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        io.unobserve(e.target);
        e.target.classList.remove("pre");
        e.target.querySelectorAll("[data-count]").forEach(countUp);
        // Clear stagger delays afterwards so hover effects respond instantly
        setTimeout(function () {
          e.target.querySelectorAll(".stat, .keywords li, .bars .b").forEach(function (el) { el.style.transitionDelay = ""; });
        }, 2000);
      });
    }, { threshold: 0.3 });
    animBlocks.forEach(function (b) { io.observe(b); });
  }

  // Home terminal: type "cat README.md", then stream its output
  var cmd = document.querySelector(".term-body .cmd");
  var readme = document.querySelector(".term-body .readme");
  var last = document.querySelector(".term-body .last");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (cmd && readme && last && !reduce) {
    var cmdText = cmd.textContent;
    var cursor = last.querySelector(".cursor");
    // Keep README markup (highlighted keywords): type through its text nodes in order
    var walker = document.createTreeWalker(readme, NodeFilter.SHOW_TEXT);
    var nodes = [];
    while (walker.nextNode()) nodes.push({ node: walker.currentNode, text: walker.currentNode.nodeValue });
    var clearReadme = function () { nodes.forEach(function (n) { n.node.nodeValue = ""; }); };
    var fillReadme = function () { nodes.forEach(function (n) { n.node.nodeValue = n.text; }); };

    readme.style.minHeight = readme.offsetHeight + "px";
    cmd.textContent = "";
    clearReadme();
    last.style.visibility = "hidden";
    cmd.after(cursor);

    // Re-measure once web fonts are in, if output hasn't started yet
    var started = false;
    (document.fonts ? document.fonts.ready : Promise.resolve()).then(function () {
      if (started) return;
      readme.style.minHeight = "";
      fillReadme();
      readme.style.minHeight = readme.offsetHeight + "px";
      clearReadme();
    });

    var typeCmd = function (i, done) {
      cmd.textContent = cmdText.slice(0, i);
      if (i < cmdText.length) setTimeout(function () { typeCmd(i + 1, done); }, 85);
      else done();
    };
    var typeReadme = function (n, i, done) {
      if (n >= nodes.length) return done();
      var cur = nodes[n];
      cur.node.nodeValue = cur.text.slice(0, i);
      if (i < cur.text.length) setTimeout(function () { typeReadme(n, i + 1, done); }, 6);
      else typeReadme(n + 1, 0, done);
    };

    setTimeout(function () {
      typeCmd(1, function () {
        setTimeout(function () {
          started = true;
          cursor.remove();
          typeReadme(0, 0, function () {
            last.appendChild(cursor);
            last.style.visibility = "";
            readme.style.minHeight = "";
          });
        }, 350);
      });
    }, 900);
  }
  // Media protection: block right-click, drag, long-press save and video download
  var isMedia = function (el) { return el && el.closest && el.closest("img, video, .lightbox"); };
  document.addEventListener("contextmenu", function (e) { if (isMedia(e.target)) e.preventDefault(); });
  document.addEventListener("dragstart", function (e) { if (isMedia(e.target)) e.preventDefault(); });
  document.querySelectorAll("img").forEach(function (img) { img.setAttribute("draggable", "false"); });
  document.querySelectorAll("video").forEach(function (v) {
    v.setAttribute("controlsList", "nodownload noplaybackrate");
    v.setAttribute("disablePictureInPicture", "");
  });

  // Full-size photos open in an in-page viewer instead of a raw image tab
  var links = document.querySelectorAll('a[href$=".jpg"], a[href$=".jpeg"], a[href$=".png"]');
  if (links.length) {
    var box = document.createElement("div");
    box.className = "lightbox";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
    box.innerHTML = '<button class="lightbox-close" aria-label="Close">&times;</button><img alt="" draggable="false">';
    document.body.appendChild(box);
    var big = box.querySelector("img");
    var close = function () { box.classList.remove("open"); big.removeAttribute("src"); document.body.style.overflow = ""; };
    box.addEventListener("click", function (e) { if (e.target !== big) close(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
    links.forEach(function (a) {
      a.addEventListener("click", function (e) {
        e.preventDefault();
        var thumb = a.querySelector("img");
        big.src = a.getAttribute("href");
        big.alt = thumb ? thumb.alt : "";
        box.classList.add("open");
        document.body.style.overflow = "hidden";
      });
    });
  }
});
