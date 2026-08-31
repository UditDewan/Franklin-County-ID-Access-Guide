// Runs the question flow. Answers live in this one object and nowhere else.
// No storage, no cookies, no network. Reloading the page wipes it.
(function () {
  "use strict";

  var data = JSON.parse(document.getElementById("tree-data").textContent);
  var questions = data.questions;
  var plan = data.plan;

  var tool = document.getElementById("tool");
  var fallback = document.getElementById("fallback");
  var quiz = document.getElementById("quiz");
  var results = document.getElementById("results");
  var stepsHome = document.getElementById("all-steps");

  var answers = {};
  var at = 0;

  function stepNode(id) {
    return document.getElementById("step-" + id);
  }

  function askQuestion() {
    var question = questions[at];
    quiz.textContent = "";

    var progress = document.createElement("p");
    progress.className = "progress";
    progress.textContent = "Question " + (at + 1) + " of " + questions.length;
    quiz.appendChild(progress);

    var fieldset = document.createElement("fieldset");
    var legend = document.createElement("legend");
    legend.textContent = question.text;
    fieldset.appendChild(legend);

    if (question.help) {
      var help = document.createElement("p");
      help.className = "help";
      help.textContent = question.help;
      fieldset.appendChild(help);
    }

    var choices = document.createElement("div");
    choices.className = "choices";
    question.options.forEach(function (option) {
      var button = document.createElement("button");
      button.type = "button";
      button.className = "choice";
      button.textContent = option.label;
      button.addEventListener("click", function () {
        answers[question.id] = option.value;
        at += 1;
        if (at < questions.length) {
          askQuestion();
        } else {
          showResults();
        }
      });
      choices.appendChild(button);
    });
    fieldset.appendChild(choices);
    quiz.appendChild(fieldset);

    if (at > 0) {
      var back = document.createElement("button");
      back.type = "button";
      back.className = "back";
      back.textContent = "Go back";
      back.addEventListener("click", function () {
        at -= 1;
        delete answers[questions[at].id];
        askQuestion();
      });
      quiz.appendChild(back);
    }

    var focusTarget = quiz.querySelector("legend");
    if (focusTarget) {
      focusTarget.setAttribute("tabindex", "-1");
      focusTarget.focus();
    }
  }

  function showResults() {
    var ids = planFor(plan, answers);
    quiz.hidden = true;
    results.textContent = "";

    var heading = document.createElement("h2");
    heading.textContent = "Your list, in order";
    heading.setAttribute("tabindex", "-1");
    results.appendChild(heading);

    var count = document.createElement("p");
    count.className = "lede";
    count.textContent =
      ids.length === 1
        ? "One thing to do. Start here."
        : ids.length + " things to do. Do them in this order.";
    results.appendChild(count);

    ids.forEach(function (id) {
      var node = stepNode(id);
      if (node) {
        node.hidden = false;
        results.appendChild(node);
      }
    });

    var again = document.createElement("button");
    again.type = "button";
    again.className = "back noprint";
    again.textContent = "Start over";
    again.addEventListener("click", function () {
      answers = {};
      at = 0;
      // Put the step cards back where they came from, hidden again.
      ids.forEach(function (id) {
        var node = stepNode(id);
        if (node) {
          node.hidden = true;
          stepsHome.appendChild(node);
        }
      });
      results.textContent = "";
      quiz.hidden = false;
      askQuestion();
    });
    results.appendChild(again);

    var print = document.createElement("button");
    print.type = "button";
    print.className = "back noprint";
    print.textContent = "Print this list";
    print.addEventListener("click", function () {
      window.print();
    });
    results.appendChild(print);

    heading.focus();
  }

  // Without JavaScript the page is already a readable list of every step, and
  // that list stays visible until the questions are actually on screen. If
  // anything below throws, the reader keeps a working page instead of a blank one.
  var cards = stepsHome.querySelectorAll(".step");
  for (var i = 0; i < cards.length; i++) {
    cards[i].hidden = true;
  }

  try {
    askQuestion();
    tool.hidden = false;
    fallback.hidden = true;
  } catch (e) {
    for (var j = 0; j < cards.length; j++) {
      cards[j].hidden = false;
    }
    throw e;
  }

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("sw.js").catch(function () {
      // Offline caching is a bonus. The page works fine without it.
    });
  }
})();
