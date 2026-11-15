"""Footage types and their buckets. Buckets are editable per project in the app."""

PRESETS = {
    "wedding": [
        "getting ready", "ceremony", "couple portraits", "family & groups",
        "speeches", "first dance", "dance floor", "details & decor",
        "drone & aerial", "guest moments", "behind the scenes", "other",
    ],
    "production": [
        "interview & a-roll", "b-roll", "product shots", "drone & aerial",
        "behind the scenes", "screen recording", "stills & plates", "other",
    ],
}
DEFAULT_PRESET = "wedding"
CONTEXTS = {
    "wedding": "a wedding studio's project folder (one couple's event, possibly several cameras)",
    "production": "a production house's project folder (one client shoot, possibly several cameras)",
}
SETTINGS = ["indoor", "outdoor", "mixed", "unknown"]
FALLBACK_BUCKET = "other"
MAX_BUCKETS = 40
MAX_BUCKET_LENGTH = 40


def normalize_buckets(raw):
    """Clean a user-edited bucket list: trimmed, lower-case, unique, with the
    fallback bucket always present so every clip has somewhere to land."""
    buckets = []
    for item in raw or []:
        name = " ".join(str(item).split()).lower()[:MAX_BUCKET_LENGTH]
        if name and name not in buckets:
            buckets.append(name)
    if FALLBACK_BUCKET in buckets:
        buckets.remove(FALLBACK_BUCKET)
    buckets = buckets[:MAX_BUCKETS - 1]
    buckets.append(FALLBACK_BUCKET)
    return buckets
