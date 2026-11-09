# English Learning Program — Technical Architecture

**Version:** 1.0.0 (design draft; no repositories or ChatGPT Projects created yet)

## 1. System boundary

Two **ChatGPT Projects** share the learning curriculum but perform distinct jobs:

| Project | Primary responsibility | Writes to |
|---|---|---|
| `English Course Development` | Editorial workflow, curriculum maintenance, original lessons, images and non-graded self-study exercises | Public course repository, after user-approved review |
| `English Learning Program` | Tutor modes Learn/Practice/Conversation/Assessment; six-skill evidence and spaced reviews | Private progress repository, with permission and successful commit verification |

**GitHub repo A:** `english-learning-course`, **public**; static learning site deployed with GitHub Pages, using MkDocs/Material for MkDocs as proposed technology.  
**GitHub repo B:** `english-learning-progress`, **private**; results, review schedule, learner preferences and event history.

The public site is an **instructional resource**, not the official grading engine. Do not publish private grades, learning logs, email/address details or copyrighted textbook scans in the public repo.

## 2. Public course repository (proposed)

```text
english-learning-course/
  README.md
  mkdocs.yml
  docs/
    index.md
    elementary/
      index.md
      unit_01/
        index.md
        grammar.md
        vocabulary.md
        everyday_english.md
        practice.md
        writing.md
        assets/
    pre_intermediate/
    intermediate/
    intermediate_plus/
    upper_intermediate/
    advanced/
    advanced_plus/
    reference/
      verb_tenses.md
      irregular_verbs.md
      modal_verbs.md
      phrasal_verbs.md
      collocations.md
  curriculum/
    master_syllabus.yaml
  governance/
    pedagogical_guidelines.md
    assessment_framework.md
    technical_architecture.md
  content_meta/
    units/
  .github/workflows/
    pages.yml
```

**Lesson IDs:** `elementary.unit_01.lesson_a` (stable identity); file slugs may change, IDs should not. Metadata should define `source_lesson`, `origin`, `prerequisites`, `objectives`, `skills`, `review_tags`, `content_version`, `status`. Distinguish observed book topics from program additions.

**Build:** approved Markdown → MkDocs static site → GitHub Actions deploy → GitHub Pages. Deploy only when checks and review pass. Mobile-friendly styling, navigation, cross-links, search, visual accessibility, and optional print styles. A downloadable PDF compendium is a **future optional artifact**, not authoritative source.

## 3. Private progress repository (proposed)

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

1. Read source index, declared gaps and curriculum; identify next lesson.
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

## 9. Implementation decisions still open

- GitHub repo owner/org and final names.
- MkDocs version/theme/build and Pages workflow configuration after current docs validation.
- Whether official assessment question banks live in the private repo or are generated fresh from private test blueprints; avoid exposing answers in public repo.
- Event JSON Schema details, snapshots regeneration, conflict handling and fallback exports.
- English voice accent defaults and detailed oral assessment rubrics.

No work has been performed in GitHub by this document; it is a design proposal only.