// The one rule the whole tool turns on: which steps a set of answers produces.
// Kept apart from the page so a test can run it against the Python version and
// prove the two agree. If they ever disagree, somebody gets sent to the wrong
// office, so tests/test_parity.py compares them on every possible answer set.
function planFor(plan, answers) {
  var chosen = [];
  for (var i = 0; i < plan.length; i++) {
    var entry = plan[i];
    var when = entry.when || {};
    var match = true;
    for (var key in when) {
      if (Object.prototype.hasOwnProperty.call(when, key)) {
        if (when[key].indexOf(answers[key]) === -1) {
          match = false;
          break;
        }
      }
    }
    if (match) {
      chosen.push(entry.step);
      if (entry.stop_after) break;
    }
  }
  return chosen;
}

if (typeof module !== "undefined") {
  module.exports = planFor;
}
