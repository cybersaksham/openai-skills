"""Atomic input coverage and confirmed decision registers."""

# Required row keys:
# id, source, text, kind, area, destinations, status, notes
# status: covered | superseded | pending
# `pending` is the exact unresolved drafting literal; never store `pending while drafting`.
REQUIREMENTS = []

# Required row keys:
# id, question, choice, rationale, consequences, affected, confirmation, status
# status: confirmed | pending
# `pending` is the exact unresolved drafting literal; final documentation contains none.
DECISIONS = []
