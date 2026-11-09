# English Learning Program — Assessment, Mastery & Review Framework

**Version:** 1.0.0 (draft for review)  
**Purpose:** Evaluate competence across six skills, preserve longitudinal evidence, and avoid blocking progress for one imperfect attempt.

## 1. Skills and equity

Treat **Grammar, Vocabulary, Writing, Listening, Speaking, Pronunciation** as equally important *over the program*. For full assessments the default reporting may show six equally weighted sub-scores (approximately 16.67% each). Do not force every lesson to assess all skills or artificially calculate an overall grade from untested skills.

- **Grammar:** choose and produce structures accurately, including contrasts and transfer.
- **Vocabulary:** meaning, collocations, informal/formal register, phrasal verbs, modals in context, retrieval/appropriate use.
- **Writing:** meaning, task completion, grammar, lexical choice, coherence and register.
- **Listening:** gist, key detail, inference at the relevant level, comprehension under progressively natural delivery.
- **Speaking:** comprehension/interaction, communicative effectiveness, organization, fluency and accuracy, appropriate to task.
- **Pronunciation:** intelligibility, word stress, sentence stress, rhythm and repair of misunderstandings; do not penalize a non-native accent itself.

## 2. Scoring, states, and decision rules

**Mastery target:** `90/100` for each skill when assessed with sufficient evidence using a defined rubric. This is an internal study standard, **not** a CEFR certificate or standardized exam score.

| State | Interpretation | Learning action |
|---|---|---|
| `not_started` | No evidence yet | Introduce unit |
| `learning` | Currently being taught, insufficient evidence | Guided practice |
| `in_consolidation` | Partial competence, inconsistent/fragile recall | Continue compatible topics + reinforce |
| `mastered` | Repeated sufficiently strong, retained, transferable performance | Progress + spaced maintenance |
| `needs_reinforcement` | Important prerequisite gap or repeated critical errors | Focused remediation before dependent topic |

**Initial progression rule:** a single sub-90 attempt does not force repeating an entire level. For `mastered`, require (a) a strong current performance (target ≥90), (b) transfer to fresh contexts, and (c) at least one delayed review; where evidence is incomplete, keep `in_consolidation`. Move forward in independent content if prerequisites are satisfied. **Final level completion:** each of the six skills must have documented mastery; overall average alone does not suffice. Detailed item difficulty and minimum evidence counts are to be calibrated with the Elementary pilot, not invented in advance.

If a task tests only grammar and vocabulary, write `not_assessed` for the other skills, never a guessed zero or 90.

## 3. Session design by mode

- **Learn:** formative checks; no official final score unless explicitly transitioned to assessment.
- **Practice:** feedback after each response; record recurring misconception and successful correction.
- **Conversation:** collect communicative evidence and a few high-priority errors after a meaningful turn; ratings may be `provisional`.
- **Assessment:** fresh items, no hints while attempting, criterion-level scoring and evidence, answer key withheld until submission; separate skill tasks where needed.

For pronunciation and spontaneous speech, automatic transcription may be inaccurate: distinguish `observed`, `inferred`, and `insufficient_evidence`; avoid falsely precise claims. Formal speaking/pronunciation scoring needs actual audio exposure and honest limitations. Listening speed should gradually become more natural as comprehension improves, with comprehension support during *practice*, not hidden in graded assessments.

## 4. Proposed tracking model (private repository only)

Maintain append-only events plus derived snapshots. Do **not** store a person's entire speech recording or complete transcript unless explicitly desired and consented to. Suggested structure:

```text
learning-progress/
  schema/
    session.schema.json
  events/
    YYYY/
      YYYY-MM-DD_session-id.json
  snapshots/
    skills.json
    units.json
    error_patterns.json
    review_queue.json
  config/
    learner_preferences.yaml
```

Every assessment event should include:

| Field | Purpose |
|---|---|
| `event_id`, `occurred_at`, `unit_id` | Identity and traceable chronology |
| `mode`, `task_ids`, `content_revision` | Context and content version |
| `skill_results` | Scores only for assessed skills, rubric dimension results, confidence |
| `evidence_summary` | Short, non-sensitive justification and observed performance |
| `errors` | Error code, severity, example fragment if relevant, correction status |
| `mastery_decision` | Previous state, new state, reason, evidence sufficiency |
| `review_actions` | Topics to revisit and tentative due dates |

Example *illustrative* event:

```json
{
  "event_id": "example-001",
  "occurred_at": "YYYY-MM-DD",
  "unit_id": "elementary.unit_03.lesson_a",
  "mode": "assessment",
  "content_revision": "example-commit-sha",
  "skill_results": {
    "grammar": {"score": 94, "confidence": "high"},
    "vocabulary": {"score": 86, "confidence": "high"}
  },
  "not_assessed": ["writing", "listening", "speaking", "pronunciation"],
  "errors": [{"code": "third_person_singular", "status": "review_needed"}],
  "mastery_decision": {"state": "in_consolidation", "reason": "vocabulary needs further retrieval"},
  "review_actions": [{"topic_id": "third_person_singular", "due": "YYYY-MM-DD"}]
}
```

Snapshots are regenerable from events; never silently overwrite event history. Use private repo permissions and minimize personal data.

## 5. Error taxonomy

Use stable IDs rather than unconstrained prose alone, e.g. `third_person_singular`, `auxiliary_do_questions`, `past_simple_irregular`, `tense_choice`, `preposition_choice`, `phrasal_verb_particle`, `collocation`, `word_order`, `register_mismatch`, `listening_detail`, `speaking_fluency`, `pronunciation_word_stress`, `pronunciation_intelligibility`. Allow adding codes through a reviewed vocabulary.

Distinguish **systematic error**, **isolated slip**, and **valid regional/alternative usage**. Do not penalize a correct alternative merely because the expected answer key listed one example.

## 6. Spaced and cumulative review

Default **provisional** sequence: 1, 3, 7, 14, 30 days after initial learning, later based on retention. This is a starting heuristic, not a rigid neurological rule.

- Include older content during new-unit practice without announcing the exact rule each time.
- Reserve time for old phrasal verbs/modals and listening/speaking transfer.
- A failed delayed task can move a previously mastered topic back into consolidation; log the evidence and review rationale.
- The private queue stores due items; a chat does **not** continuously watch the calendar or repo. Review happens on session start or via an explicitly configured reminder workflow.

## 7. Elementary acceleration protocol

Use short diagnostics before each unit or cluster, starting from Elementary. If fundamentals are demonstrated, reduce repetitive reading and move to stronger transfer tasks; still offer basic voice/listening practice. Never assume Grammar proficiency establishes Listening proficiency. No compulsory re-study of an entire level for a narrow weakness unless it blocks needed prerequisites.

## 8. Review checklist before official scoring

- [ ] Assessment scope and rubric stated before attempt.
- [ ] Tasks are unseen or materially different from public ungraded questions.
- [ ] Scored skills actually assessed; other skills explicitly marked unassessed.
- [ ] CEFR-aligned task difficulty considered, without claiming certification.
- [ ] Accepted alternative answers reviewed.
- [ ] Audio-based criteria use actual evidence; limitations disclosed.
- [ ] Error patterns and delayed-review queue updated only after successful repo write.
- [ ] Snapshot and append-only history consistent.

## 9. Pending calibration

Choose a stable rubric scale for spoken/written dimensions, evidence requirements for `mastered`, and fair score normalization in the pilot. These are **not yet finalized** by this draft.