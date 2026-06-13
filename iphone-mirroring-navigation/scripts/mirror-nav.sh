#!/usr/bin/env bash

set -euo pipefail

APP_NAME="iPhone Mirroring"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OCR_LANG="${OCR_LANG:-eng}"
OCR_ENGINE="${OCR_ENGINE:-auto}"
OCR_PSM="${OCR_PSM:-6}"
VISION_OCR_SCRIPT="${SCRIPT_DIR}/vision-ocr.swift"
POINTER_SCRIPT="${SCRIPT_DIR}/pointer.swift"
POINTER_CLEANUP_NEEDED=0
POINTER_PID=""
POINTER_WATCHDOG_PID=""

USAGE="Usage: $(basename "$0") <action> [args...]
Actions:
  focus                          Bring iPhone Mirroring to front
  home                           Send command+1 (Home)
  app-switcher                   Send command+2 (App Switcher)
  spotlight                      Send command+3 (Spotlight)
  open-app \"<app name>\"           Open app by name using Spotlight
  type-text \"<text>\"              Type text into the active field in remote session
  return                         Send Return key
  read-screen [output.png]         Capture the iPhone Mirroring window to PNG
  read-screen-ocr [output.png]     Capture and OCR the mirrored screen in one step
  ocr-screen [image.png]           OCR an existing screen capture and print text
  ocr-boxes [image.png]            OCR with text boxes as x/y/w/h ratios
  find-text \"<pattern>\" [image.png] OCR an image or current screen and print matching lines
  wait-for-text \"<pattern>\" [timeout] [interval] Capture repeatedly until matching text appears
  tap-ratio <x> <y>                Tap relative window coordinates from 0.0 to 1.0
  tap-pixel <x> <y> [image.png]    Tap image pixel coordinates from a capture
  tap-text \"<pattern>\" [image.png] OCR visible labels and tap the first match
  swipe-ratio <x1> <y1> <x2> <y2> [duration] Drag between relative coordinates
  scroll-down [amount]             Scroll to lower content with an upward finger drag
  scroll-up [amount]               Scroll to earlier content with a downward finger drag
"

run_osascript() {
  /usr/bin/osascript "$@"
}

release_pointer() {
  if command -v swift >/dev/null 2>&1 && [ -f "${POINTER_SCRIPT}" ]; then
    swift "${POINTER_SCRIPT}" release >/dev/null 2>&1 || true
  fi
}

cleanup_pointer() {
  if [ -n "${POINTER_WATCHDOG_PID:-}" ]; then
    kill "${POINTER_WATCHDOG_PID}" 2>/dev/null || true
  fi

  if [ -n "${POINTER_PID:-}" ] && kill -0 "${POINTER_PID}" 2>/dev/null; then
    kill "${POINTER_PID}" 2>/dev/null || true
    sleep 0.1
    kill -9 "${POINTER_PID}" 2>/dev/null || true
  fi

  if [ "${POINTER_CLEANUP_NEEDED:-0}" = "1" ]; then
    release_pointer
    POINTER_CLEANUP_NEEDED=0
  fi
}

handle_pointer_signal() {
  local status=$1

  cleanup_pointer
  exit "${status}"
}

trap cleanup_pointer EXIT
trap 'handle_pointer_signal 129' HUP
trap 'handle_pointer_signal 130' INT
trap 'handle_pointer_signal 143' TERM

focus_app() {
  run_osascript -e "tell application \"${APP_NAME}\" to activate"
}

press_command_key() {
  local key_code=$1
  run_osascript -e "tell application \"System Events\" to key code ${key_code} using {command down}"
}

spotlight() {
  press_command_key 20
}

press_return() {
  run_osascript -e 'tell application "System Events" to key code 36'
}

send_text() {
  local text=$1
  run_osascript - "$text" <<'EOF'
on run argv
tell application "System Events"
  keystroke (item 1 of argv)
end tell
end run
EOF
}

clear_text_field() {
  run_osascript -e 'tell application "System Events" to keystroke "a" using {command down}'
  run_osascript -e 'tell application "System Events" to key code 51'
}

open_app() {
  local target=$1
  if [ -z "${target}" ]; then
    echo "Error: open-app requires an app name." >&2
    exit 1
  fi
  spotlight
  sleep 0.2
  clear_text_field
  send_text "${target}"
  sleep 0.2
  press_return
}

default_capture_path() {
  local output_dir="${TMPDIR:-/tmp}/iphone-mirroring-navigation"
  mkdir -p "${output_dir}"
  printf "%s/iphone-mirroring-%s.png\n" "${output_dir}" "$(date +%Y%m%d-%H%M%S)"
}

