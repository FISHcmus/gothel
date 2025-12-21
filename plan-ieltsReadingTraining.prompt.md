## Plan: ieltsReadingTraining backend (FastAPI + SQLAlchemy)

Build an IELTS Reading training backend on top of your existing FastAPI app (`main.py`), SQLAlchemy setup (`model/User.py`), and JWT auth (`auth/auth.py`). Start with an MVP that supports passages, questions, attempts, and scoring/points. Then expand into richer analytics (band estimation, weak areas), admin tooling (content lifecycle, bulk import), and safe schema evolution (Alembic migrations, data backfills). Prioritize security (role-based admin, ownership checks) and edge-case hardening (retakes, partial submissions, time limits, cheating signals).

### Steps
1. Define core entities + relationships in `model/` alongside `UserDB` (new `ieltsReadingTraining` tables).
2. Add MVP APIs in `main.py` (or `routers/`) for catalog, session, submit, results, and progress.
3. Implement scoring + points rules (attempt-level, question-level, streaks, anti-farm limits).
4. Add admin/content management endpoints (CRUD, publish states, import/export, moderation).
5. Add analytics/progress tracking endpoints + derived aggregates (per skill, time, accuracy).
6. Adopt schema evolution strategy (Alembic, versioned content, migrations/backfills, soft deletes).

### Further Considerations
1. Difficulty model: manual (admin-set) vs computed from answer stats—start manual, compute later.
2. Band estimation: simple raw→band mapping first; later calibrate by question difficulty.
3. Storage: keep SQLite for MVP; plan Postgres migration when concurrency/analytics grow.

---

## 1) Core entities / data model (SQLAlchemy)

Keep `UserDB` as-is, and add a minimal “content → session → attempt → analytics” model. Use camelCase naming in API JSON, but snake_case columns in DB.

### 1.1 Users & roles
- **UserDB** (existing): add fields later if needed
  - `role` (`"user" | "admin"`) for admin access (or separate `user_roles` table).
  - Optional: `display_name`, `target_band`, `timezone`, `is_active`.

### 1.2 Content: passages, questions, answer keys
**ReadingPassage**
- `id` (PK)
- `title`
- `text` (full passage)
- `topic` (e.g., environment, technology)
- `difficulty` (1–5 or “easy/med/hard”)
- `source` (book/test identifier)
- `estimated_time_sec` (baseline)
- `status` (`draft | review | published | archived`)
- `version` (int; for safe edits while keeping attempt history stable)
- `created_by_user_id`, timestamps

**ReadingQuestion**
- `id` (PK)
- `passage_id` (FK ReadingPassage)
- `question_no` (ordered)
- `type` (enum: `multipleChoice`, `trueFalseNotGiven`, `matchingHeadings`, `sentenceCompletion`, etc.)
- `prompt` (question text)
- `instructions` (optional)
- `points` (default 1; supports weighted scoring later)
- `status` / `version` mirroring passage if needed

**ReadingQuestionOption** (for MCQ-like)
- `id`, `question_id`, `label` (“A/B/C/D”), `text`

**ReadingAnswerKey**
- `id`, `question_id`
- `correct_value` (string; for TFNG, exact answer; for MCQ label; for matching store normalized tokens)
- `alt_values` (JSON array) for acceptable variants
- `normalization_rules` (JSON: casefold, strip punctuation, numeric tolerance)
- `explanation` (admin-authored)
- `reference_span` (optional: text offsets or quote)

**Tag** + association tables
- Tag passages/questions with skills: `skimming`, `detail`, `inference`, `vocab`, topic tags, etc.
- Enables analytics by tag later.

### 1.3 Training/run-time: sessions and attempts
**ReadingSession**
- Represents a “practice run” a user starts for a passage (or a test bundle later).
- `id`, `user_id`, `passage_id`, `passage_version_snapshot`
- `mode` (`practice | timed | examLike`)
- `started_at`, `ended_at`
- `time_limit_sec` (nullable for practice)
- `status` (`inProgress | submitted | abandoned`)
- Anti-cheat metadata: `client_reported_duration_sec` (optional), `ip_hash` (optional), `user_agent` (optional)

**ReadingAttempt**
- One per submission (supports retakes).
- `id`, `session_id`, `attempt_no` (1..N)
- `submitted_at`
- `raw_score` (sum points)
- `max_score`
- `accuracy` (raw_score/max_score)
- `estimated_band` (optional, computed)
- `points_awarded` (gamification points)
- `grading_version` (so scoring algorithm changes don’t break old results)

**ReadingAttemptAnswer**
- `id`, `attempt_id`, `question_id`, `question_version_snapshot`
- `answer_text` (user input; store as text even for MCQ label)
- `is_correct` (bool)
- `points_earned`
- `feedback` (optional; e.g., which tokens mismatched)
- `graded_at`

