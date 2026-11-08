APP_NAME = "Smarty"
APP_VERSION = "0.1.0"
CONTENT_VERSION = "2026-11-07.1"

# A record counts as "new" (gets the color-coded NEW badge) while it's
# still unreviewed and was first added within this many days -- matches
# roughly two Grok-bot ingest cycles on a twice-weekly schedule, so a
# fresh idea stays flagged through the next check-in before fading to
# ordinary backlog.
NEW_IDEA_WINDOW_DAYS = 7

# Content tiles, keyed by their exact category label text (matches how
# records reference a category in the real seed: Idea/PerformanceRecord
# .categories holds label strings, not a slug).
CATEGORIES_ORDER = [
    "Weekly bots performance",
    "Growth and enrolment",
    "New audiences and channels",
    "Parent engagement and retention",
    "Teaching–Professor ideas",
    "Learning Dragon ideas",
    "Miscellaneous",
]

# Status views are a separate concept (filtered by UserState.status, not by
# a record's categories), so these stay internal slugs.
STATUS_VIEWS_ORDER = [
    "rudys_collection",
    "park_it_for_later",
    "rejected_recoverable",
]

# Web-app-only bucket labels (desktop keeps its own simpler "Rudy's
# collection" = kept, undifferentiated by buffer/archive -- these are
# additive, new names used only by smarty.web.app, not a rename of the
# shared STATUS_VIEW_* maps above).
WEB_BUFFER_LABEL = "Buffered ideas waiting to be sent to Grok-Bots"
WEB_PARKED_LABEL = "Ideas Parked worth reviewing"
WEB_REJECTED_LABEL = "Rejected (recoverable)"
WEB_ARCHIVE_LABEL = "Rudy's collection of actionable ideas"
