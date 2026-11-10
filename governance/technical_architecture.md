# English Learning Program — Technical Architecture

**Version:** 1.2.0 (implementation status reviewed 2026-11-10; changes in PR #1 remain unapproved until merged)

## 1. System boundary

Two **ChatGPT Projects** share the learning curriculum but perform distinct jobs:

| Project | Primary responsibility | Writes to |
|---|---|---|
| `English Course Development` | Editorial workflow, curriculum maintenance, original lessons, images and non-graded self-study exercises | Public course repository, after user-approved review |
| `English Learning Program` | Tutor modes Learn/Practice/Conversation/Assessment; six-skill evidence and spaced reviews | Private progress repository, with permission and successful commit verification |

**GitHub repo A:** `english-learning-course`, **public**; static learning site deployed with GitHub Pages, using MkDocs/Material for MkDocs as the implemented site stack.  
**GitHub repo B:** `english-learning-progress`, **private according to the architecture contract (not revalidated here)**; results, review schedule, learner preferences and event history.

The public site is an **instructional resource**, not the official grading engine. Do not publish private grades, learning logs, email/address details or copyrighted textbook scans in the public repo.

## 2. Public course repository (implemented foundation and proposed lesson structure)

```text
english-learning-course/
  README.md
  mkdocs.yml
  requirements.txt
  requirements-dev.txt
  curriculum/
    master_syllabus.yaml
    lesson_metadata.schema.json
  governance/
    pedagogical_guidelines.md
    assessment_framework.md
    technical_architecture.md
    lesson_template.md
  scripts/
    validate_course.py
  docs/
    index.md
    elementary/
      index.md
      unit_01/            # proposed, not yet created
        lesson_a.md       # proposed, not yet created
        lesson_b.md       # proposed, not yet created
        lesson_c.md       # proposed, not yet created
        assets/           # proposed, not yet created
    pre_intermediate/
    intermediate/
    intermediate_plus/
    upper_intermediate/
    advanced/
    advanced_plus/
    reference/
  .github/
    workflows/
      pages.yml
      quality.yml

```

**Lesson IDs:** `elementary.unit_01.lesson_a` (stable identity); file slugs may change, IDs should not. Metadata must conform to `curriculum/lesson_metadata.schema.json` and include `source_lesson`, `source_verification`, `source_references`, per-topic `origin`, `prerequisites`, `objectives`, `skills`, `review_tags`, `content_version`, `oral_activities`, `writing_outcome`, `cefr`, and `editorial_status`. Distinguish observed book topics from program additions.

**Build:** approved Markdown → MkDocs static site → GitHub Actions deploy → GitHub Pages. Deploy only when checks and review pass. Mobile-friendly styling, navigation, cross-links, search, visual accessibility, and optional print styles. A downloadable PDF compendium is a **future optional artifact**, not authoritative source.

## 3. Private progress repository (architecture contract; not revalidated in this preparation PR)

```text
english-learning-progress/
  README.md
  schema/
    event.schema.json
  events/
    2026/
  snapshots/
    skills.json
    units.json
    error_patterns.json
    review_queue.json
  config/
    learner_preferences.yaml
  docs/
    tutor_operating_protocol.md
```

Events append; derived snapshots may be regenerated. Keep identifiable/sensitive information to the minimum. Avoid storing audio by default. Do not commit project API keys or credentials. For version safety read current SHA before updating an existing file. In contested edits or simultaneous sessions, refresh, reconcile and retry rather than overwriting latest changes. Use GitHub permissions appropriate to each project. Never claim a log or commit was saved until the write response confirms success.

## 4. Cross-project information contract

**Shared, public (read):** master syllabus, unit metadata, published lesson, current content revision.  
**Learning-only (private read/write):** learner state, errors, attempts, reviews.  
**Development-only (public write):** curated lesson revisions, site assets, metadata; may receive anonymized content-quality feedback if explicitly approved, but no private results by default.

The tutor should begin a session by fetching the latest relevant `unit_id`, prerequisites and learner snapshot (if tools are connected/available). If not available, say the state could not be verified and avoid fabricating progression. After assessments, prepare an event, write it, and verify the result; in case of failure provide a local/importable event file, not false confirmation.

ChatGPT Projects do **not** automatically synchronize memories or private repository states with one another. Repository reads and writes happen through available authorized GitHub connector actions and can require explicit user action/permissions. There is no always-on monitoring unless separately configured.

## 5. Tutor operating sequence

1. Confirm target unit or pick next eligible based on private snapshot + prerequisites.
2. Load current published unit and content revision.
3. Choose mode: Learn / Practice / Conversation / Assessment.
4. Work on lesson-specific competencies; include spaced review.
5. Give corrections in learner-friendly English; key bilingual anchors where needed.
6. During assessment, score only evidenced skills; do not expose answer key in advance.
7. Create append-only event and update/derive snapshots, verifying repo writes.
8. Show next objective and queued review.

Voice mode speed and lexical density adapt to comprehension; no assumption that speech recognition is a perfect pronunciation grader.

## 6. Editorial operating sequence

1. Read current approved curriculum and its identified primary project source index; verify the original asset and any declared gaps before drafting. Use external references only for missing or supplementary context.
2. Draft original content and task answer keys using pedagogical guidelines.
3. Prepare original purposeful images with alt text and instructional purpose.
4. Validate grammar, alternatives, reading level, register and source traceability.
5. Preview site locally; run links/build checks and mobile inspection.
6. Submit changes for approval (ideally a branch/PR).
7. Merge and deploy; verify site; update unit status and content revision.

## 7. Risks and controls

| Risk | Control |
|---|---|
| Public repo leaks progress | Completely separate private repo; no public imports of private JSON |
| Copyrighted publisher material exposed | Original content only; no uploaded scans or copied exercise banks in public repository |
| Multiple chats overwrite state | Append-only events, SHA checked updates, conflicts reconciled |
| PDF/site layout regression | Markdown source, build checks, mobile preview and optional print stylesheet |
| Tutor hallucinates progress | Read source of truth or state unavailable; never infer unseen results |
| Weak voice scoring evidence | Provisional scores and explicit confidence/evidence thresholds |
| Over-engineering | Start with one Elementary unit pilot; no backend/login/database initially |

## 8. MVP acceptance criteria

- [ ] Both repos have correct public/private visibility and scoped permissions.
- [ ] Source documents and stable schema committed after review.
- [ ] MkDocs site builds and publishes; mobile navigation and images work.
- [ ] One original Elementary lesson with grammar/vocabulary/writing + meaningful visuals available.
- [ ] Tutor can read lesson, conduct an elementary listening/speaking session and grade a scoped assessment.
- [ ] One test event saved to private repo and successfully read from a new conversation.
- [ ] User can identify exactly what content is public vs private.

## 9. Current implementation, controls and pending decisions

- **Verified 2026-11-10:** the public repository is `jccabreralosada/english-learning-course`, with default branch `main` and a working GitHub connection.
- **Branch ruleset:** `Protect main - English Learning Course` (ID `26878741`) reports enforcement `active`, target `refs/heads/main`, pull request required, allowed merge method squash, required check `course-quality`, resolved review threads, deletion and force-push blocked, and no bypass actors. It currently requires zero approving GitHub reviews; user editorial sign-off is a separate mandatory control.
- **Verified Pages foundation:** MkDocs Material and the `pages.yml` workflow have produced a successful strict build and GitHub Pages deployment. Public URL is `https://jccabreralosada.github.io/english-learning-course/`. Independent visual/mobile inspection remains pending.
- **Preparation PR:** PR #1 (`chore/course-foundations-v1`) is a draft with no merge. The files in this branch are not yet published via `main`.
- **Quality checks:** the proposed `.github/workflows/quality.yml` runs automated metadata, source-provenance, navigation, local-link, image-alt, test-suite, and strict MkDocs checks in PRs and permitted branches. The quality workflow **does not deploy**.
- **Release control:** human editorial approval of the exact head commit and successful required checks precede setting the PR ready for review, squash merging, and verification of the resulting `main` checks. Never commit or merge directly to `main` from editorial automation. Check Pages only on changes to the site publishing workflow's configured paths; curriculum-only changes need not republish.
- **Source integrity (verified 2026-11-10):** Elementary 1A–1C have been checked directly against the original supplied Fourth Edition index image; primary references are private project asset names, index locations, and SHA-256 hashes. The external index is no longer primary. Pre-intermediate now has 12 indexed units, 36 A/B/C source lessons and their Practical English / Revise and Check sequence, drawn from the original complete contents images. All source scans remain outside the public repository. A passing build does not constitute educational approval.
- **CEFR:** introductory objectives are provisionally oriented to A1; individual descriptor mappings and all-level calibration remain unverified.
- **Private progress repository:** statuses and permissions must be verified separately in the English Learning Program project. No private data is read or published by this PR.

### Source provenance and privacy contract

- Store original Oxford images/PDFs privately in the ChatGPT project, never under public repository paths.
- Store **only** bibliographic metadata, project attachment filenames, source locations and SHA-256 digests in the public curriculum. The digests identify reference copies; CI cannot inspect private image bytes and therefore checks metadata format rather than claiming live file verification.
- `source_index_confirmed` marks publisher-indexed topics; `program_extension` marks independent outcomes, prompts and activities. A CEFR band remains provisional until matched with an authoritative descriptor.
- The per-lesson metadata schema permits an `asset` + `asset_sha256` private reference or an external `url`, never requiring a publicly accessible commercial scan.

## 10. Remaining decisions

- Direct comparison of original user-supplied Elementary index images with the external contents index.
- Exact CEFR can-do descriptor mapping and piloted writing/speaking rubrics.
- Final lesson page review and mobile visual accessibility checks after an approved original lesson exists.
- Choosing official assessment bank/private blueprint storage in the separate learning repository.
- Event schema, review snapshot workflows and audio evidence policy in the separate learning project.

This file documents current infrastructure and proposed quality controls; it does not authorize merge or publication.
