import Foundation
import Darwin

/// Opt-in bounded source-activation diagnostic. Does not change routing or buffers.
final class ExpertActivationTrace: @unchecked Sendable {
    static let shared: ExpertActivationTrace? = {
        guard let path = ProcessInfo.processInfo.environment["SWIFTLET_ACTIVATION_TRACE"] else { return nil }
        return ExpertActivationTrace(path: path)
    }()
    private let lock = NSLock()
    private let file: FileHandle
    private var counts: [String: Int] = [:]
    private var sequence = 0

    private init(path: String) {
        let fd = open(path, O_WRONLY | O_CREAT | O_EXCL, 0o600)
        guard fd >= 0 else { fatalError("Activation trace requires a new writable file") }
        file = FileHandle(fileDescriptor: fd, closeOnDealloc: true)
    }

    func capture(layer: Int, position: Int, phase: String,
                 input: @autoclosure () -> [Float], experts: [Int], weights: [Float]) {
        guard [0, 20, 39].contains(layer) else { return }
        lock.lock()
        defer { lock.unlock() }
        let key = "\(phase):\(layer)"
        let count = counts[key, default: 0]
        guard count < 4 && sequence < 24 else { return }
        let x = input()
        guard x.count == 2048, experts.count == 8, Set(experts).count == 8,
              weights.count == 8, x.allSatisfy(\.isFinite), weights.allSatisfy(\.isFinite),
              experts.allSatisfy({ (0..<256).contains($0) }) else {
            fatalError("Invalid source activation fixture")
        }
        // Integer IEEE-754 bit patterns survive JSON without decimal float drift.
        let record: [String: Any] = [
            "sequence": sequence, "layer": layer, "position": position,
            "schedule": phase, "schedule_layer_ordinal": count,
            "input_f32_bits": x.map(\.bitPattern), "experts": experts,
            "weights_f32_bits": weights.map(\.bitPattern)
        ]
        do {
            var data = try JSONSerialization.data(withJSONObject: record, options: [.sortedKeys])
            data.append(10)
            try file.write(contentsOf: data)
        } catch { fatalError("Activation fixture write failed: \(error)") }
        counts[key] = count + 1
        sequence += 1
    }
}