window_rect() {
  run_osascript <<'EOF'
tell application "System Events"
  if not (exists process "iPhone Mirroring") then error "iPhone Mirroring is not running"
  tell process "iPhone Mirroring"
    set frontmost to true
    if (count of windows) is 0 then error "No iPhone Mirroring window is available"
    set targetWindow to window 1
    set windowPosition to position of targetWindow
    set windowSize to size of targetWindow
    return {item 1 of windowPosition, item 2 of windowPosition, item 1 of windowSize, item 2 of windowSize}
  end tell
end tell
EOF
}

read_screen() {
  local output=${1:-}
  local rect

  if [ -z "${output}" ]; then
    output=$(default_capture_path)
  elif [[ "${output}" != /* ]]; then
    output="${PWD}/${output}"
  fi

  mkdir -p "$(dirname "${output}")"
  rect=$(window_rect)
  rect=$(printf "%s" "${rect}" | tr -d "[:space:]")

  if ! /usr/sbin/screencapture -x -R "${rect}" "${output}"; then
    echo "Error: could not capture iPhone Mirroring window. Check macOS Screen Recording permission for the calling app/terminal." >&2
    exit 2
  fi

  printf "%s\n" "${output}"
}

read_ocr_tesseract() {
  local image=$1
  local psm=${2:-${OCR_PSM}}

  if [ ! -f "${image}" ]; then
    echo "Error: image file not found: ${image}" >&2
    return 1
  fi

  if ! command -v tesseract >/dev/null 2>&1; then
    echo "Error: tesseract is not installed or not in PATH." >&2
    return 1
  fi

  if ! cat "${image}" | tesseract stdin stdout -l "${OCR_LANG}" --psm "${psm}"; then
    return 1
  fi
}

read_ocr_vision() {
  local image=$1

  if [ ! -f "${image}" ]; then
    echo "Error: image file not found: ${image}" >&2
    return 1
  fi

  if ! command -v swift >/dev/null 2>&1 || [ ! -f "${VISION_OCR_SCRIPT}" ]; then
    return 1
  fi

  swift "${VISION_OCR_SCRIPT}" "${image}"
}

read_ocr() {
  local image=$1
  local psm=${2:-${OCR_PSM}}
  local vision_output

  case "${OCR_ENGINE}" in
    vision )
      read_ocr_vision "${image}"
      ;;
    tesseract )
      read_ocr_tesseract "${image}" "${psm}"
      ;;
    auto )
      if vision_output=$(read_ocr_vision "${image}" 2>/dev/null) && [ -n "${vision_output}" ]; then
        printf "%s\n" "${vision_output}"
      else
        read_ocr_tesseract "${image}" "${psm}"
      fi
      ;;
    * )
      echo "Error: OCR_ENGINE must be auto, vision, or tesseract." >&2
      return 1
      ;;
  esac
}

read_ocr_boxes() {
  local image=$1

  if [ ! -f "${image}" ]; then
    echo "Error: image file not found: ${image}" >&2
    return 1
  fi

  if ! command -v swift >/dev/null 2>&1 || [ ! -f "${VISION_OCR_SCRIPT}" ]; then
    echo "Error: Vision OCR boxes require /usr/bin/swift and ${VISION_OCR_SCRIPT}." >&2
    return 1
  fi

  swift "${VISION_OCR_SCRIPT}" --boxes "${image}"
}

find_text() {
  local pattern=$1
  local image=${2:-}

  if [ -z "${pattern}" ]; then
    echo "Error: find-text requires a pattern." >&2
    return 1
  fi

  if [ -z "${image}" ]; then
    image=$(default_capture_path)
    read_screen "${image}" >/dev/null
  fi

  read_ocr "${image}" | grep -Ei "${pattern}"
}

window_rect_parts() {
  window_rect | tr -d "[:space:]"
}

global_point_from_ratio() {
  local x_ratio=$1
  local y_ratio=$2
  local rect
  local x
  local y
  local width
  local height

  rect=$(window_rect_parts)
  IFS=',' read -r x y width height <<<"${rect}"

  awk -v x="${x}" -v y="${y}" -v width="${width}" -v height="${height}" -v xr="${x_ratio}" -v yr="${y_ratio}" \
    'BEGIN { printf "%.0f %.0f\n", x + (width * xr), y + (height * yr) }'
}

pointer_click() {
  local x=$1
  local y=$2

  if command -v swift >/dev/null 2>&1 && [ -f "${POINTER_SCRIPT}" ]; then
    run_pointer_command click "${x}" "${y}"
  else
    run_osascript -e "tell application \"System Events\" to click at {${x}, ${y}}"
  fi
}

pointer_timeout_for() {
  local command=$1
  local duration=${6:-0.35}

  if [ "${command}" != "drag" ]; then
    printf "4\n"
    return 0
  fi

  awk -v duration="${duration}" '
    BEGIN {
      if (duration !~ /^[0-9]+([.][0-9]+)?$/) duration = 0.35
      timeout = duration + 3
      if (timeout < 4) timeout = 4
      if (timeout > 8) timeout = 8
      printf "%.2f\n", timeout
    }
  '
}

run_pointer_command() {
  local timeout_seconds
  local status

  timeout_seconds=$(pointer_timeout_for "$@")
  POINTER_CLEANUP_NEEDED=1
  swift "${POINTER_SCRIPT}" "$@" &
  POINTER_PID=$!

  (
    sleep "${timeout_seconds}"
    if kill -0 "${POINTER_PID}" 2>/dev/null; then
      kill "${POINTER_PID}" 2>/dev/null || true
      sleep 0.2
      kill -9 "${POINTER_PID}" 2>/dev/null || true
      release_pointer
    fi
  ) &
  POINTER_WATCHDOG_PID=$!

  if wait "${POINTER_PID}"; then
    status=0
  else
    status=$?
  fi

  kill "${POINTER_WATCHDOG_PID}" 2>/dev/null || true
  wait "${POINTER_WATCHDOG_PID}" 2>/dev/null || true
  POINTER_PID=""
  POINTER_WATCHDOG_PID=""
  release_pointer
  POINTER_CLEANUP_NEEDED=0

  return "${status}"
}

pointer_drag() {
  local x1=$1
  local y1=$2
  local x2=$3
  local y2=$4
  local duration=${5:-0.35}

  if ! command -v swift >/dev/null 2>&1 || [ ! -f "${POINTER_SCRIPT}" ]; then
    echo "Error: swipe-ratio requires /usr/bin/swift and ${POINTER_SCRIPT}." >&2
    return 1
  fi

  run_pointer_command drag "${x1}" "${y1}" "${x2}" "${y2}" "${duration}"
}

tap_ratio() {
  local x_ratio=$1
  local y_ratio=$2
  local point
  local x
  local y

  point=$(global_point_from_ratio "${x_ratio}" "${y_ratio}")
  read -r x y <<<"${point}"
  pointer_click "${x}" "${y}"
}

image_dimensions() {
  local image=$1

  /usr/bin/sips -g pixelWidth -g pixelHeight "${image}" 2>/dev/null | awk '
    /pixelWidth/ { width = $2 }
    /pixelHeight/ { height = $2 }
    END {
      if (width == "" || height == "") exit 1
      print width, height
    }
  '
}

tap_pixel() {
  local pixel_x=$1
  local pixel_y=$2
  local image=${3:-}
  local dimensions
  local width
  local height
  local x_ratio
  local y_ratio

  if [ -z "${image}" ]; then
    image=$(read_screen)
  fi

  dimensions=$(image_dimensions "${image}")
  read -r width height <<<"${dimensions}"
  x_ratio=$(awk -v x="${pixel_x}" -v width="${width}" 'BEGIN { printf "%.6f", x / width }')
  y_ratio=$(awk -v y="${pixel_y}" -v height="${height}" 'BEGIN { printf "%.6f", y / height }')
  tap_ratio "${x_ratio}" "${y_ratio}"
}

tap_text() {
  local pattern=$1
  local image=${2:-}
  local match
  local x
  local y
  local width
  local height
  local confidence
  local text
  local center_x
  local center_y

  if [ -z "${pattern}" ]; then
    echo "Error: tap-text requires a pattern." >&2
    return 1
  fi

  if [ -z "${image}" ]; then
    image=$(read_screen)
  fi

  match=$(read_ocr_boxes "${image}" | awk -F '\t' -v pattern="${pattern}" 'BEGIN { IGNORECASE = 1 } $6 ~ pattern { print; exit }')

  if [ -z "${match}" ]; then
    echo "No visible text matched: ${pattern}" >&2
    return 1
  fi

  IFS=$'\t' read -r x y width height confidence text <<<"${match}"
  center_x=$(awk -v x="${x}" -v width="${width}" 'BEGIN { printf "%.6f", x + (width / 2) }')
  center_y=$(awk -v y="${y}" -v height="${height}" 'BEGIN { printf "%.6f", y + (height / 2) }')
  tap_ratio "${center_x}" "${center_y}"
  printf "Tapped text: %s\n" "${text}"
}

swipe_ratio() {
  local x1_ratio=$1
  local y1_ratio=$2
  local x2_ratio=$3
  local y2_ratio=$4
  local duration=${5:-0.35}
  local start_point
  local end_point
  local x1
  local y1
  local x2
  local y2

  start_point=$(global_point_from_ratio "${x1_ratio}" "${y1_ratio}")
  end_point=$(global_point_from_ratio "${x2_ratio}" "${y2_ratio}")
  read -r x1 y1 <<<"${start_point}"
  read -r x2 y2 <<<"${end_point}"
  pointer_drag "${x1}" "${y1}" "${x2}" "${y2}" "${duration}"
}

scroll_down() {
  local amount=${1:-medium}

  case "${amount}" in
    short )
      swipe_ratio 0.5 0.65 0.5 0.42 0.25
      ;;
    medium )
      swipe_ratio 0.5 0.78 0.5 0.30 0.35
      ;;
    long )
      swipe_ratio 0.5 0.86 0.5 0.18 0.45
      ;;
    * )
      echo "Error: scroll-down amount must be short, medium, or long." >&2
      return 1
      ;;
  esac
}

scroll_up() {
  local amount=${1:-medium}

  case "${amount}" in
    short )
      swipe_ratio 0.5 0.42 0.5 0.65 0.25
      ;;
    medium )
      swipe_ratio 0.5 0.30 0.5 0.78 0.35
      ;;
    long )
      swipe_ratio 0.5 0.18 0.5 0.86 0.45
      ;;
    * )
      echo "Error: scroll-up amount must be short, medium, or long." >&2
      return 1
      ;;
  esac
}

wait_for_text() {
  local pattern=$1
  local timeout_seconds=${2:-15}
  local interval_seconds=${3:-1}
  local start_time
  local now
  local image

  if [ -z "${pattern}" ]; then
    echo "Error: wait-for-text requires a pattern." >&2
    return 1
  fi

  start_time=$(date +%s)

  while true; do
    image=$(default_capture_path)
    read_screen "${image}" >/dev/null

    if find_text "${pattern}" "${image}"; then
      return 0
    fi

    now=$(date +%s)
    if [ $((now - start_time)) -ge "${timeout_seconds}" ]; then
      echo "Timed out waiting for text matching: ${pattern}" >&2
      return 1
    fi

    sleep "${interval_seconds}"
  done
}

focus_app
sleep 0.2

action=${1:-}
shift || true

case "${action}" in
  "" )
    echo "${USAGE}"
    exit 1
    ;;
  focus )
    exit 0
    ;;
  home )
    press_command_key 18
    ;;
  app-switcher | app_switcher )
    press_command_key 19
    ;;
  spotlight )
    press_command_key 20
    ;;
  open-app | open_app | launch )
    open_app "$*"
    ;;
  type-text )
    if [ $# -eq 0 ]; then
      echo "Error: type-text requires a string argument." >&2
      exit 1
    fi
    send_text "$*"
    ;;
  return )
    press_return
    ;;
  read-screen | read_screen | capture-screen | screenshot )
    read_screen "${1:-}"
    ;;
  read-screen-ocr | read_screen_ocr )
    ocr_capture=$(read_screen "${1:-}")
    read_ocr "${ocr_capture}"
    ;;
  ocr-screen | ocr_screen )
    if [ $# -eq 0 ]; then
      echo "Error: ocr-screen requires an image path." >&2
      exit 1
    fi
    read_ocr "$1"
    ;;
  ocr-boxes | ocr_boxes )
    if [ $# -eq 0 ]; then
      ocr_boxes_capture=$(read_screen)
      read_ocr_boxes "${ocr_boxes_capture}"
    else
      read_ocr_boxes "$1"
    fi
    ;;
  find-text | find_text )
    if [ $# -lt 1 ]; then
      echo "Error: find-text requires a pattern." >&2
      exit 1
    fi
    find_text "$1" "${2:-}"
    ;;
  wait-for-text | wait_for_text )
    if [ $# -lt 1 ]; then
      echo "Error: wait-for-text requires a pattern." >&2
      exit 1
    fi
    wait_for_text "$1" "${2:-15}" "${3:-1}"
    ;;
  tap-ratio | tap_ratio )
    if [ $# -lt 2 ]; then
      echo "Error: tap-ratio requires x and y ratios." >&2
      exit 1
    fi
    tap_ratio "$1" "$2"
    ;;
  tap-pixel | tap_pixel )
    if [ $# -lt 2 ]; then
      echo "Error: tap-pixel requires x and y pixel coordinates." >&2
      exit 1
    fi
    tap_pixel "$1" "$2" "${3:-}"
    ;;
  tap-text | tap_text )
    if [ $# -lt 1 ]; then
      echo "Error: tap-text requires a visible text pattern." >&2
      exit 1
    fi
    tap_text "$1" "${2:-}"
    ;;
  swipe-ratio | swipe_ratio )
    if [ $# -lt 4 ]; then
      echo "Error: swipe-ratio requires x1 y1 x2 y2 ratios." >&2
      exit 1
    fi
    swipe_ratio "$1" "$2" "$3" "$4" "${5:-0.35}"
    ;;
  scroll-down | scroll_down )
    scroll_down "${1:-medium}"
    ;;
  scroll-up | scroll_up )
    scroll_up "${1:-medium}"
    ;;
  *)
    echo "Error: unknown action '${action}'." >&2
    echo "${USAGE}" >&2
    exit 1
    ;;
esac
