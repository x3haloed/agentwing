import Testing
@testable import SwiftletServer

/// AW-0045 falsifier for the existing one-entry replay cache. Run only in an
/// isolated checkout, after the fixed AW-0044 model comparison is complete.
@Suite struct ReplayRetentionTests {
    @Test func secondReplyDisplacesFirstRawSpelling() throws {
        let cache = ToolReplayCache()
        let first = ParsedToolReply(content: nil, calls: [
            ParsedToolCall(id: "first", name: "bash", arguments: #"{"command":"printf 'one\\n'"}"#)
        ], normalizedSchemaTags: false)
        let second = ParsedToolReply(content: nil, calls: [
            ParsedToolCall(id: "second", name: "bash", arguments: #"{"command":"printf 'two\\n'"}"#)
        ], normalizedSchemaTags: false)
        let incoming = [OpenAIToolCall(id: "first", type: "function",
            function: OpenAIToolCall.Function(name: "bash", arguments: first.calls[0].arguments))]
        let raw = "<tool_call>\n<function=bash>\n<parameter=command>printf 'one\\n'</parameter>\n</function>\n</tool_call>"
        cache.record(reply: first, rawText: raw)
        #expect(cache.replayText(for: incoming) == raw)
        cache.record(reply: second, rawText: "second raw spelling")
        #expect(cache.replayText(for: incoming) == nil)
    }
}
