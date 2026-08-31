# Verification log

Every check that put a fact into `content/`, newest last.

Format for each entry: date, agency, who did it, method, question, answer, source
URL with the date it was read, and a confidence level. Anything at `desk` or
`phone` confidence needs a second independent contact before it is published.

**No phone calls have been made yet.** Everything below is a desk check against an
agency's own website or published form. That is the starting position, not the
finish line. See `research/PROCESS-MAP.md` for the call list in priority order.

---

## 2026-08-30 — Ohio BMV, acceptable documents

Checked by: project team
Method: desk check of BMV form 2430, revision 5/25, read in full
Question: What proves an Ohio street address, and is a shelter letter on the list?
Answer: Two documents from different sources are required for a compliant card.
        The accepted list includes an SSA document, a public assistance benefits
        statement, an ODJFS child support statement, BMV correspondence, a court
        order of probation or parole, a pay stub, a bank statement, utility bills
        (two different providers satisfy both proofs), school records and current
        insurance. **No shelter letter appears anywhere on the list.** The BMV 2336
        certified statement covers only a dependent child, a spouse at the same
        address, or a nursing home resident.
Source URL: https://dam.assets.ohio.gov/image/upload/publicsafety.ohio.gov/bmv2430.pdf
        (read 2026-08-30)
Confidence: desk. The document is authoritative, but practice at the counter is
        the thing that matters. Confirm at four deputy registrars before publishing.

## 2026-08-30 — Ohio BMV, standard versus compliant card

Checked by: project team
Method: desk check, Disability Rights Ohio voter guide, cross-read against BMV 2430
Question: How many address documents does a non-compliant card need?
Answer: One. The two-document rule applies to the compliant card used for air
        travel. This matters: a person who can produce one address document can
        still get an ID.
Source URL: https://www.disabilityrightsohio.org/assets/documents/obtaining-a-state-id-card-in-ohio.pdf
        (read 2026-08-30)
Confidence: desk. Second-hand source. Confirm with the BMV directly.

## 2026-08-30 — Ohio BMV, ID card fee

Checked by: project team
Method: desk check of the BMV fees page
Question: What does a state ID card cost?
Answer: The fee table lists $13.00 new, $25.00 renewal, $12.00 duplicate, beside a
        note reading "New/Renewal/Duplicate for 17 and older or permanently
        disabled free of charge." A second source states cards became free on
        2023-04-07 for Ohioans over 17 without a driver licence.
Source URL: https://www.bmv.ohio.gov/doc-fees.aspx (read 2026-08-30)
Confidence: desk, and **contradictory on its face**. The page can be read two ways.
        Ask at a counter. Someone budgeting bus fare needs a straight answer.

## 2026-08-30 — Columbus Public Health, Office of Vital Statistics

Checked by: project team
Method: desk check of the city service page and the certificate application form
Question: Address, hours, fee, payment, and what identification is required?
Answer: 240 Parsons Ave, Columbus OH 43215. 614-645-7331. Monday to Friday 8:00am
        to 4:15pm, Wednesday opening at 9:00am. $25 per certified copy, by check or
        money order payable to Columbus City Treasurer. Issues certificates for any
        Ohio birth from 1908 to the present, not only Franklin County births.
Source URL: https://www.columbus.gov/Services/Public-Health/Get-a-Birth-or-Death-Certificate
        (read 2026-08-30)
Confidence: desk. **The identification requirement was not answered by the page.**
        That is the most important open question in the project. Also ask whether
        cash is accepted.
Note: columbus.gov blocks automated requests, so the link checker cannot see this
        page. A person has to open it.

## 2026-08-30 — Ohio Department of Health, Bureau of Vital Statistics

Checked by: project team
Method: desk check, state vital statistics ordering pages and secondary reporting
Question: Fee, hours, address, and whether local offices can issue any Ohio birth?
Answer: In-person orders quoted at $25, payable by cash, money order or personal
        check, with an Ohio licence or ID required to pay by personal check. State
        office at 4200 Surface Rd, Columbus, open to walk-ins 10:00am to 2:00pm.
        More than 100 local offices offer same-day in-person service for any Ohio
        birth.
Source URL: https://odh.ohio.gov/know-our-programs/vital-statistics/How-to-Order-Certificates/VS-How-to-Order-Certificates
        (read 2026-08-30)
