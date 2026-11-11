# Editorial lesson template (proposal — not a published lesson)

**Status:** Draft for user review. This is an editorial specification, not Elementary 1A content. Use the blank page structure in `governance/lesson_page_skeleton.md` and metadata rules in `curriculum/lesson_metadata.schema.json`.

## Identity and source
- Stable ID: `<level>.unit_<NN>.lesson_<letter>`
- Book crosswalk: edition, unit, A/B/C, source URL/location and whether the original user-provided index was directly verified
- Origin per topic: `source_index_confirmed`, `program_extension` or `pending_source`
- Editorial status and content revision
- Prerequisite IDs and review tags
- CEFR: provisional band or exact descriptor citation only when verified; this is not certification
- Six skills, three to six measurable learning outcomes, `writing_outcome`, oral activities, content version and stable review tags

## Learning outcomes
Write three to six learner-observable outcomes, each beginning with an action verb such as *identify*, *ask*, *respond*, *write*, *distinguish*, or *use*. Specify the context and expected performance. Do not confuse a lesson objective with a certified CEFR level.

## Lesson page structure
1. **At a glance** — goals, prerequisites, time-independent roadmap, source/extension labels.
2. **Core idea / Concepto clave** — two concise sentences: accessible English and accurate Spanish.
3. **Grammar explained** — meaning, form, affirmatives/negatives/questions where applicable, subjects, contrasts, exceptions, Spanish-speaker traps.
4. **Natural examples** — everyday first, optional tech/work only when appropriate; note register.
5. **Vocabulary in context** — meanings, chunks, collocations and learner-useful phrases.
6. **Visual explainer** — optional; add only if it improves comprehension. Alt text must convey its purpose; use original assets.
7. **Everyday English** — common contractions, high-frequency modals/phrasal verbs when level-appropriate; explain use, do not overload.
8. **Self-study practice** — progressively scaffolded, at most 20 original grammar items per grammar topic; separate writing prompt.
9. **Answer rationale** — reasons and genuinely acceptable alternatives for ungraded items.
10. **Writing** — one concise application and optional extension with checklist.
11. **Interactive tutor handoff** — concrete speaking, listening and pronunciation prompts; no official graded test or private learner results on the public page.
12. **Recap and next step** — quick-reference table, review tags and relevant internal links.

## Visual design contract
- Use consistent MkDocs Material headings, modest admonitions and succinct tables.
- Preserve clear typography and mobile legibility; avoid decorative image filler.
- Use purpose-driven diagrams (timeline, spatial contrast, sequence) when they beat prose.
- Images require informative `alt`, source/origin and accessible contrast.
- Examples are original, contemporary, and at Elementary use beginner-friendly language.
- Explain accepted alternatives; do not publish official assessment banks.
- Do not display source scans, textbook graphics, learner grades, chats or recordings.

## Separation of student-facing content and internal editorial metadata

- Keep `lesson_id`, `editorial_status`, `content_version`, source provenance and private asset references in the Markdown **front matter** and in `curriculum/master_syllabus.yaml`. Do not display them as a metadata banner or editorial footnote in the learner's article.
- Use the original lesson code in navigation: `1A — Welcome to the class`. Never append `(Draft)` or describe an already-published page as unapproved or unavailable.
- Learner-facing references may credit *English File Fourth Edition* by title and explain that our material is original, without listing private image filenames, SHA-256 values, branch names or PR numbers.
- Draft lessons can retain `in_review` in metadata while the PR is **Draft**; before changing the PR to **Ready for review**, synchronize curriculum and page front matter to `published` and remove obsolete notices. `course-quality` enforces this release gate on ready-for-review PRs and on `main`.
- Never put unapproved lesson pages on the publicly deployed `main` branch. Academic words such as *review*, *practice*, and *assessment* remain legitimate student prose.

## Gate before publication
- [ ] Source lesson mapping checked against accessible cited index; record if original user-provided image remains pending, and never misrepresent the evidence.
- [ ] Lesson metadata passes schema and links follow the stable IDs.
- [ ] Bilingual anchor and natural examples reviewed.
- [ ] Exercises and explanations checked for ambiguity.
- [ ] Speaking/listening/pronunciation handoff exists.
- [ ] Images are original, legible and accessible (if used).
- [ ] Automated checks and strict MkDocs build pass.
- [ ] User has expressly approved merge/publication.
