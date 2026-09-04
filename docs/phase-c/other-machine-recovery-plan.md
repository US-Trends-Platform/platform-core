# Recovering work from the other computer — do this, not that

**Written:** 2026-09-04
**Read this BEFORE copying anything across from the other machine.**

## The situation

The database described in earlier session notes (318 standardized GDP rows, 942
unemployment rows) was not present on the Windows development machine on
2026-09-04. Docker there held a single volume, created that day, and had
previously run nothing but `hello-world` containers. A copy is believed to exist
on another computer that was not reachable at the time.

Rather than wait, the database was rebuilt from version control and re-ingested
from FRED. **It reproduced the original numbers exactly** — 322 raw rows, 318
standardized (`OFFICIAL_MEASUREMENT`, 1947-01-01 → 2026-04-01), and 4
`missing_data_records` for the four quarters of 1946. That match is strong
evidence the rebuild is faithful, not approximate.

## The one thing that actually matters

**Code is not at risk. Git handles code.** Everything on this branch is pushed to
`US-Trends-Platform/platform-core`. If the other machine has different code, Git
will show you exactly what differs and let you merge deliberately.

Only two things are genuinely at risk:

1. **The database** — Postgres data does not live in Git.
2. **Files that exist only on that machine and were never committed.**

Everything below is about those two.

## Golden rules

1. **Never drag-and-drop folders over the top of this repository.** That silently
   overwrites newer work with older work and leaves no record. It is the single
   most likely way to lose the work done since.
2. **Never merge the two databases.** Pick one. See below for why.
3. **Never run `git add .`** — add files individually. An accidental `git add .`
   once staged 36 unintended files.
4. **`docs/phase-a/Approved Master Plan.md` must never be committed.**

## When the other computer is available — step by step

### Step 1: Find out what is actually different, before changing anything

On the other machine, in its copy of the repo:

```bash
git log --oneline -10
```

```bash
git status
```

`git log` tells you whether it has commits that were never pushed. `git status`
tells you which files were never committed at all. **Send both outputs to your
assistant before copying anything.** Do not act on assumptions about what that
machine has.

### Step 2: Rescue uncommitted code, if any

If `git status` shows uncommitted work you want to keep, push it from that
machine on its own branch — never by copying files:

```bash
git checkout -b recovered/from-other-machine
```

```bash
git push origin recovered/from-other-machine
```

It then appears on GitHub as a separate branch and can be compared and merged
deliberately. Nothing is overwritten, and nothing is lost if it turns out to be
older.

### Step 3: Decide about the database — pick ONE, do not merge

This is the decision that matters most.

**Why merging is not an option.** `seed_from_data_dictionary.py` derives every
`metric_id` deterministically from the metric slug (UUID v5). The old database
generated them randomly (`uuid_generate_v4()`). **The same metric therefore has a
different `metric_id` in each database.** Observation rows reference metrics by
that id, so copying observations between the two produces rows pointing at
metrics that do not exist. The result is silent, hard-to-detect corruption —
exactly the failure mode this project's principles exist to prevent.

You have two clean options.

**Option A — keep the recovered database** (has both GDP and unemployment data):

```bash
python seed_from_data_dictionary.py
```

Idempotent. Adds only the metrics it is missing, leaves every existing row
untouched. Its `unemployment_rate` data survives.

**Option B — keep the rebuilt database** (currently GDP only). Re-run ingestion
for anything missing. The raw data lives at the Federal Reserve and the scripts
are in Git, so this costs minutes, not work.

Either is defensible. What is not defensible is running both and losing track of
which is authoritative.

### Step 4: Resolve the unemployment naming conflict

Deliberately left open on 2026-09-04, pending exactly this recovery.

| Source | Slug |
|---|---|
| `docs/phase-a/data-dictionary.yaml` | `unemployment_rate_total` |
| Transformation scripts + old database | `unemployment_rate` |

`seed_from_data_dictionary.py` exits with code **2** and prints a warning about
this. That is deliberate, not a failure — it is a standing reminder.

**Once you can see which name the recovered database actually uses, pick that
one** and make the other match it. If it uses `unemployment_rate`, change the
dictionary (a documentation edit, nothing breaks). Then delete the
`SLUGS_REQUIRED_BY_CODE` warning path from the seed script, and the exit code
returns to 0.

## Rebuilding from scratch, any time, on any machine

This now works from a clean clone — it did not before 2026-09-04:

```bash
cd backend
```

```bash
docker compose up -d
```

```bash
alembic upgrade head
```

```bash
python seed_from_data_dictionary.py
```

```bash
python test_fred_ingestion.py
```

```bash
python app/transformations/standardize_fred_gdp.py
```

Expected result: 10 domains, 7 confidence tiers, 30 metrics, 2 transformation
scripts, 322 raw observations, 318 standardized, 4 missing-data records.

**If those numbers do not match, stop and investigate before continuing.** They
are the project's known-good fingerprint.