Confidence: desk, and weaker than the others. The ODH site blocks automated
        requests entirely, so parts of this came from secondary reporting. Confirm
        the fee and hours by phone before publishing, and correct the URL if it has
        moved.

## 2026-08-31 — Franklin County Public Health: entry withdrawn

Checked by: project team
Method: desk check, repeated
Question: What is the address, phone and fee for vital statistics at FCPH?
Answer: **Not established.** An earlier draft of this guide carried 280 E Broad St
        and 614-525-3160. Neither came from the agency, and neither could be
        confirmed on a second pass. Searching turned up a different office
        entirely, at 373 S High St (18th floor in one listing, 22nd in another),
        with 614-525-3894 attached to it via the county probate court's adoption
        forms. Three addresses, two floors, no agency source.
Action: The agency was removed from `content/agencies.yaml` and from the
        birth certificate step. The guide now sends people to Columbus Public
        Health and the state office, both of which are sourced and both of which
        can issue any Ohio birth record.
Source URL: https://myfcph.org/ (read 2026-08-31)
Confidence: n/a — nothing published.
Note: Put this back only after somebody calls FCPH and confirms whether they
        issue birth certificates at all, and at what address. A wrong address in
        this file costs a person a bus fare and an afternoon.

## 2026-08-30 — Social Security Administration

Checked by: project team
Method: desk check of the SSA replacement card pages
Question: What does a replacement card cost, and what identification is needed?
Answer: No fee. One document proving identity is required, an original or a copy
        certified by the issuing agency. Photocopies and notarised copies are not
        accepted. Field offices assess secondary documents case by case.
Source URL: https://www.ssa.gov/number-card/replace-card (read 2026-08-30)
Confidence: desk. ssa.gov blocks automated requests. Ask the Columbus office what
        it accepts in practice from someone with no photo ID.

## 2026-08-30 — Community Shelter Board, Homeless Hotline

Checked by: project team
Method: desk check
Question: How does someone reach a shelter bed in Franklin County?
Answer: Through the Homeless Hotline, 614-274-7000, staffed 24 hours. Shelter
        services listed include help getting identification.
Source URL: https://www.csb.org/ (read 2026-08-30)
Confidence: desk. Ask which shelters hold mail, in what form, and for how long
        after someone leaves.

## 2026-08-30 — Star House

Checked by: project team
Method: desk check
Question: Who helps people under 25, and where?
Answer: Drop-in centre at 1220 Corrugated Way, Columbus OH 43201, 614-826-5868,
        open 24 hours, for people aged 14 to 24. Services listed include help
        obtaining ID cards.
Source URL: https://www.starhouse.us/ (read 2026-08-30)
Confidence: desk.

## 2026-08-30 — LSS Faith Mission

Checked by: project team
Method: desk check
Question: Location and whether case managers help with documents?
Answer: 245 N Grant Ave, Columbus OH 43215, 614-224-6617. Listed services include
        case management and employment readiness.
Source URL: https://www.lssnetworkofhope.org/faithmission/ (read 2026-08-30)
Confidence: desk. Confirm whether case managers help with documents specifically,
        and whether any fund covers certificate fees this year.

## 2026-08-30 — Deputy registrar locations

Checked by: project team
Method: desk check
Question: Which Franklin County deputy registrar offices should the guide list?
Answer: None individually. A location surfaced in search had already closed. The
        guide points at the state locator instead, plus the BMV line 844-644-6268.
Source URL: https://publicsafety.ohio.gov/local-office (read 2026-08-30)
Confidence: desk. Deliberate decision: a stale address is worse than a locator.
        Revisit once the team has confirmed specific offices by phone, and list
        those with the date confirmed.

## 2026-08-30 — Link check note

Checked by: project team
Method: automated HEAD requests against every `source_url`
Answer: bmv.ohio.gov and dam.assets.ohio.gov respond normally. columbus.gov,
        cdc.gov, ssa.gov and lssnetworkofhope.org return 403 to automated
        requests. odh.ohio.gov returns 404 to automated requests at every path
        tried, including its own root.
Confidence: n/a. Recorded so nobody wastes an afternoon on it: `--check-links`
        reports these as warnings, not failures, and the pages are fine in a
        browser. Any genuinely dead link has to be caught by a human opening it.
