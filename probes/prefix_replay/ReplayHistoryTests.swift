import Foundation
import Testing
@testable import SwiftletServer

@Suite struct ReplayHistoryTests {
    func reply(_ id: String, content: String? = nil) -> ParsedToolReply {
        ParsedToolReply(content: content, calls: [
            ParsedToolCall(id: id, name: "bash", arguments: #"{"command":"x"}"#)
        ], normalizedSchemaTags: false)
    }
    func calls(_ id: String, args: String = #"{"command":"x"}"#,
               name: String = "bash", type: String = "function") -> [OpenAIToolCall] {
        [OpenAIToolCall(id: id, type: type, function: .init(name: name, arguments: args))]
    }

    @Test func historicalReplayBindsAllFieldsAndVisibleContent() {
        let cache = ToolReplayCache(historyEnabled: true)
        cache.record(reply: reply("a", content: "explanation"), rawText: "raw a")
        cache.record(reply: reply("b"), rawText: "raw b")
        #expect(cache.replayText(for: calls("a"), content: "explanation") == "raw a")
        #expect(cache.replayText(for: calls("a"), content: "edited") == nil)
        #expect(cache.replayText(for: calls("a")) == nil)
        #expect(cache.replayText(for: calls("a", args: #"{"command":"changed"}"#), content: "explanation") == nil)
        #expect(cache.replayText(for: calls("a", args: "invalid"), content: "explanation") == nil)
        #expect(cache.replayText(for: calls("a", name: "other"), content: "explanation") == nil)
        #expect(cache.replayText(for: calls("a", type: "other"), content: "explanation") == nil)
        #expect(cache.replayText(for: calls("unknown"), content: "explanation") == nil)
        #expect(cache.replayText(for: calls("b"), content: "") == "raw b")
    }

    @Test func countAndByteEvictionsAreBounded() {
        for cache in [ToolReplayCache(historyEnabled: true, maxEntries: 2),
                      ToolReplayCache(historyEnabled: true, maxEntries: 64, maxBytes: 500)] {
            for id in ["a", "b", "c"] { cache.record(reply: reply(id), rawText: "raw " + id) }
            #expect(cache.replayText(for: calls("a")) == nil)
            #expect(cache.replayText(for: calls("b")) == "raw b")
            #expect(cache.replayText(for: calls("c")) == "raw c")
            #expect(cache.historyUsage.entries == 2)
            #expect(cache.historyUsage.chargedBytes <= 500)
        }
    }

    @Test func replacementAndOversizedEntryCannotLeaveStaleBinding() {
        let cache = ToolReplayCache(historyEnabled: true, maxBytes: 500)
        cache.record(reply: reply("a"), rawText: "first")
        cache.record(reply: reply("a"), rawText: "replacement")
        #expect(cache.historyUsage.entries == 1)
        #expect(cache.replayText(for: calls("a")) == "replacement")
        cache.record(reply: reply("a"), rawText: String(repeating: "🦋", count: 300))
        #expect(cache.replayText(for: calls("a")) == nil)
        #expect(cache.historyUsage.entries == 0 && cache.historyUsage.chargedBytes == 0)
        cache.record(reply: reply("b"), rawText: "recovered")
        #expect(cache.replayText(for: calls("b")) == "recovered")
    }

    @Test func orderedMultipleCallsAndCanonicalArguments() {
        let cache = ToolReplayCache(historyEnabled: true)
        let combined = ParsedToolReply(content: nil, calls: [
            ParsedToolCall(id: "a", name: "bash", arguments: #"{"b":2,"a":1}"#),
            ParsedToolCall(id: "b", name: "bash", arguments: #"{"command":"x"}"#)
        ], normalizedSchemaTags: false)
        cache.record(reply: combined, rawText: "both")
        let incoming = calls("a", args: #"{"a":1,"b":2}"#) + calls("b")
        #expect(cache.replayText(for: incoming) == "both")
        #expect(cache.replayText(for: Array(incoming.reversed())) == nil)
        #expect(cache.replayText(for: calls("b")) == nil)
    }

    @Test func zeroCapacityFallsBackWithoutRejectingCalls() {
        let cache = ToolReplayCache(historyEnabled: true, maxEntries: 0)
        cache.record(reply: reply("a"), rawText: "valid")
        #expect(cache.replayText(for: calls("a")) == nil)
        #expect(cache.historyUsage.entries == 0)
    }

    @Test func actualTemplateConversionRetainsOlderSpellingAndHonorsEdits() throws {
        let cache = ToolReplayCache(historyEnabled: true)
        let raw = "<tool_call>\n<function=bash>\n<parameter=command>x</parameter>\n</function>\n</tool_call>"
        cache.record(reply: reply("a"), rawText: raw)
        cache.record(reply: reply("b"), rawText: "second raw spelling")
        func request(content: Any) throws -> ChatRequest {
            let call: [String: Any] = ["id": "a", "type": "function", "function": [
                "name": "bash", "arguments": #"{"command":"x"}"#]]
            let body: [String: Any] = ["messages": [
                ["role": "user", "content": "run it"],
                ["role": "assistant", "content": content, "tool_calls": [call]],
                ["role": "tool", "tool_call_id": "a", "content": "ok"]
            ], "tools": [["type": "function", "function": ["name": "bash", "parameters": [
                "type": "object", "properties": ["command": ["type": "string"]]]]]]]
            return try JSONDecoder().decode(ChatRequest.self, from: JSONSerialization.data(withJSONObject: body))
        }
        let intact = try request(content: NSNull()).templateInput(replayCache: cache)
        #expect(intact.messages[1]["content"] as? String == raw)
        #expect(intact.messages[1]["tool_calls"] == nil)
        let edited = try request(content: "edited content").templateInput(replayCache: cache)
        #expect(edited.messages[1]["content"] as? String == "edited content")
        #expect(edited.messages[1]["tool_calls"] != nil)
    }
}
