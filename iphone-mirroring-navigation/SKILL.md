---
name: iphone-mirroring-navigation
description: Use when the user asks to control, navigate, inspect, read, OCR, or automate a mirrored iPhone UI in macOS iPhone Mirroring.
---

# iPhone Mirroring Navigation

Use this skill when a user asks for controlled navigation or screen inspection in the iPhone Mirroring window.

## Quick start

From this skill folder:

```bash
cd /Users/cybersaksham/.codex/skills/iphone-mirroring-navigation
./scripts/mirror-nav.sh <action> [arguments]
```

## Actions

Common actions:

- `focus` — focus the iPhone Mirroring app.
- `home` — send `Command+1` (Home).
- `app-switcher` — send `Command+2` (App Switcher).
- `spotlight` — send `Command+3` (Spotlight).
- `open-app "<app>"` — launch app by name via Spotlight.
- `type-text "<text>"` — type text into active mirrored input.
- `return` — send Return.
- `read-screen [output.png]` — capture the visible iPhone Mirroring window to PNG and print the path.
- `read-screen-ocr [output.png]` — capture the screen and OCR it immediately.
- `ocr-screen [image.png]` — OCR an existing captured image.
- `ocr-boxes [image.png]` — OCR visible text with normalized `x y w h confidence text` boxes.
- `find-text "<pattern>" [image.png]` — OCR an image or current screen and print only matching lines.
- `wait-for-text "<pattern>" [timeout] [interval]` — repeatedly capture and OCR until matching text appears.
- `tap-ratio <x> <y>` — tap a relative point in the mirrored window using values from `0.0` to `1.0`.
- `tap-pixel <x> <y> [image.png]` — tap a pixel coordinate from a captured image.
- `tap-text "<pattern>" [image.png]` — OCR visible labels and tap the first text match.
- `swipe-ratio <x1> <y1> <x2> <y2> [duration]` — drag between two relative points.
- `scroll-down [short|medium|long]` — reveal lower content with an upward finger drag.
- `scroll-up [short|medium|long]` — reveal earlier content with a downward finger drag.

## Stable workflow sequence

1. Run `focus` first.
2. Run `read-screen-ocr` when the next action depends on visible UI state.
3. Use `tap-text` when the desired target has a visible label.
4. Use `scroll-down` or `scroll-up` for list/page movement.
5. Use `tap-ratio`, `tap-pixel`, or `swipe-ratio` for icon-only targets and custom gestures.
6. Run `home`, `app-switcher`, or `spotlight` as needed.
7. For app launch, run `open-app "<app name>"` directly.
8. Use `type-text` + `return` for search boxes where needed.

## Read-and-act loop

Use this generic loop for app workflows:

```bash
./scripts/mirror-nav.sh read-screen-ocr
./scripts/mirror-nav.sh open-app "<app name>"
./scripts/mirror-nav.sh find-text "<visible text pattern>"
./scripts/mirror-nav.sh tap-text "<visible label pattern>"
./scripts/mirror-nav.sh scroll-down medium
./scripts/mirror-nav.sh scroll-up short
./scripts/mirror-nav.sh swipe-ratio 0.5 0.8 0.5 0.3
./scripts/mirror-nav.sh wait-for-text "<visible text pattern>" 15 1
```

After each screen read, use OCR output to choose the next generic action. Keep app-specific rules in the calling workflow, not inside this skill.

## Scrolling

iPhone Mirroring does not expose app internals. Treat scrolling as a touchscreen gesture in the mirrored window:

- To reveal lower content, use `scroll-down`; internally it drags from lower screen to upper screen.
- To reveal earlier content, use `scroll-up`; internally it drags from upper screen to lower screen.
- Use `short`, `medium`, or `long` based on how much content should move.
- Use `swipe-ratio <x1> <y1> <x2> <y2> [duration]` when a screen needs a custom gesture, carousel movement, or horizontal swipe.
- After scrolling, run `read-screen-ocr` or `find-text` again because OCR reflects only the current visible screen.

## Notes

- `read-screen` captures the mirrored window.
- OCR defaults to `OCR_ENGINE=auto`, which tries macOS Vision first and falls back to tesseract through stdin.
- Set `OCR_ENGINE=vision` or `OCR_ENGINE=tesseract` to force one engine.
- `ocr-boxes` and `tap-text` use macOS Vision because bounding boxes are needed for navigation.
- `wait-for-text` is useful after opening apps, submitting searches, navigating screens, or waiting for loading states.
- `tap-ratio` is the most stable way to tap icon-only UI; `tap-pixel` is useful when working from a saved screenshot.
- Prefer `scroll-down` and `scroll-up` over mouse wheel scrolling; iPhone apps respond more consistently to drag gestures.
- If an action appears ignored, rerun `focus` and execute the action again.
- This skill does not pair new devices; it only sends navigation input.
- Passwords, OTPs, payment confirmations, and secure screens may be hidden or should be handled manually by the user.

## Reference

- [shortcut-map.md](references/shortcut-map.md)
