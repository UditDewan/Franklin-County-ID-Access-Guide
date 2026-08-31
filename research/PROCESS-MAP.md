# The process, branch by branch

Status: **desk research complete, phone verification not started.**

Everything below came from agency websites and published forms. Nothing here has
been confirmed by a person at a counter. Treat every number as provisional until
`python -m src.reverify` comes back empty.

The exit criterion for Phase 0 is not "this document exists". It is: every branch
traced end to end, every node backed by at least one logged call, and nothing left
at `desk` confidence.

---

## The shape of the problem

To get an Ohio ID card you must prove five things:

1. Full legal name
2. Date of birth
3. Legal presence in the United States
4. Social Security number
5. Ohio street address

Elements 1 to 3 normally come off one document: a certified birth certificate.
Element 4 comes off a Social Security card, or a W-2, 1099 or pay stub showing the
whole number. Element 5 is the one that stops people, and it is worth being precise
about why.

Source: BMV form 2430, revision 5/25.

### Element 5 is where the guide earns its keep

A compliant (gold star) card requires **two** documents from **different sources**
showing an Ohio street address. A standard card requires one.

Reading the accepted list closely, **no shelter letter appears on it**. The BMV's
own certified statement form, BMV 2336, covers exactly three situations: a
dependent child whose parent or guardian has proof at the same address, a married
person whose spouse has proof at the same address, and a nursing home resident with
a statement from a nursing home official. A shelter cannot sign it. A friend cannot
sign it.

What *is* on the list, and is reachable by someone staying in a shelter:

- Social Security Administration document
- Public assistance benefits statement issued within the last 12 months
- Child support statement or account summary from ODJFS
- BMV postcard or correspondence
- Court order of probation, parole, or mandatory release
- Pay stub issued within the last 12 months
- Bank or credit union statement from the last 12 months
- Two utility bills from two different companies (these satisfy both proofs)
- School record or transcript
- Insurance card or policy, current

So the practical route is: get a mailing address, then get two government or
financial letters *mailed to it*. That is the sequence the tool teaches, and it is
the reason `mailing-address` comes before everything else in the plan.

**This is the single most important thing to confirm by phone.** If deputy
registrars in Franklin County accept shelter letters in practice, the guide should
say so and name which ones. If they do not, that is a finding for the barrier memo.

---

## Branch: born in Ohio

Any local vital statistics office in Ohio can print a certified copy of any Ohio
birth from 1908 onward. You do not have to travel to your birth county. Columbus
Public Health prints them while you wait at 240 Parsons Ave.

- Cost: $25 at Columbus Public Health. The state office quotes $25 in person.
  Local offices set their own price and the range statewide is roughly $17 to $28.
- Payment: check or money order to Columbus City Treasurer. **Whether cash is
  accepted is unconfirmed and matters enormously.** Ask this on every call.
- Identification required: **unconfirmed.** This is the circular point. Ask
  precisely: what does this office accept from someone with no photo ID at all?

Fee note for the memo: under ORC 3705.24 the state sets a floor, and separate
statutory add-ons of $1.50 and $5.00 ride on each certified copy. The LSC fiscal
note on HB 472 described a local board of health charging $25 keeping $11.50 and
forwarding $13.50 to the state. Confirm the current split before quoting it in
testimony.

## Branch: born out of state

Ohio offices cannot issue another state's record. The applicant has to deal with
the state of birth, usually by mail, usually with a photo ID requirement of that
state's design.

The guide links the federal *Where to Write for Vital Records* directory rather
than publishing per-state fees, because a wrong fee sends someone to the post
office with the wrong money order. The five states listed in `content/states.yaml`
are a **guess**. Ask shelter intake staff which birth states they actually see, and
replace that list with real numbers.

This branch is marked `referral: true`. It is honest about needing a caseworker.

## Branch: not sure where you were born

No clean path. The guide says so and routes to the Homeless Hotline and a case
manager. Do not invent steps here.

## Branch: no ID and no birth certificate at all

The genuinely circular case. The chain that appears to work:

1. Mailing address (shelter, or someone willing to receive mail).
2. Birth certificate — **blocked on the identification question above.** If an
   Ohio office will issue with no photo ID, the chain works. If not, the person
   needs an SSA or benefits document first, which itself usually needs identity
   evidence.
3. Social Security card, using the birth certificate.
4. Two address documents, mailed to the address from step 1.
5. BMV.

Until step 2 is answered by a human, the guide cannot promise this path works.
That single question is the highest-value call in the whole project.

## Branch: under 18

Different rules, different fees, usually a parent or guardian signature that is
not always available. Not mapped. The guide routes to Star House, which works with
people aged 14 to 24 daily. Map this properly before publishing.

## Branch: name changed since birth

The BMV wants the paper that connects the birth name to the current name: a
marriage licence, a divorce or dissolution decree, or a court name change order —
one for each change. Certified copies come from the court that issued them.

The guide describes the paperwork and nothing else. Gender marker changes, sealed
records and custody questions go to legal aid, not to this tool.

---

## Fees, as currently understood

| Item | Amount | Confidence |
|---|---|---|
| Ohio state ID card, applicant 17+ with no driver licence | $0 | desk, two sources, conflicting page |
| Ohio state ID card, listed fee if charged | $13 new / $25 renewal / $12 duplicate | desk |
| Certified Ohio birth certificate, Columbus Public Health | $25 | desk |
| Certified Ohio birth certificate, state office in person | $25 | desk |
| Replacement Social Security card | $0 | desk |

The ID card fee needs resolving at a counter. Two sources say the card is free for
Ohioans 17 and over without a driver licence, effective April 2023. The BMV's own
fee page still prints dollar amounts beside a note about free issuance. A person
budgeting bus fare deserves a straight answer.

---

## Open questions, in priority order

1. What does an Ohio vital statistics office accept as identification from
   someone with no photo ID? Ask Columbus Public Health, Franklin County Public
   Health, and the state office separately. Expect different answers.
2. Does any Franklin County deputy registrar accept a shelter letter as proof of
   address? Ask at least four. Record which ones and in exactly what form.
3. Is the ID card actually free for 17+ with no driver licence, at the counter,
   today?
4. Does Columbus Public Health take cash?
5. Which local programme, if any, pays birth certificate fees this year? The
   guide currently only says "ask", which is weak.
6. Which shelters will hold mail, and for how long after someone leaves?
7. Does Franklin County Public Health issue birth certificates at all, and from
   what address? The entry was withdrawn on 2026-08-31 because three different
   addresses surfaced and none came from the agency. See the verification log.
8. What birth states do shelter intake staff actually see?
9. Under-18 process, end to end.
10. What does SSA accept in Columbus when someone has no photo ID?

---

## How to run the calls

Two or three people, one week, working from `python -m src.reverify`. It prints
the fact, the reason it needs a call, the number to dial and the question to ask.

Write every call into `research/verification-log.md` before touching the YAML. The
log is the audit trail that makes this guide trustworthy, and it is also the raw
material for the barrier memo — especially the calls where two offices that should
be identical give different answers.
