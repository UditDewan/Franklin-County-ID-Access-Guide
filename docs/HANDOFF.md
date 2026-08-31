# Handoff

## Who owns this

| Semester | Owner | Contact |
|---|---|---|
| Autumn 2026 | **unassigned** | — |
| Spring 2027 | **unassigned** | — |

**If nobody will own it, take the site down.** An outdated guide that sends
someone to a closed office is worse than no guide. That is not a figure of speech
and it is not a decision to defer: taking it down is the correct action, and the
build is designed to force the question by failing at 180 days.

## What the owner actually has to do

Two hours a quarter, plus watching one inbox.

1. **Weekly, automatically.** A GitHub Action runs `src.reverify` and opens an
   issue listing every fact past 90 days. The issue is the reminder. It carries the
   phone numbers and the question to ask at each one.
2. **When that issue appears.** Work the list. Log each call in
   `research/verification-log.md`, then update `verified_on`, `verified_by` and
   `confidence` in the YAML. Open a pull request.
3. **If the build starts failing.** Something crossed 180 days. Fix it or take the
   site down. There is no flag to silence it, on purpose.
4. **At the end of a semester.** Name the next owner in the table above, or sunset.

## Before this is published at all

None of these are done yet.

- [ ] Every fact at `confirmed` confidence, meaning two independent contacts.
      `python -m src.validate --publish` passes.
- [ ] The open questions in `research/PROCESS-MAP.md` are answered, especially:
      what identification a vital statistics office requires from someone with
      none, and whether any deputy registrar takes a shelter letter.
- [ ] Reviewed by at least two direct-service organisations. Community Shelter
      Board and one shelter that runs an intake desk are the obvious candidates.
      Ask a caseworker to walk the tool aloud. Ask what is wrong, what is missing,
      and what would make them hand it to a client. Budget a full week for the
      revisions, and expect to be told something is wrong.
- [ ] Routed to Rep. Cockley's District 6 office. They may want to be listed as a
      contact, or may want distance from a volunteer product. Ask; do not assume.
- [ ] `SITE_URL` in `src/build.py` set to the real address before printing
      anything. It is currently a placeholder and it appears on the handout.
- [ ] One person navigates every path on a phone in under three minutes.
- [ ] The printed sheet checked on paper, not on screen.
- [ ] Screen reader pass on the question flow.

## Deploying

The output is static. GitHub Pages or Netlify, publishing `public/`. No backend,
no database, nothing to patch, no cost.

```
python -m src.validate --publish
python -m src.build
```

`public/.nojekyll` is written by the build so Pages serves the files as they are.

If the site moves, update `SITE_URL` in `src/build.py`, since it is printed on the
handout that shelters keep on a desk for months.

## What was handed over

1. The tool, at a stable URL.
2. Printable one-page sheets, as PDFs the office can print without help. Print
   `public/print.html` to PDF; the stylesheet is designed for US Letter.
3. `research/BARRIER-MEMO.md`.
4. `research/verification-log.md`, the audit trail that makes the guide
   trustworthy.
5. This file, with a named owner.
6. A walkthrough for the office, and one for a shelter's front-line staff if they
   will have you.

## Things a new owner will want to know

- The content is YAML in `content/`. You almost never need to touch Python.
- `python -m src.reverify` prints the call list. Start there.
- `CONTRIBUTING.md` explains the constraints and why each one exists. The privacy
  rules in particular are not preferences, and they are enforced by tests.
- The rule that turns answers into a list of steps lives in two places, Python and
  JavaScript, and `tests/test_parity.py` proves they agree. If you change one,
  change both, and the test will tell you if you forgot.
- Two pages stop dead and hand the person to a caseworker: under 18, and
  birthplace unknown. A third, out-of-state births, warns that it needs one. Do
  not fill these in with plausible-sounding steps. If you learn the real answer,
  log the call first.
