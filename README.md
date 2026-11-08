# Smarty

Smarty is a local desktop workbench for reviewing Tower Hill business ideas
and weekly bot-performance records. It runs entirely on one laptop at a
time, with no hosting, no accounts, no AI API calls, and no credits spent
just by opening it. Rudy and Lumi can each run it on their own PC and sync
their notes/statuses through the shared NAS when it's reachable.

**Kept is not approval.** Choosing a status in this app never sends a
message, launches a campaign, or spends money. It only files the record
into a personal view.

## How to run it

### Option A — the installed app (already set up on this machine)

A desktop shortcut named **Smarty** was created and points at:

```
C:\Users\<you>\AppData\Local\Programs\Smarty\Smarty.exe
```

Double-click it. No admin rights, no Python required for this path.

### Option B — run from source (for development)

```powershell
cd C:\TowerHill\Smarty
.\.venv\Scripts\Activate.ps1
python smarty_launcher.py
```

### Option C — rebuild the frozen exe

```powershell
cd C:\TowerHill\Smarty
.\.venv\Scripts\Activate.ps1
.\packaging\build_windows.ps1        # produces dist\Smarty\Smarty.exe
.\packaging\create_shortcut.ps1      # copies it to %LocalAppData%\Programs\Smarty + desktop shortcut
```

## Data paths (legacy "Sparky" names, kept on purpose)

