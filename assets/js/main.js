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

  // Home terminal: type "cat README.md", then stream its output
  var cmd = document.querySelector(".term-body .cmd");
  var readme = document.querySelector(".term-body .readme");
  var last = document.querySelector(".term-body .last");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (cmd && readme && last && !reduce) {
    var cmdText = cmd.textContent;
    var outText = readme.textContent;
    var cursor = last.querySelector(".cursor");
    readme.style.minHeight = readme.offsetHeight + "px";
    cmd.textContent = "";
    readme.textContent = "";
    last.style.visibility = "hidden";
    cmd.after(cursor);

    var type = function (el, text, delay, done) {
      var i = 0;
      (function step() {
        el.textContent = text.slice(0, ++i);
        if (i < text.length) setTimeout(step, delay);
        else done();
      })();
    };
    (document.fonts ? document.fonts.ready : Promise.resolve()).then(function () {
      if (readme.textContent) return;
      readme.style.minHeight = "";
      readme.textContent = outText;
      readme.style.minHeight = readme.offsetHeight + "px";
      readme.textContent = "";
    });
    setTimeout(function () {
      type(cmd, cmdText, 85, function () {
        setTimeout(function () {
          cursor.remove();
          type(readme, outText, 6, function () {
            last.appendChild(cursor);
            last.style.visibility = "";
            readme.style.minHeight = "";
          });
        }, 350);
      });
    }, 900);
  }
});
