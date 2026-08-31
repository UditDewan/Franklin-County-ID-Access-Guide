# Getting an ID with no fixed address in Franklin County: what it costs and where it breaks

Draft, 2026-08-30. Prepared alongside the Franklin County ID Access Guide.

**Every figure below is desk-verified only.** Sources are agency websites and
published forms; none has yet been confirmed by a person at a counter. The
verification log records exactly what was checked and how. Nothing here should be
used in testimony until `python -m src.reverify` returns an empty list.

This memo documents a process. It does not argue a position. The documentation is
the argument.

---

## 1. Summary

A person in Franklin County with no fixed address, no photo identification and no
birth certificate faces a sequence of four or five separate in-person or by-mail
transactions before they hold a state ID card. The binding constraint is not the
fee. It is proof of an Ohio street address, and the fact that the accepted-document
list has no entry a shelter can satisfy.

The fee that HB 472 would have waived is real and it matters. It is not the part of
the process that stops people first.

## 2. Total cost, by path

| Path | Birth certificate | SS card | ID card | Total |
|---|---|---|---|---|
| Born in Ohio, has birth certificate and SS card | $0 | $0 | $0 | **$0** |
| Born in Ohio, needs birth certificate | $25 | $0 | $0 | **$25** |
| Born in Ohio, needs birth certificate and SS card | $25 | $0 | $0 | **$25** |
| Born out of state, needs birth certificate | varies by state | $0 | $0 | **$25 or more, plus postage and a money order fee** |

Notes on the figures:

- **$25** is Columbus Public Health's charge per certified copy. Local health
  departments across Ohio set their own price; the observed range is roughly $17
  to $28.
- **The ID card appears to be free** for applicants 17 and over who do not hold a
  driver licence, effective April 2023. The BMV fee page simultaneously lists
  $13.00 new, $25.00 renewal and $12.00 duplicate beside a note about free
  issuance. This ambiguity needs resolving; it is the difference between a trip a
  person can afford and one they cannot.
- **Replacement Social Security cards are free.**
- Out-of-state records carry their own fee plus the practical cost of a money
  order and postage, since most states will not take cash by mail.

Costs not on the fee schedule and not usually counted: bus fare for each trip,
hours of work missed, and a money order fee for anyone without a bank account.

## 3. Number of separate trips

Best case, born in Ohio with a birth certificate and a Social Security card
already in hand: **one trip** to a deputy registrar.

Typical case, born in Ohio with neither document and no address proof:

1. Shelter intake or hotline call, to establish somewhere mail arrives.
2. Vital statistics office, in person, for the birth certificate.
3. Social Security office, in person, for the card. Most offices ask for an
   appointment.
4. A wait of one to three weeks while address documents are mailed.
5. Deputy registrar, for the ID.

**Four in-person trips and a mail wait**, and that assumes nothing goes wrong.

Born out of state, the birth certificate trip becomes a mail transaction with
another state's records office, adding two to eight weeks and requiring a mailing
address that will still be good when the envelope arrives.

## 4. Where the circular requirements are, precisely

There are two, and they are different in kind.

### 4.1 The document circle

To get an Ohio ID you need a certified birth certificate. To get a certified birth
certificate, offices generally ask for identification. Whether an Ohio vital
statistics office will issue to someone with no photo ID at all is **the single
unresolved question** in the process map, and the guide cannot promise the
no-ID path works until it is answered.

If the answer is no, the circle is closed under current practice, and the only exit
is a caseworker with a relationship at a specific office.

### 4.2 The address circle, which is the harder one

BMV form 2430 requires two documents from different sources showing an Ohio street
address for a compliant card, one for a standard card. Reading the accepted list in
full:

- No shelter letter appears on it.
- BMV form 2336, the "certified statement" of Ohio residency, covers exactly three
  situations: a dependent child whose parent or guardian holds proof at the same
  address, a married person whose spouse holds proof at the same address, and a
  nursing home resident with a statement from a nursing home official.