| What | Where | Notes |
| --- | --- | --- |
| Local data (this laptop) | `C:\TowerHill\Grok-Bot-data\business-ideas\` | catalog cache + your journal |
| Shared root | `T:\TowerHill\Sparky\` | **legacy name** — this is Smarty's shared storage, not the old camera-companion "Sparky" app |
| Shared notes/status log | `T:\TowerHill\Sparky\Data\journal.jsonl` | only read/written if `T:\TowerHill\Sparky\Data` already exists |
| Shared installers | `T:\TowerHill\Sparky\Installers\` | `latest.json` + versioned zips, for the self-updater |

All of these are overridable via `sparky-paths.json` (in the local data
folder) or the environment variables `SPARKY_LOCAL_ROOT`, `SPARKY_NAS_ROOT`,
`SPARKY_CONFIG`, `SPARKY_DEVICE_ID`, `SPARKY_DEVICE_LABEL` — names kept from
an earlier Linux build of this same product so config files stay
compatible if one ever shows up.

**The `T:\` mapping has not been verified from this build machine.** The
app never hardcodes a UNC path, never creates `T:\TowerHill\Sparky\Data` if
it's missing, and never auto-publishes a build there. Confirm the mapping
yourselves on your real laptops before relying on sync.

## What's loaded right now

**The real catalog is loaded: 59 ideas + 10 weekly-performance records +
10 categories = 69 records, all unreviewed, all notes blank.** It took
three attempts to get here, worth recording honestly:

1. A message pointed at `/workspace/SMARTY_FOR_CLAUDE.md` and
   `/opt/cursor/artifacts/Smarty_Claude_Continue_Prompt.md` — paths that
   belong to a separate Cursor sandbox, not this Windows machine. Checked
   directly; neither exists here.
2. A follow-up pasted the real `categories.json` content inline, but its
   own text said the 59 ideas and 10 performance records were **not**
   included — only in the unreachable Cursor file. (Saved for reference as
   `seed\categories.reference.json`.)
3. A third message said the file now exists locally at
   `C:\TowerHill\Smarty\SMARTY_FOR_CLAUDE.md` (157,055 bytes). Checked —
   it was really there this time, containing all three JSON sections in
   full. Extracted and validated them programmatically (not by hand-typing
   data): exactly 59 unique idea ids, 10 unique performance ids, 10
   categories, 69 unique ids total, and the 5 ideas with no source URL
   matched exactly the ones named earlier (Pillar OS, Rogers–Feller,
   ClassDojo/Edutopia, and the family-name-preflight record). Saved
   verbatim to
   `C:\TowerHill\Grok-Bot-data\business-ideas\catalog\seed\{categories,ideas,weekly-performance}.json`.

The real schema differs from what this app originally guessed (built
before any real file existed): categories are referenced on records by
exact **label text** ("Growth and enrolment"), not a slug; ideas use
`received_date`, performance records use `period`; evidence fields are
nested under an `evidence` object. The code (`models.py`, `seed.py`,
`importer.py`, `version.py`, the UI) was updated to match the real shape
rather than forcing the real data into the earlier guess.

To refresh the catalog later: use the in-app **Import batch...** button
with a new batch file (see "Imports" below) — it never touches your
notes/status. The local `catalog\seed\` folder is only consulted on a
genuinely fresh install with no cache file yet.

## Keyboard / UI basics

- **Left column:** category tiles — Weekly bots performance, Growth and
  enrolment, New audiences and channels, Parent engagement and retention,
  Teaching–Professor ideas, Learning Dragon ideas, Miscellaneous — plus
  three status views: Rudy's collection (kept), Park it for later (parked),
  Rejected (recoverable).
- **Center:** the selected record — summary + bot-suggested implementation
  advice on top, status buttons + your notes + editable practical steps on
  the bottom.
- **Right:** the chronological list for whichever tile is selected (newest
  received-period first by default; toggle to oldest-first; ties break by
  title then id — the original order within a period is unknown, and the
  app says so rather than pretending otherwise).
- Search box + bot filter + status filter sit above the three columns.
- **Rejecting needs two clicks** (click once arms a "Confirm reject?"
  state for a few seconds, click again to actually reject) — a cheap guard
  against an accidental permanent-looking action, even though rejection is
  always recoverable from the Rejected view.
- Notes and practical-steps edits autosave a second after you stop typing,
  and on switching records or closing the app.
- "Sync now" button runs a bounded-timeout sync against the shared NAS
  journal; the label shows the last successful sync time, or "never".
- "This computer: (unlabeled — click to set)" button lets you type a label
  for this PC (e.g. "Rudy-Laptop") so your edits are identifiable during
  sync. It starts blank on every machine — nothing is guessed or defaulted
  to the Windows hostname — and is remembered after you set it once.
- "Import batch..." opens a file picker for a hand-prepared JSON batch
  (see "Imports" below) and applies it on top of the current catalog,
  then shows how many records were added/updated/skipped/kept-as-alternate.

## Privacy

No student profiles, parent contacts, credentials, or secrets are stored
by this app. All data is local JSON files plus whatever you put on the
shared NAS yourselves. No analytics, no cloud calls, no AI API calls.

## Notes, status, and multi-PC sync — how it actually works

- **Catalog** (titles, summaries, categories, sources, implementation
  advice) and **user state** (status/notes/practical-steps) are stored
  completely separately on disk. Re-importing or upgrading the catalog can
  never wipe your notes or status, because the importer never touches the
  journal file at all.
- Every status/notes/practical-steps edit is one **append-only operation**
  in `state\journal.jsonl` (device id, field, the base you edited from, the
  new value, a timestamp). Nothing is ever edited or deleted in place —
  resolving a conflict writes a new operation on top, it doesn't erase the
  old ones.
- Status and notes are independent fields: one PC can change notes while
  another changes status with no false conflict.
- If two PCs genuinely edit the **same field from the same base** with
  different values, both values are kept and shown as a conflict until a
  person resolves it by making a fresh edit. A stale PC that never wrote a
  competing edit cannot resurrect or override a real change — it just has
  nothing to contribute.
- Syncing takes a short-lived, auto-expiring lock on the shared journal
  (default 30s lease, so a crash can't block the share forever), unions
  operations by id, writes a temp file, fsyncs, and atomically renames it
  into place, then re-reads what's actually there before trusting it.
- A damaged line in the shared journal is **never silently dropped** —
  it's carried forward verbatim in the republished file rather than quietly
  discarded, in case it's a half-written op from a crash elsewhere.
- Up to 5 automatic backups of the shared journal are kept
  (`Data\backups\journal-<timestamp>.jsonl.bak`); nothing else in the
  backups folder is ever touched, so manual backups are safe.
- If the share is missing, unreachable, or `Data` doesn't exist yet, the
  app just says so and keeps working locally — it never hangs the window
  and never creates `Data` on its own.

## Web app (iPad / phone access)

`src/smarty/web/` is a second, independent front end for the exact same
logic (`store.py`, `journal.py`, `importer.py`, `view_model.py` — all
Qt-free by design, which is what made this possible without duplicating
any business logic). It's a small FastAPI app:

- **Password-gated** (`SMARTY_WEB_PASSWORD`) — one shared password, not an
  account system, required before any page loads.
- **Mobile-friendly UI**: same tiles → list → detail structure as the
  desktop app, same two-click reject, same autosaving notes/practical
  steps, same "kept is not approval" banner.
- **Its own journal**, stored at `SPARKY_LOCAL_ROOT` (`/data/smarty` in
  the Docker image) — edits made from an iPad are real edits, applied
  directly to this instance's store.
- **HTTP sync API** (`GET/POST /api/sync/{pull,push}`, bearer-token
  authenticated via `SMARTY_SYNC_TOKEN`, separate from the browser
  password) — the exact same union-by-op-id, keep-both-on-conflict merge
  the T:\\ share sync uses, just reached over HTTPS. The desktop app's new
  **"Sync to cloud"** button (`smarty/cloud_sync.py`) calls this, so edits
  flow both ways between the laptop and the hosted copy.

Run it locally:

```powershell
cd C:\TowerHill\Smarty
.\.venv\Scripts\Activate.ps1
$env:SPARKY_LOCAL_ROOT = "C:\TowerHill\Smarty\.devdata\local"
$env:SMARTY_WEB_PASSWORD = "choose-a-password"
$env:SMARTY_SYNC_TOKEN = "choose-a-token"
python -m uvicorn smarty.web.app:app --host 127.0.0.1 --port 8711
```

To point the desktop app at a deployed instance, set before launching:
`SPARKY_CLOUD_SYNC_URL=https://<your-render-url>` and
`SPARKY_CLOUD_SYNC_TOKEN=<same token as SMARTY_SYNC_TOKEN>` (or save them
into `sparky-paths.json` as `cloud_sync_url`/`cloud_sync_token`).

