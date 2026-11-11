# Elementary editorial production plan — proposal

**Status:** Editorial production proposal, updated after 1A/1B publication. Not authorization to approve or publish other lessons.

## Current coverage

- **Published:** Elementary 1A and 1B, both merged and deployed. Their structure is a provisional benchmark.
- **In review:** No Elementary lesson at the time of this update.
- **Pending:** Elementary 1C and later Elementary lessons, including future Practical English and Revise and Check sections.

## Production stages

1. **1B calibration (completed):** indexed scope, exercises, writing scaffolding, oral handoff, browser verification and user approval preceded the published merge.
2. **Calibrate 1C individually:** check its possessive-adjective, classroom-language and pronunciation scope, respecting 1A–1B prerequisites; request independent user approval.
3. **After Unit 1:** plan the full next unit (source map, prerequisites, objectives, vocabulary, pronunciation, review) but still author and approve lessons one by one. No bulk publication.
4. **Later Elementary:** proceed through the 12 source-indexed units A/B/C. Do not fill gaps with textbook claims without the original source.

## Editorial quality standard

- Reuse Understand → Examples → Check → Continue, bilingual anchors, natural examples, contrasts, common Spanish-speaker pitfalls, optional study breaks, self-study answer explanations, three-stage Writing, oral tutor handoff and quick reference.
- Calibrate length and exercise count by topic; at most 20 original grammar exercises **per topic**, not an arbitrary fixed quota.
- Add original SVGs/images only when a concept benefits, with accessible alt and equivalent prose.
- Require source metadata, valid prerequisites, link and image checks, strict MkDocs build, required PR course-quality, and a real browser rendering test of each new lesson across desktop and mobile light/dark. Generalize visual automation before subsequent units.

## Coverage and feedback

- Maintain an editorial coverage ledger: source-confirmed, planned, in-review, approved, published. Track PR, source reference, and validation run separately from learning progress.
- Collect **de-identified, aggregate** observations from English Learning Program: misconceptions, confusing examples, missing scaffolding, and accessibility issues. No individual grades, chats, transcripts or recordings go in the public repo.
- Classify issues as content, visual/technical or tutor-interaction; propose changes through new feature branches and PR review. Do not silently rewrite approved material.
- Continue development independent of the learner's pace, but publish only after explicit editorial sign-off.

## Release gate

A new lesson starts in a Draft PR. The user reviews and approves the exact version; Squash into protected main only after passing checks. Verify GitHub Pages Action after merge. Preparing future lessons does not imply permission to publish them.
