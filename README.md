# Franklin County ID Access Guide

A static, privacy-preserving tool for people with no fixed address in Franklin
County, Ohio who need a state ID card or a certified birth certificate. It asks
seven questions and returns an ordered checklist: what to bring, where to go,
what it costs, how long it takes, and what to say at the counter.

There is a second output: a one-page sheet shelters and Rep. Cockley's District 6
office can print and hand out.

## Status

**Draft. Not for distribution.** Every fact in `content/` currently comes from an
agency website, not from a person who confirmed it. The build says so on the page,
in a banner, and `python -m src.validate --publish` refuses to pass until each
fact has two independent confirmations. The phone calls are Phase 0 of
[the process map](research/PROCESS-MAP.md), and they are the real work here.

## Why it exists

HB 472 would have waived the fee for one certified birth certificate a year for
people verified as experiencing homelessness. It passed the House with bipartisan
support, was replaced in Senate committee by a substitute bill loaded with
unrelated voter-ID provisions, moved in 48 hours, and was vetoed in June 2026.

The bill is dead. The circular requirement it targeted is not: you need a birth
certificate to get an ID, identification to get a birth certificate, and money for
both. This repository is the navigation aid, and
[research/BARRIER-MEMO.md](research/BARRIER-MEMO.md) is the evidence file for
whoever reintroduces it.

## Running it

```
pip install -r requirements.txt

python -m src.validate      # schema, staleness, reading level, tree
python -m src.build         # writes public/
python -m pytest            # 63 tests
python -m src.reverify      # the call list: which facts need a phone call
```

`public/` is a static site. Open `public/index.html` in a browser, or serve it
with `python -m http.server -d public` to exercise the service worker.

## What is in here

```
content/agencies.yaml       offices, addresses, hours, phones
content/documents.yaml      what the BMV takes as proof, and what it does not
content/states.yaml         out-of-state birth records
content/steps/*.yaml        one file per step in the guide
content/tree.yaml           the questions, and the rules that pick steps
research/PROCESS-MAP.md     the process, branch by branch, and what is unknown
research/verification-log.md  every check: who, when, what was said
research/BARRIER-MEMO.md    what the process costs a person, itemised
docs/HANDOFF.md             who owns this, and who owns it next
src/validate.py             every check that can fail the build
src/build.py                YAML to static site
src/reverify.py             the recurring phone-call checklist
static/plan.js              the answer-to-steps rule, shared with the browser
templates/                  the page and the printable sheet
tests/                      including a Python/JavaScript parity check
public/                     build output, not committed
```

## The rules this repository enforces on itself

These are checked, not just written down. See
[CONTRIBUTING.md](CONTRIBUTING.md) for the reasoning.

- **No data leaves the device.** No analytics, cookies, storage, fonts, CDNs or
  form posts. `tests/test_build.py` fails the build if any appear.
- **Every fact carries a source, a date, a person, and a confidence level.**
  Missing any of them fails the build. There is no override flag.
- **Facts go stale visibly.** Past 90 days a warning renders on the page. Past
  180 days the build fails outright.
- **Plain language.** Reading level under grade 8, sentences under 20 words,
  checked in CI.
- **Under 100KB.** One HTML file, no framework, no web fonts. It is about 40KB.
- **It works with JavaScript off**, and offline after the first visit.

## Not legal advice

The guide describes documented agency requirements and nothing else. It does not
advise on immigration status, criminal records, custody, or benefits eligibility.
Where there is no clean path, it says so and routes to a caseworker rather than
inventing steps.