### 1.4 Analytics/progress aggregates (denormalized, optional)
Start with query-based analytics (compute on the fly). Add aggregates when needed.

**UserReadingStatsDaily**
- `id`, `user_id`, `date`
- `sessions_started`, `sessions_completed`
- `questions_attempted`, `questions_correct`
- `time_spent_sec`
- `points_earned`

**UserQuestionStats**
- `user_id`, `question_id`
- attempts count, correct count, last_attempt_at
- used for weak-areas + spaced repetition later

---

## 2) API endpoints (MVP + next)

Your current auth flows:
- `POST /register`
- `POST /token`
- `GET /users/me`

Add “/api” prefix and version later; for MVP you can keep simple paths.

### 2.1 MVP endpoints

#### Catalog & content viewing (user-facing)
- `GET /reading/passages`
  - filters: `status=published`, `difficulty`, `topic`, `tag`, pagination
- `GET /reading/passages/{passageId}`
  - returns passage + question list (without answer keys/explanations)
- `GET /reading/passages/{passageId}/questions`
  - optional separate endpoint if you want paged questions

#### Session lifecycle
- `POST /reading/sessions`
  - body: `passageId`, `mode`, optional `timeLimitSec`
  - returns `sessionId`, startedAt
- `GET /reading/sessions/{sessionId}`
  - ownership enforced; returns passage snapshot info + status
- `POST /reading/sessions/{sessionId}/submit`
  - body: list of `{questionId, answerText}` plus optional `clientDurationSec`
  - returns attempt summary: rawScore/maxScore, band estimate, points awarded, per-question correctness (no correct answers revealed unless practice mode rules allow)

#### History & progress
- `GET /reading/attempts`
  - filters: by passageId, date range; pagination
- `GET /reading/attempts/{attemptId}`
  - returns full breakdown; optionally includes explanations in practice mode

### 2.2 Next-phase endpoints

#### Admin content management (role=admin)
- `POST /admin/reading/passages`
- `PATCH /admin/reading/passages/{passageId}`
- `POST /admin/reading/passages/{passageId}/publish`
- `POST /admin/reading/questions`
- `PATCH /admin/reading/questions/{questionId}`
- `POST /admin/reading/answerKeys`
- `POST /admin/reading/import`
  - upload JSON/CSV; returns import report
- `GET /admin/reading/quality`
  - flags: too-easy/hard, ambiguous questions, many alt answers, low discrimination

#### Advanced training modes
- `POST /reading/tests`
  - bundles multiple passages (full IELTS-like)
- `POST /reading/tests/{testId}/sessions`
- `POST /reading/sessions/{sessionId}/saveProgress`
  - partial answers autosave; supports pause/resume

#### Analytics
- `GET /reading/progress/summary`
  - totals, accuracy trend, time trend, points trend
- `GET /reading/progress/byTag`
  - accuracy/time for each tag/skill
- `GET /reading/progress/weakAreas`
  - lowest-performing tags/question types
- `GET /reading/progress/bandEstimate`
  - rolling estimate (e.g., last 5 timed sessions)

---

## 3) Scoring & points rules (practical MVP)

Separate **score** (IELTS-like correctness) from **points** (gamification). That way you can adjust points without invalidating IELTS score logic.

### 3.1 Correctness grading (MVP)
Per question type:
- **MCQ**: correct if selected label matches `correct_value`.
- **TFNG**: normalize to `true/false/not given` canonical tokens; accept common variants (`t`, `f`, `ng`).
- **Short answer / completion**:
  - Normalize: trim, collapse whitespace, unicode normalize, casefold (English), remove trailing punctuation.
  - Accept if matches `correct_value` or any `alt_values`.
  - Optional later: numeric tolerance (`10` vs `ten`) with explicit rule per question.
- **Matching**:
  - Store correct mapping as structured JSON in `correct_value` (later); for MVP keep as single token if simple.

Return per-answer feedback in a safe way:
- MVP: `isCorrect`, `pointsEarned`.
- Practice mode can optionally include `correctAnswer` after submission; timed/examLike should not.

### 3.2 Raw score → IELTS band (MVP heuristic)
- IELTS Reading band mapping differs for Academic vs General. For MVP:
  - Implement a simple lookup table configurable per “track”.
  - Default to Academic mapping with `rawScore` out of `maxScore` (usually 40).
- Store `estimated_band` on `ReadingAttempt`, plus the mapping version used.

### 3.3 Points (gamification) rules
Goal: encourage consistency without letting users farm points by repeating trivial items.

