import Foundation
import ImageIO
import Vision

struct OCRRow {
    let text: String
    let confidence: Float
    let x: CGFloat
    let y: CGFloat
    let width: CGFloat
    let height: CGFloat
}

func usage() -> Never {
    FileHandle.standardError.write(Data("Usage: vision-ocr.swift [--boxes] <image.png>\n".utf8))
    exit(2)
}

let args = CommandLine.arguments.dropFirst()
let boxesMode = args.contains("--boxes")
guard let imagePath = args.first(where: { !$0.hasPrefix("--") }) else {
    usage()
}

let imageURL = URL(fileURLWithPath: imagePath)
guard let imageSource = CGImageSourceCreateWithURL(imageURL as CFURL, nil),
      let image = CGImageSourceCreateImageAtIndex(imageSource, 0, nil) else {
    FileHandle.standardError.write(Data("Error: could not read image: \(imagePath)\n".utf8))
    exit(1)
}

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = true

let handler = VNImageRequestHandler(cgImage: image, options: [:])
do {
    try handler.perform([request])
} catch {
    FileHandle.standardError.write(Data("Error: Vision OCR failed: \(error)\n".utf8))
    exit(1)
}

let observations = request.results ?? []
let rows = observations.compactMap { observation -> OCRRow? in
    guard let candidate = observation.topCandidates(1).first else {
        return nil
    }

    let box = observation.boundingBox
    return OCRRow(
        text: candidate.string.replacingOccurrences(of: "\t", with: " ").replacingOccurrences(of: "\n", with: " "),
        confidence: candidate.confidence,
        x: box.minX,
        y: 1.0 - box.maxY,
        width: box.width,
        height: box.height
    )
}
.sorted { left, right in
    if abs(left.y - right.y) > 0.015 {
        return left.y < right.y
    }
    return left.x < right.x
}

if boxesMode {
    for row in rows {
        print(String(format: "%.6f\t%.6f\t%.6f\t%.6f\t%.3f\t%@", Double(row.x), Double(row.y), Double(row.width), Double(row.height), row.confidence, row.text))
    }
} else {
    for row in rows {
        print(row.text)
    }
}
