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

  // Gallery: fold past years behind a "Show N events" button
  document.querySelectorAll(".gallery-fold").forEach(function (g) {
    var n = g.children.length;
    var label = "Show " + n + (n === 1 ? " event" : " events");
    g.classList.add("collapsed");
    var btn = document.createElement("button");
    btn.className = "news-toggle gallery-fold-toggle";
    btn.textContent = label;
    btn.addEventListener("click", function () {
      var collapsed = g.classList.toggle("collapsed");
      btn.textContent = collapsed ? label : "Show less";
    });
    g.after(btn);
  });

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