Suggested MVP:
- Base points per attempt: `+10` for submit (completed session).
- Per correct answer: `+2 * question.points` (default points=1).
- Time bonus (timed mode only): if finished <= time_limit, `+0…+10` scaled.
- Streak: `+5` for day-streak milestones (2, 3, 5, 7 days).
- Anti-farming:
  - Retake diminishing returns: attempt_no=1 full points, 2nd 50%, 3rd+ 0% points (still record score).
  - Or cap daily points (e.g., 300/day) stored in daily stats table.

Store:
- `ReadingAttempt.points_awarded` (final number)
- Optional `UserPointsLedger` later for auditability.

---

## 4) Admin / content management (workflows)

### 4.1 Content lifecycle
- `draft`: editable, not visible to users.
- `review`: locked for editing except admins; optional reviewer tooling.
- `published`: visible in catalog; changes require version bump.
- `archived`: hidden but kept for attempt history.

### 4.2 Versioning strategy (important)
When a passage/question changes after publication:
- Create new version (new `ReadingPassage` row or increment `version` with immutable snapshots).
- Sessions store `passage_version_snapshot` and `question_version_snapshot` so old attempts remain interpretable.

For MVP simplicity:
- Keep a single row with `version` and enforce “published content is immutable” (only allow new version via clone endpoint).

### 4.3 Admin safety & permissions
- Require JWT + `role=admin` for `/admin/*`.
- Add ownership checks for user endpoints: session/attempt must belong to current user.
- Rate-limit admin import endpoints to prevent accidental overload.

---

## 5) Analytics & progress tracking

Start with query-based analytics; add materialized stats if it gets slow.

### 5.1 Metrics to track
Per user:
- Accuracy trend (daily/weekly)
- Time spent trend
- Question-type accuracy
- Tag/skill accuracy
- Band estimate trend (rolling window)
- Completion rate (started vs submitted)

### 5.2 Useful derived signals (next)
- “Weak areas”: lowest accuracy tags with enough samples (e.g., ≥20 questions)
- “Speed”: seconds per question and per passage
- “Consistency”: practice days per week
- “Cheat signals”: extremely low client duration with high accuracy; repeated identical answers across attempts

---

## 6) Schema evolution strategy (SQLite now, scalable later)

Your repo currently creates/drops tables via `Base.metadata.create_all()` and `script/reset.py`. For a real product, move to migrations.

### 6.1 Adopt Alembic migrations
- Add Alembic config, generate initial migration from current `UserDB`.
- New tables (ieltsReadingTraining) added with subsequent migrations.
- Stop using `drop_all()` except for local/dev.

### 6.2 Backfills and safe migrations
- When adding non-null columns: add nullable → backfill → enforce non-null.
- For versioning changes: copy forward “published” rows into new versioned tables if needed.

### 6.3 Environment configuration
- Move DB URL and JWT secret out of code:
  - Read from environment variables with safe defaults for dev.
- Prepare for future Postgres:
  - Avoid SQLite-specific assumptions (like limited JSON querying).

---

## 7) Edge cases & security checklist

### 7.1 Auth, access control, and data protection
- Enforce ownership on:
  - `GET /reading/sessions/{id}`
  - `POST /reading/sessions/{id}/submit`
  - `GET /reading/attempts/{id}`
- Don’t leak answer keys/explanations to non-admins (or only after submission in practice).
- Hash secrets: replace hard-coded `SECRET_KEY` with env var; rotate keys via `kid` (next).

### 7.2 Input validation edge cases
- Empty submissions (no answers) → allow submit but score 0; still mark ended.
- Duplicate question answers in payload → reject or last-write-wins (choose one and document).
- Question not in passage/session snapshot → reject (prevents submitting other passage answers).
- Long answer_text payloads → cap length (e.g., 1–500 chars) to prevent abuse.

### 7.3 Concurrency / replay protection
- Prevent double-submit:
  - If session already `submitted`, reject or create a new attempt only via an explicit “retake” flow.
- Token expiry handling already exists; ensure refresh strategy later if needed.

### 7.4 Content integrity and moderation
- Admin import should validate:
  - question numbering contiguous
  - every question has an answer key
  - published passages have at least N questions
- Soft-delete vs hard-delete:
  - Prefer archive/disable; never delete content referenced by attempts.

### 7.5 Observability basics (next)
- Add request IDs, structured logs.
- Track grading errors separately; never fail a submit without returning a stable error shape.

---

## Draft review questions (to refine this plan)
1. Do you want **Academic**, **General Training**, or both (affects band mapping)?
2. Should users see **correct answers/explanations immediately** (practice) or only after a delay?
3. Do you want “full test” mode in MVP, or strictly single-passage practice first?

