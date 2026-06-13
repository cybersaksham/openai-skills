import CoreGraphics
import Darwin
import Foundation

func usage() -> Never {
    FileHandle.standardError.write(Data("Usage: pointer.swift click <x> <y> | drag <x1> <y1> <x2> <y2> [duration] | release [x y]\n".utf8))
    exit(2)
}

func point(_ x: String, _ y: String) -> CGPoint {
    guard let px = Double(x), let py = Double(y) else {
        usage()
    }
    return CGPoint(x: px, y: py)
}

func currentPointerLocation() -> CGPoint {
    CGEvent(source: nil)?.location ?? CGPoint(x: 0, y: 0)
}

func post(_ type: CGEventType, at point: CGPoint, button: CGMouseButton = .left) {
    let event = CGEvent(mouseEventSource: nil, mouseType: type, mouseCursorPosition: point, mouseButton: button)
    event?.post(tap: .cghidEventTap)
}

func releaseMouseButtons(at point: CGPoint) {
    post(.leftMouseUp, at: point, button: .left)
    post(.rightMouseUp, at: point, button: .right)
    post(.otherMouseUp, at: point, button: .center)
}

func ignoreTerminationSignals() {
    signal(SIGINT, SIG_IGN)
    signal(SIGTERM, SIG_IGN)
    signal(SIGHUP, SIG_IGN)
}

func restoreTerminationSignals() {
    signal(SIGINT, SIG_DFL)
    signal(SIGTERM, SIG_DFL)
    signal(SIGHUP, SIG_DFL)
}

func normalizedDuration(_ raw: String?) -> Double {
    guard let raw, let parsed = Double(raw), parsed.isFinite else {
        return 0.35
    }

    return min(max(parsed, 0.01), 2.0)
}

let args = Array(CommandLine.arguments.dropFirst())
guard let command = args.first else {
    usage()
}

switch command {
case "click":
    guard args.count == 3 else {
        usage()
    }
    let target = point(args[1], args[2])
    var mouseIsDown = false

    ignoreTerminationSignals()
    defer {
        if mouseIsDown {
            releaseMouseButtons(at: target)
        }
        restoreTerminationSignals()
    }

    post(.mouseMoved, at: target)
    usleep(20_000)
    post(.leftMouseDown, at: target)
    mouseIsDown = true
    usleep(40_000)
    post(.leftMouseUp, at: target)
    mouseIsDown = false

case "drag":
    guard args.count == 5 || args.count == 6 else {
        usage()
    }
    let start = point(args[1], args[2])
    let end = point(args[3], args[4])
    let duration = normalizedDuration(args.count == 6 ? args[5] : nil)
    let steps = max(8, Int(duration * 60))
    let sleepMicros = useconds_t(max(1_000, Int(duration * 1_000_000) / steps))
    var lastPoint = start
    var mouseIsDown = false

    ignoreTerminationSignals()
    defer {
        if mouseIsDown {
            releaseMouseButtons(at: lastPoint)
        }
        restoreTerminationSignals()
    }

    post(.mouseMoved, at: start)
    usleep(20_000)
    post(.leftMouseDown, at: start)
    mouseIsDown = true

    for step in 1...steps {
        let progress = Double(step) / Double(steps)
        let current = CGPoint(
            x: start.x + ((end.x - start.x) * progress),
            y: start.y + ((end.y - start.y) * progress)
        )
        lastPoint = current
        post(.leftMouseDragged, at: current)
        usleep(sleepMicros)
    }

    post(.leftMouseUp, at: end)
    mouseIsDown = false

case "release":
    guard args.count == 1 || args.count == 3 else {
        usage()
    }
    let target = args.count == 3 ? point(args[1], args[2]) : currentPointerLocation()
    releaseMouseButtons(at: target)

default:
    usage()
}