- A shelter cannot sign that form. A friend housing someone cannot sign it either.

So a person staying in a shelter cannot prove residency by saying where they stay.
They can only prove it by having a bank, an employer, a utility, a court, or a
government agency **mail them something**, which requires already having an address
where mail is held, and in several cases requires the identification they are
trying to obtain.

The workable route the guide teaches — Social Security documents, public assistance
statements, ODJFS child support statements, probation or parole orders, BMV
correspondence — exists, but it takes weeks and it is invisible unless someone
reads the acceptable-documents list line by line. Most people do not. They bring a
shelter letter, get turned away, and the trip is wasted.

A nursing home resident has an accommodation written into the form. A shelter
resident does not.

## 5. Paths with no clean solution under current practice

1. **No photo ID, no birth certificate, born out of state.** Requires satisfying
   another state's identity requirements by mail, with no identity documents. The
   guide marks this as a referral and does not pretend otherwise.
2. **Birthplace unknown.** No documented path. Referral only.
3. **Under 18 with no available parent or guardian.** Not mapped; routed to Star
   House, which handles these cases directly.

The guide's own design rule is that where there is no clean path it says so, rather
than inventing steps. Two of its ten pages stop and hand the person to a
caseworker, and a third says plainly that the out-of-state route needs one.

## 6. Where practice varies between offices that should be identical

Two places, both worth documenting with dates and office names once the calls are
made:

- **Deputy registrars.** Requirements are set statewide, but which documents get
  accepted in practice varies by office. The guide tells people that if they are
  turned away they should record what was said and try another office, which is
  advice no guide should have to give.
- **Vital statistics offices.** Fees differ by health department by statute. Whether
  cash is accepted, and what identification is required, appears to differ too.

This variance is itself a finding. When the rule is uniform and the experience is
not, the difference is absorbed by the person with the least ability to absorb it.

## 7. What HB 472 would and would not have fixed

**Would have fixed:** the $25 fee for one certified birth certificate a year, for
people verified as experiencing homelessness. For the Ohio-born applicant who can
already prove an address, that is the whole barrier, and the bill would have
removed it.

**Would not have fixed:**

- The address-proof requirement, which is the earlier and harder obstacle.
- The absence of any shelter equivalent to the nursing home provision on BMV 2336.
- The identification required to *request* a birth certificate — the document
  circle in section 4.1.
- Out-of-state birth records, which Ohio cannot waive fees on.
- The number of separate trips, which is what actually consumes a person's week.

**What the record shows about the bill:** it passed the House with bipartisan
support. A substitute bill was introduced in Senate committee without the joint
sponsors' knowledge or consent, carrying unrelated absentee-voter-ID provisions,
and moved through the legislature in 48 hours. The Governor vetoed the resulting
bill in June 2026. The fee waiver died with provisions it was never written
alongside.

## 8. Suggested lines of inquiry for reintroduction

Offered as observations from the process, not as recommendations.

1. A fee waiver alone leaves the address barrier untouched. Anyone reintroducing
   the waiver may want to know that the people it is written for will often be
   stopped one step earlier.
2. BMV form 2336 already contemplates certified statements of residency from a
   third party — a parent, a spouse, a nursing home official. A shelter is not on
   that list. Adding one would be a change to an existing mechanism rather than a
   new one.
3. The identification required to request a birth certificate is set by rule and
   by local practice, not only by statute, and appears to vary between offices.
4. Uniform practice across deputy registrars would remove a category of wasted trip
   that costs the state nothing to fix.

## 9. What has to happen before this memo is usable

Everything in the process map's open-questions list. In particular: whether an
Ohio vital statistics office will issue to someone with no photo ID, whether any
Franklin County deputy registrar accepts a shelter letter, and whether the ID card
is in fact free today. Three phone calls, and the memo either holds or changes
materially.
