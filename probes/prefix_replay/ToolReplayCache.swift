/// AW-0045 draft: retain exact accepted spellings for bounded tool history.
/// This replaces only ToolReplayCache in an isolated, explicitly prepared tree.
final class ToolReplayCache: @unchecked Sendable {
    private let lock = NSLock()
    private let debug: Bool
    private let historyEnabled: Bool
    private let maxEntries: Int
    private let maxBytes: Int
    // Original off-mode storage and matching behavior remain intact.
    private var signatures: [ToolCallSignature] = []
    private var rawText: String?
    private struct Entry {
        let signatures: [ToolCallSignature]
        let visibleContent: String
        let rawText: String
        let charge: Int
    }
    private var entries: [Entry] = []
    private var chargedBytes = 0

    init(debug: Bool = false,
         historyEnabled: Bool = ProcessInfo.processInfo.environment["SWIFTLET_TOOL_REPLAY_HISTORY"] == "1",
         maxEntries: Int = 64, maxBytes: Int = 1_048_576) {
        precondition(maxEntries >= 0 && maxBytes >= 0)
        self.debug = debug
        self.historyEnabled = historyEnabled
        self.maxEntries = maxEntries
        self.maxBytes = maxBytes
    }

    // Logical payload plus explicit metadata charges, not a claim about RSS.
    var historyUsage: (entries: Int, chargedBytes: Int) {
        lock.lock(); defer { lock.unlock() }
        return (entries.count, chargedBytes)
    }

    func record(reply: ParsedToolReply, rawText: String) {
        let next = reply.calls.map {
            ToolCallSignature(id: $0.id, type: "function", name: $0.name,
                arguments: canonicalArguments($0.arguments) ?? $0.arguments)
        }
        let visible = reply.content ?? ""
        lock.lock(); defer { lock.unlock() }
        guard historyEnabled else {
            signatures = next
            self.rawText = rawText
            return
        }
        // Replace a repeated binding even if the new spelling is too large;
        // an oversized replacement must not leave its old spelling eligible.
        if let index = entries.firstIndex(where: {
            $0.signatures == next && $0.visibleContent == visible
        }) {
            chargedBytes -= entries.remove(at: index).charge
        }
        let charge = next.reduce(rawText.utf8.count + visible.utf8.count + 64) {
            $0 + $1.id.utf8.count + $1.type.utf8.count + $1.name.utf8.count
                + $1.arguments.utf8.count + 128
        }
        guard maxEntries > 0 && charge <= maxBytes else { return }
        while entries.count >= maxEntries || chargedBytes > maxBytes - charge {
            chargedBytes -= entries.removeFirst().charge
        }
        entries.append(Entry(signatures: next, visibleContent: visible,
                             rawText: rawText, charge: charge))
        chargedBytes += charge
    }

    func replayText(for calls: [OpenAIToolCall], content: String? = nil) -> String? {
        let incoming: [ToolCallSignature] = calls.compactMap { call in
            guard let arguments = canonicalArguments(call.function.arguments) else { return nil }
            return ToolCallSignature(id: call.id, type: call.type,
                                     name: call.function.name, arguments: arguments)
        }
        guard incoming.count == calls.count else { return nil }
        lock.lock(); defer { lock.unlock() }
        if historyEnabled {
            guard let entry = entries.reversed().first(where: {
                $0.signatures == incoming && $0.visibleContent == (content ?? "")
            }) else { return nil }
            if debug {
                FileHandle.standardError.write(Data(
                    "[tool-replay] history-hit calls=\(incoming.count) entries=\(entries.count) charged=\(chargedBytes)\n".utf8))
            }
            return entry.rawText
        }
        // Preserve original diagnostic text in off mode.
        guard incoming == signatures else {
            if debug {
                let sameCount = incoming.count == signatures.count
                let ids = sameCount && zip(incoming, signatures).allSatisfy { $0.0.id == $0.1.id }
                let types = sameCount && zip(incoming, signatures).allSatisfy { $0.0.type == $0.1.type }
                let names = sameCount && zip(incoming, signatures).allSatisfy { $0.0.name == $0.1.name }
                let arguments = sameCount && zip(incoming, signatures).allSatisfy { $0.0.arguments == $0.1.arguments }
                FileHandle.standardError.write(Data(
                    "[tool-replay] miss count=\(sameCount) ids=\(ids) types=\(types) names=\(names) arguments=\(arguments)\n".utf8))
            }
            return nil
        }
        if debug {
            FileHandle.standardError.write(Data("[tool-replay] hit calls=\(incoming.count)\n".utf8))
        }
        return rawText
    }
}
