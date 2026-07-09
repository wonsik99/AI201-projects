# Mixtape Bug Hunt — submission.md

## AI Usage

1. **Codebase orientation:** I pasted `models.py`, route files, and service modules into Codex and asked for file summaries and call-chain traces (e.g., how rating flows from `routes/songs.py` to `notification_service.rate_song()`). This helped me build the codebase map faster, but I verified every relationship by reading the actual SQLAlchemy models and route handlers myself.

2. **Bug investigation:** After reproducing each bug with `pytest` or API calls, I asked Codex to explain suspicious functions (for example, what `songs[:-1]` does and why an `outerjoin` on `song_tags` could duplicate rows). The AI correctly flagged the playlist slice and search join as likely causes. I rejected its initial guess for Issue #1 (weekday vs. isoweekday confusion) once I read line 73 directly and saw the extra `today.weekday() != 6` guard was the actual problem.

3. **What I verified manually:** Every fix was confirmed with `pytest tests/` and, where relevant, by re-reading the full function after the change. I did not apply AI-suggested fixes without tracing the call chain myself.

---

## Codebase Map

### Main files

| File / folder | Role |
|---------------|------|
| `app.py` | Flask app factory, SQLAlchemy `db` setup, blueprint registration |
| `models.py` | SQLAlchemy models: `User`, `Song`, `Playlist`, `Rating`, `Notification`, `ListeningEvent`, `Tag`, plus join tables for friendships, song tags, and ordered playlist entries |
| `routes/` | HTTP layer — parses requests, calls services, returns JSON |
| `services/` | Business logic — where all five bugs live |
| `seed_data.py` | Populates SQLite with users, songs, playlists, listening events, and friendships for local testing |
| `tests/` | Pytest coverage for streaks, search, and playlists |

### Pattern

Routes stay thin. Example: `POST /songs/<id>/rate` in `routes/songs.py` validates JSON and delegates to `notification_service.rate_song()`. The service layer owns streak updates, feed filtering, search queries, notifications, and playlist ordering.

### Data flow — friend rates a shared song

1. Client sends `POST /songs/<song_id>/rate` with `{ user_id, score }`.
2. `routes/songs.py` calls `notification_service.rate_song()`.
3. `rate_song()` loads the `Song` and `User`, upserts a `Rating` row, commits.
4. If the rater is not the original sharer, `create_notification()` writes a `Notification` for `song.shared_by`.
5. Client fetches notifications with `GET /users/<user_id>/notifications`.

Playlist adds follow a similar pattern: `notification_service.add_to_playlist()` saves the playlist entry, then notifies the song sharer — this was the working pattern Issue #4 was missing for ratings.

---

## Root Cause Analysis

### Issue #1 — My listening streak keeps resetting

**How I reproduced it:** Ran `pytest tests/test_streaks.py::test_streak_increments_on_sunday`. The test simulates listening on Saturday then Sunday and expects streak `2`; before the fix it returned `1`.

**How I found the root cause:** Read `services/streak_service.py` → `update_listening_streak()`. Traced the branch for `days_since_last == 1`.

**Root cause:** Line 73 required `today.weekday() != 6` before incrementing a consecutive-day streak. On Sunday (`weekday() == 6`), listening one day after Saturday matched `days_since_last == 1` but failed the Sunday guard and fell through to the reset branch.

**Fix and side-effect check:** Removed the Sunday guard so consecutive calendar days always increment. Re-ran full streak tests; Monday→Tuesday and skip-day reset tests still pass.

**Commit:** `fix: allow streak increment when listening on consecutive Sundays`

---

### Issue #2 — Friends Listening Now shows people from yesterday

**How I reproduced it:** Read `seed_data.py` listening timestamps and `feed_service.RECENT_THRESHOLD`. Seed events older than ~30 minutes should not appear in "listening now", but a 24-hour window includes yesterday evening.

**How I found the root cause:** `routes/feed.py` → `feed_service.get_friends_listening_now()` → `RECENT_THRESHOLD = timedelta(hours=24)`.

**Root cause:** "Listening now" used a rolling 24-hour cutoff, so any friend listen from the previous evening still qualified the next morning.

**Fix and side-effect check:** Changed threshold to `timedelta(minutes=30)`. General activity feed (`get_activity_feed`) is unchanged and still returns historical events.

**Commit:** `fix: limit friends listening now feed to last 30 minutes`

---

### Issue #3 — The same song keeps showing up twice in search

**How I reproduced it:** Ran `pytest tests/test_search.py::test_search_no_duplicates_multi_tag_song` — a song with multiple tags returned 3 rows instead of 1.

**How I found the root cause:** `routes/songs.py` → `search_service.search_songs()` → unnecessary `.outerjoin(song_tags)` even though the filter only uses title/artist.

**Root cause:** Joining `song_tags` emitted one SQL row per tag. A song with three tags appeared three times in results.

**Fix and side-effect check:** Removed the unused join; tags still load through the `Song.tags` relationship in `to_dict()`. Search tests pass.

**Commit:** `fix: remove song_tags join that duplicated search results`

---

### Issue #4 — Rating notifications missing

**How I reproduced it:** Compared `add_to_playlist()` (which calls `create_notification()`) with `rate_song()` (which did not). Rating saves correctly via `POST /songs/<id>/rate`, but no notification row was created for the sharer.

**How I found the root cause:** Read `notification_service.py` end-to-end. Playlist adds notify the sharer; `rate_song()` stopped after `db.session.commit()`.

**Root cause:** Architectural omission — rating flow never called `create_notification()`, unlike the working playlist-add flow.

**Fix and side-effect check:** After commit, if the rating is new and the rater is not the sharer, create a `song_rated` notification using the same helper as playlist adds. Self-ratings still do not notify.

**Commit:** `fix: notify song sharer when another user rates their song`

---

### Issue #5 — The last song in a playlist never shows up

**How I reproduced it:** Ran `pytest tests/test_playlists.py::test_playlist_returns_all_songs` — a 5-song playlist returned 4 entries.

**How I found the root cause:** `routes/playlists.py` → `playlist_service.get_playlist_songs()` → return line used `songs[:-1]`.

**Root cause:** Python slice `[:-1]` drops the final list element, so the most recently added song was always excluded.

**Fix and side-effect check:** Return the full `songs` list. Playlist order tests still pass.

**Commit:** `fix: return all playlist songs including the most recent entry`

---

## Test Results

After all fixes:

```bash
pytest tests/
# 13 passed
```

## git log

Run on branch `bugfix/mixtape`:

```bash
git log --oneline
```

Include a screenshot of this output when submitting to the Course Portal.
