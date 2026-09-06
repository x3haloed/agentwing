import Foundation
import Darwin

/// Diagnostic only. Never alters logits, counts, or the chosen token.
final class SamplingTrace: @unchecked Sendable {
    private let handle: FileHandle
    private let lock = NSLock()
    private var ordinal = 0
    private var failed = false

    init(path: String) throws {
        let fd = Darwin.open(path, O_WRONLY | O_CREAT | O_EXCL, mode_t(0o600))
        guard fd >= 0 else { throw POSIXError(POSIXErrorCode(rawValue: errno) ?? .EIO) }
        handle = FileHandle(fileDescriptor: fd, closeOnDealloc: true)
    }

    static func fromEnvironment() -> SamplingTrace? {
        guard let path = ProcessInfo.processInfo.environment["SWIFTLET_SAMPLING_TRACE"], !path.isEmpty else { return nil }
        do { return try SamplingTrace(path: path) }
        catch { print("[sampling-trace] unavailable: \(error)"); return nil }
    }

    private func write(_ record: [String: Any]) {
        lock.lock(); defer { lock.unlock() }
        guard !failed else { return }
        do {
            var data = try JSONSerialization.data(withJSONObject: record, options: [.sortedKeys])
            data.append(10)
            try handle.write(contentsOf: data)
        } catch {
            failed = true
            print("[sampling-trace] write failed: \(error)")
        }
    }

    func begin(_ fields: [String: Any]) -> Int {
        lock.lock(); ordinal += 1; let id = ordinal; lock.unlock()
        var record = fields
        record["event"] = "begin"; record["request"] = id; record["schema"] = 1
        write(record)
        return id
    }

    static func score(_ value: Float) -> Any {
        if value.isNaN { return "nan" }
        if value == .infinity { return "+inf" }
        if value == -.infinity { return "-inf" }
        return Double(value)
    }

    static func describe(_ logits: [Float], vocabulary: Int) -> [String: Any] {
        var top: [(Int, Float)] = []
        var nonfinite = 0
        var minimum = Float.infinity, maximum = -Float.infinity
        for id in 0..<min(vocabulary, logits.count) {
            let value = logits[id]
            if value.isFinite { minimum = min(minimum, value); maximum = max(maximum, value) }
            else { nonfinite += 1 }
            if value.isNaN { continue }
            if top.count < 8 || value > top.last!.1 {
                top.append((id, value))
                top.sort { $0.1 == $1.1 ? $0.0 < $1.0 : $0.1 > $1.1 }
                if top.count > 8 { top.removeLast() }
            }
        }
        return ["top": top.map { ["id": $0.0, "score": score($0.1)] as [String: Any] },
                "nonfinite": nonfinite, "finite_min": score(minimum), "finite_max": score(maximum)]
    }

    func decision(request: Int?, generated: Int, raw: [Float], adjusted: [Float],
                  vocabulary: Int, selected: Int, seen: Int, banEOS: Bool, isEOS: Bool) {
        guard let request else { return }
        write(["event": "decision", "request": request, "generated_before": generated,
               "selected": selected, "seen_before": seen, "ban_eos": banEOS, "is_eos": isEOS,
               "selected_raw": Self.score(raw[selected]), "selected_adjusted": Self.score(adjusted[selected]),
               "raw": Self.describe(raw, vocabulary: vocabulary),
               "adjusted": Self.describe(adjusted, vocabulary: vocabulary)])
    }

    func end(request: Int?, generated: [Int], text: String, reason: String, cached: Int) {
        guard let request else { return }
        write(["event": "end", "request": request, "generated_ids": generated,
               "text": text, "finish_reason": reason, "cached_tokens_after": cached])
    }
}
