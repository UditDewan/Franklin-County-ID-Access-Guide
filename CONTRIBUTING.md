# How to work on this

Read this before changing anything in `content/`.

## The one thing to understand first

The hard work here is verification, not code. The tool is about 800 lines. The
research is a hundred phone calls. Wrong information in this repository does not
produce a bug report — it sends someone without bus fare across town to an office
that will not serve them. Assume that will happen if you are careless.

## Non-negotiable constraints

### 1. Zero data collection

No analytics, no cookies, no localStorage, no form POST, no third-party fonts or
scripts, no CDN calls. Everything ships from one origin. If a change would
introduce any network call after page load, it does not go in.

People using this tool are vulnerable, and some have specific safety reasons to
leave no trace. This is not a preference.

`tests/test_build.py::test_nothing_loads_from_anywhere_else` enforces it.

### 2. Every fact carries provenance

Content lives in YAML. Every node with a fact needs a `provenance` block:

```yaml
provenance:
  source_url: https://...        # https only
  verified_on: 2026-08-30        # a real date
  verified_by: A. Student        # a person
  confidence: phone              # desk | phone | confirmed
  note: >                        # optional, but use it
    Front desk, not a supervisor. Reconfirm at a second location.
```

The build fails on any node missing them. No exceptions, no override flag.

**Confidence levels:**

| level | means |
|---|---|
| `desk` | Taken off the agency's own website or form. Nobody has spoken to a person. |
| `phone` | One staff member confirmed it. |
| `confirmed` | Two independent contacts agree. Only these may be published. |

`python -m src.validate --publish` refuses anything below `confirmed`. Until every
fact clears that bar, the built page carries a draft banner and should not be
handed out. Requirements vary between deputy registrars in practice, and that
variance is itself worth writing down in the log.

### 3. Staleness is visible

Past 90 days, a fact renders with a warning on the page and appears in
`python -m src.reverify`. Past 180 days, the build fails.

The 180-day failure is harsh on purpose. A guide that will not rebuild is a guide
somebody has to look at. Agency fees and requirements change, and a confidently
wrong guide is worse than no guide.

### 4. Not legal advice

The tool describes documented agency requirements. It never advises on immigration
status, criminal records, custody, or benefits eligibility. If a change starts to
read like advice, stop and route the person to a caseworker instead.

Where a path has no clean answer under current law — no ID, no birth certificate,
born out of state — say so plainly and hand off. Do not invent steps to fill the
gap.

### 5. Plain language, sixth-grade target

- Reading level under grade 8 on `plain_summary` and `what_to_say`, measured with
  Flesch-Kincaid in CI.
- Sentences under 20 words.
- No agency jargon without a plain-English gloss. "Certified copy" is explained
  the first time it appears.

Short sentences do most of the work. If a sentence fails, split it in two.

### 6. Page weight budget: 100KB, uncompressed

Users are on phones, often on limited or metered data, sometimes on public wifi.
No web fonts. No framework. System font stack. The CSS and JavaScript are inlined
into the one HTML file, so the whole guide is a single request. The build fails
over budget.

## Adding or changing a fact

1. Make the call. Ask the question you actually need answered.
2. Write the call up in `research/verification-log.md`, in the format that file
   already uses. Every entry: date, agency, who called, method, question, answer,
   source URL, confidence.
3. Edit the YAML. Update `verified_on`, `verified_by` and `confidence`.
4. Run `python -m src.validate` and `python -m pytest`.
5. If the answer contradicts what was there, say so in the log. A change of
   answer between two offices is a finding for the barrier memo, not a nuisance.

Anything at `phone` confidence gets a second, independent contact before it is
published. Call a different office, or a different person.

## Adding a step

`content/steps/<id>.yaml`, then add it to `plan:` in `content/tree.yaml` with the
answers that should select it. Every path a person can click must end on a step
marked `terminal: true` (they are done) or `referral: true` (a person takes over).
The validator walks all 288 possible answer sets and fails if any path ends
anywhere else.

## Changing the questions

Six or seven questions is the ceiling. Every extra question loses people. If you
add one, cut one.

Quote every `label` and `value` in the YAML. Unquoted `Yes` and `No` are booleans
to YAML and would reach the page as "true" and "false". The validator catches it
now, but it shipped once.

## Stack

Python 3.11+, Jinja2, PyYAML, pytest, textstat. Output is one static HTML file
plus a printable sheet and a service worker. No framework, no bundler, no backend.

`static/plan.js` holds the rule that turns answers into steps. Python has the same
rule in `src/content.py`. `tests/test_parity.py` runs both over every possible
answer set and fails if they disagree, because a browser and a printout that
disagree would be worse than either alone.

## Before publishing

The checklist in `docs/HANDOFF.md` is the gate. Two direct-service organisations
review it, the Rep's office sees it, and every fact reaches `confirmed`. Not
before.