**Deploying to Render:** `Dockerfile`, `render.yaml`, and
`requirements-web.txt` (deliberately excludes PySide6 — the web process
never imports `smarty.ui.main_window`/`app`) are ready at the project
root. `render.yaml`'s persistent disk needs a paid ("Starter" or above)
Render plan — Render's free web-service tier has no persistent disk, so
`/data` would be wiped on every redeploy/restart (the app would just
re-seed from the bundled catalog and lose any notes/status entered since
the last deploy). Needed on Render's dashboard once connected to a repo:
set `SMARTY_WEB_PASSWORD`, `SMARTY_SYNC_TOKEN`, and `SMARTY_INGEST_TOKEN`
as secret env vars (`SMARTY_SESSION_SECRET` auto-generates via the
blueprint).

### Automated ingestion (e.g. Grok-bot)

`POST /api/ingest` lets an automated source add new ideas without a human
in the loop, authenticated with its own `SMARTY_INGEST_TOKEN` — a secret
deliberately separate from `SMARTY_WEB_PASSWORD` (your own browser login)
and `SMARTY_SYNC_TOKEN` (the laptop's sync), so revoking a misbehaving bot
never logs you out of either. `GET /api/ingest/schema` (no auth needed —
it returns only the contract, not data) describes the exact JSON shape,
the valid category labels, and the id-naming convention.

Reuses `apply_import_batch` unchanged, so an automated submission gets the
same guarantees a hand-import gets: duplicate ids, unknown categories, and
invented scores are all rejected; a rejected submission applies nothing at
all. It additionally **cannot create a new category** (the `categories`
field is accepted by the batch format generally, but the ingest endpoint's
request model doesn't expose it at all, and categories are independently
checked against the fixed 7 content tiles — a status-view label like
"Rudy's collection" is rejected too, even though it's technically in the
same `categories.json` list). Resubmitting the same `id` later (e.g. a
revised wording) merges by the usual revision rules rather than creating a
duplicate, and **never touches notes or kept/parked/rejected status** on
that id — the catalog cache and the journal are separate stores, so this
is a structural guarantee, not something the endpoint has to special-case
(covered by `tests/test_ingest.py::test_ingest_preserves_existing_notes_and_status_on_resubmission`).

**Content richness:** the real seed data has `summary` literally equal to
`"{title}: {advice text}"` for all 59 original ideas (checked against the
raw source file, not assumed) — the record page used to show the title,
then that same sentence, then the advice text a second time. The page now
detects that exact redundancy and shows the advice once; if a future
submission's `summary` genuinely differs from its `implementation_advice`,
both show. `GET /api/ingest/schema`'s `content_guidance` section tells an
automated submitter to make `summary` and `implementation_advice.text`
actually different, and to make the advice longer and specific rather than
a one-liner — Smarty can't invent that richness itself without breaking
the no-fabrication rule that governs this whole app, so it can only ask.
To enrich an idea already in the catalog, resubmit the same `id` at a
higher `content_revision`; that updates the editorial fields in place and
never touches notes or status.

**Reverse channel — `GET /api/feedback`:** lets Grok-bot read back what
Rudy decided: status (kept/parked/rejected/unreviewed) and notes per idea,
read-only, reduced the same way the UI shows it (never a raw op log).
Shares `SMARTY_INGEST_TOKEN` with `/api/ingest` on purpose — both
directions belong to the same counterpart, so one token covers submitting
ideas and reading feedback on them, and revoking it cuts off both at once.
By default returns only records that have actually been reviewed (status
set, or notes non-blank); `?include_all=true` returns everything, and
`?status=kept` (etc.) filters to one status. Documented in the same
`GET /api/ingest/schema` response, under `reverse_channel`. Covered by
`tests/test_feedback.py`, including a full round trip: ingest an idea,
review it through the web UI, read it back via `/api/feedback`.

## Imports after the seed

`smarty.importer.apply_import_batch(cache, batch)` accepts a dict with
`ideas` / `performance_records` / `categories` lists, plus an optional
envelope (`content_revision`, `prepared_on`, `batch_id`). Rules enforced in
code and covered by tests:

- Duplicate ids inside one file reject the whole file (nothing partially
  applied).
- Unknown category labels reject the batch rather than silently dumping
  the record into Miscellaneous.
- A higher revision updates editorial fields (never notes/status, which
  aren't in this file at all).
- A stale revision is skipped; a same-revision conflicting version is kept
  as a visible **alternate** rather than overwriting what's there.
- Re-importing identical bytes, or replaying a `batch_id` already applied,
  is a no-op.
- Performance records must not carry an invented score/grade — rejected if
  they do.

## Self-updater

`smarty.updater` implements: reject any zip not named exactly
`Smarty_vX.Y.Z.zip`; verify SHA-256 against the manifest before touching
anything; refuse a downgrade; extract to a fresh versioned folder; run a
smoke check; only then flip `current_version.txt`; leave the previous
version in place untouched if the smoke check fails. `latest.json` is only
written after the zip is staged and its hash is confirmed, then re-read to
confirm what's actually on disk.

`packaging\make_release_zip.ps1 -Version X.Y.Z` builds `Smarty_vX.Y.Z.zip`
and `latest.json` locally under `release\`. **It does not copy anything to
`T:\`** — that mapping hasn't been verified from this machine, and
publishing is a deliberate action for a person on a machine that can see
the real share, not something a build script should do by itself.

## Level 1 scope vs. later

Shipped now: catalog/journal/sync/import/updater core, a working three-pane
PySide6 UI, a frozen `Smarty.exe` built and smoke-tested on this machine,
with the real 69-record catalog loaded.

**Not built, and should not be assumed working:**

- No real two-PC test: everything above was verified with two `Store`
  instances pointed at one temp "shared" folder in the same test process,
  not two physical laptops talking over the actual `\\...\Arhiva` share.
  The sync/lock/backup logic is unit-tested against that simulated share,
  not proven against real network latency, SMB locking quirks, or a truly
  simultaneous write from two machines.
- The `T:\TowerHill\Sparky` mapping itself is unverified from this build
  machine (confirmed only that *some* `T:\` drive is reachable here with
  unrelated content on it — not that it's the same share Rudy/Lumi's
  laptops see).
- No MSI/installer wizard — "installer" here means a zip + a PowerShell
  script that copies it to `%LocalAppData%\Programs\Smarty` and makes a
  desktop shortcut, both of which were actually run on this machine (see
  Test plan below), not just written.
- `python -m sparky` is not how this one launches — this is a from-scratch
  build (no `Smarty_source_optional.zip` was available), so the package is
  named `smarty`, not `sparky`. Only the **path and env-var names**
  documented above were kept for compatibility, per the brief.
- No automated background content-refresh-via-manifest loop is wired into
  the UI startup beyond the notes-journal sync; the catalog-manifest half
  of "content refresh" (`smarty.importer.validate_manifest_filename` +
  revision rules) is implemented and tested but not yet called from
  `app.py`'s startup sequence.
- No Tauri/other native wrap — explicitly out of scope, not attempted.

## Test plan — what was actually run, on this machine

Platform: **Windows 11** (not simulated/cross-compiled), via this session's
shell. Python 3.14.6, PySide6 6.12.0, in `.venv` at `C:\TowerHill\Smarty\.venv`.

```powershell
cd C:\TowerHill\Smarty
.\.venv\Scripts\Activate.ps1
python -m pytest tests -q
```

**Result: 100 passed, 0 failed.** Covers: seed validation (missing fields,
invented scores rejected), journal conflict reduction (independent fields,
supersession, divergent-edit conflicts kept until resolved, resolution
clears them), store read/write round-trips, importer revision rules
(add/update/stale/same-revision-alternate/idempotent/batch-id-replay/
unknown-category-reject/duplicate-id-reject, end-to-end `import_file`
writing the cache only on success), device-label config (blank by
default, persists once typed, other config fields untouched), sync
(offline, missing `Data` dir never auto-created, two simulated devices
converge, stale device can't resurrect a rejection, damaged line preserved
not discarded, lock-busy vs. lock-expired-and-stolen, only 5 auto-backups
kept and a manual backup file untouched), updater (bad filename rejected,
downgrade refused, hash mismatch rejected, failed smoke check leaves the
previous version in place, successful stage + switch, manifest only
publishable after the zip is staged), and offscreen UI checks (window
title is "Smarty", column order is tiles → detail → list — not the
conventional list/detail split — note typed and reloaded in a fresh
window still has it, reject requires two clicks, the "kept is not
approval" line is on screen, device-label button starts blank and takes
a typed label, importing a batch through the UI adds the record and the
bot filter grows without duplicating on repeated refresh), the web app
(login gate, tiles/detail/notes/two-click-reject all working the same way
as desktop, sync API bearer-token auth), and cloud sync integration tests
that start a **real** `smarty.web.app` instance in a background thread and
talk to it over **real HTTP** (not mocked): a laptop pushes edits and a
second laptop pulls and sees them, a wrong token is rejected, and a
browser-made edit (simulating the iPad) reaches a laptop that syncs
afterward. Also covers `/api/ingest` (schema endpoint needs no auth,
wrong/missing token rejected, new idea added and shows up immediately,
invalid category rejected, a status-view label specifically rejected even
though it's technically in the same seed list, resubmitting the same id
doesn't duplicate, and — the one that mattered most — existing notes and
status survive a resubmission untouched).

The deployed web app uses a dark blue / white theme
(`src/smarty/web/static/style.css`), checked visually in the browser at
phone width, not just by the tests above (which don't assert on color).

Two real bugs this project caught and fixed, both found by writing
end-to-end checks rather than only unit tests in isolation:

1. The importer wasn't tagging incoming records with `kind: "idea"` /
   `kind: "performance"` based on which list they came from, so a batch
   file without an explicit `"kind"` field on each record (the realistic
   case) would import successfully but then silently vanish from the
   catalog view. Fixed in `smarty/importer.py::apply_import_batch`.
2. The catalog-cache round-trip (`load_cache` → `_record_dicts`) used a
   generic `dataclasses.asdict`, which serializes under this app's own
   Python attribute names (`received_period`, a flat
   `missing_source_note`) instead of the real seed schema's key names
   (`received_date`/`period`, a nested `evidence` object) that
   `Idea.from_dict`/`PerformanceRecord.from_dict` expect. After exactly
   one cache write-then-read, every record's received date silently
   became "None to None" and every missing-source note silently became
   blank — caught by a full-app smoke test that actually opened a record
   and read its rendered text, not by the narrower unit tests, which is
   why `to_cache_dict()` methods now exist as the deliberate inverse of
   `from_dict` and there's a regression test
   (`test_load_cache_from_fresh_catalog_preserves_received_date_and_missing_source_note`)
   pinning this.

Separately, end-to-end smoke tests actually run on this machine (not just
unit tests):

- `python smarty_launcher.py`-equivalent entry point built and launched
  under `QT_QPA_PLATFORM=offscreen` against the real 69-record catalog:
  confirmed all 69 show unreviewed/blank notes, confirmed per-tile counts
  (Weekly bots performance 10, Growth and enrolment 18, New audiences and
  channels 9, Parent engagement and retention 17, Teaching–Professor
  ideas 19, Learning Dragon ideas 6, Miscellaneous 1 — tiles overlap by
  design, so these don't need to sum to 59), confirmed the Professor
  weekly-performance record renders "documented_partial" and "v61
  published" correctly, confirmed an idea with no source URL
  (`sparky-idea-drifting-students`) renders its exact
  `missing_source_note` text, device id/label reported blank rather than
  the hostname, and did **not** create anything under
  `T:\TowerHill\Sparky`.
- `packaging\build_windows.ps1` actually run three times, as the source
  changed under it (first scaffold, then import/device-label, then the
  real-schema rewrite): produced a real `dist\Smarty\Smarty.exe` (~122 MB
  one-dir build) via PyInstaller 6.22.3 each time. Every build was
  launched (offscreen) and stayed running without error.
- `packaging\create_shortcut.ps1` actually run after each rebuild: copied
  the current build to `C:\Users\<you>\AppData\Local\Programs\Smarty` and
  (re)created `C:\Users\<you>\Desktop\Smarty.lnk`, pointing at the latest
  build (now carrying the real 69-record catalog). The installed copy's
  `Smarty.exe` was also launched (offscreen) and stayed running each time.
- `packaging\make_release_zip.ps1 -Version 0.1.0` actually run: produced
  `release\Smarty_v0.1.0.zip` and `release\latest.json`; the manifest's
  SHA-256 was independently recomputed with Python's `hashlib` and
  matched.

What this does **not** prove: nobody looked at a rendered window on an
actual monitor (this session has no attached display — "offscreen" means
Qt never opened a real window surface, just exercised the same code path).
Before trusting it for real use, open it from the desktop shortcut
yourselves and look at it at 1366×768 and 1280×800.

No Linux results exist for this build — it was written and tested fresh
on Windows, not ported from the earlier Linux/PySide6 build (which was not
available as source).
