"""Source-backed coverage inventory for journeys, flows, implementation units, and clients.

Populate these lists from repository or greenfield architecture discovery. Final validation
requires every listed item to resolve to one focused page and every focused page to resolve
back to one inventory entry. Never group unrelated implementation units merely to reduce pages.
"""

PRODUCT_JOURNEY_INVENTORY = []
FEATURE_INVENTORY = []
ARCHITECTURE_FLOW_INVENTORY = []
RUNTIME_MODULE_INVENTORY = []
CLIENT_SURFACE_INVENTORY = []

# Final specifications must configure repository-backed discovery roots. Each root is a
# dictionary with `path`, `mode`, and `include_extensions`:
#
# {"path": "backend/internal", "mode": "child-directories", "include_extensions": [".go"]}
# {"path": "backend/config", "mode": "root", "include_extensions": [".py"]}
#
# Supported modes are `child-directories`, `child-files`, and `root`. Root mode covers direct
# source files only and must be paired with child-directories on the same path when source-bearing
# child packages exist. Every discovered source unit maps one-to-one to
# RUNTIME_MODULE_INVENTORY[].source_unit and its own unique focused page route. Exclusions remain visible and require a concrete
# non-runtime reason; never exclude a unit merely to combine pages.
RUNTIME_DISCOVERY_ROOTS = []
RUNTIME_DISCOVERY_EXCLUSIONS = []

# RUNTIME_MODULE_INVENTORY entries use role `settings`, `common`, or `implementation`.
# Final specifications require one settings and one common owner unless the product truly has
# no such boundary and the corresponding reason below explains where that responsibility lives
# in at least twenty characters.
RUNTIME_SETTINGS_NOT_APPLICABLE_REASON = ""
RUNTIME_COMMON_NOT_APPLICABLE_REASON = ""

# For a genuinely API-only, worker-only, library-only, or otherwise clientless product, set a
# concrete reason. Keep this empty when client surfaces exist or the decision remains open.
CLIENT_SURFACES_NOT_APPLICABLE_REASON = ""
