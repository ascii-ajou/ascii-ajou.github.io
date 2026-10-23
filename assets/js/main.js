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
});
