import Foundation
import Testing
import Tokenizers
@testable import SwiftletServer

/// Explicit local diagnostic: loads only the pinned model's tokenizer, never
/// its model weights. Run separately from measured model work.
@Suite struct ReplayTokenizerTests {
    @Test func historicalSpellingSurvivesActualTokenizer() async throws {
        let folder = try #require(ProcessInfo.processInfo.environment["AW45_TOKENIZER_DIR"])
        let tokenizer = try await AutoTokenizer.from(modelFolder: URL(fileURLWithPath: folder))
        let raw1 = "<tool_call><function=bash><command>printf one</command></function></tool_call>"
        let raw2 = "<tool_call>\n<function=bash>\n<parameter=command>printf two</parameter>\n</function>\n</tool_call>"
        let first = try #require(try parseToolReply(raw1, declaredTools: ["bash"],
            acceptedSchemaTags: ["bash": ["command"]]))
        let second = try #require(try parseToolReply(raw2, declaredTools: ["bash"]))
        func assistant(_ reply: ParsedToolReply) -> [String: Any] {
            ["role": "assistant", "content": reply.content as Any? ?? NSNull(),
             "tool_calls": reply.calls.map { call in
                ["id": call.id, "type": "function", "function": [
                    "name": call.name, "arguments": call.arguments]] as [String: Any]
             }]
        }
        func request(_ both: Bool) throws -> ChatRequest {
            var messages: [[String: Any]] = [
                ["role": "user", "content": "Run two shell commands."],
                assistant(first),
                ["role": "tool", "tool_call_id": first.calls[0].id, "content": "one"]
            ]
            if both {
                messages += [assistant(second),
                    ["role": "tool", "tool_call_id": second.calls[0].id, "content": "two"]]
            }
            let body: [String: Any] = ["messages": messages, "tools": [
                ["type": "function", "function": ["name": "bash", "parameters": [
                    "type": "object", "properties": ["command": ["type": "string"]]]]]]]
            return try JSONDecoder().decode(ChatRequest.self,
                from: JSONSerialization.data(withJSONObject: body))
        }
        let short = try request(false)
        let full = try request(true)
        func render(_ request: ChatRequest, _ cache: ToolReplayCache) throws -> [Int] {
            let input = try request.templateInput(replayCache: cache)
            return try tokenizer.applyChatTemplate(messages: input.messages, tools: input.tools,
                additionalContext: ["enable_thinking": false])
        }
        for enabled in [false, true] {
            let cache = ToolReplayCache(historyEnabled: enabled)
            cache.record(reply: first, rawText: first.acceptedRawText ?? raw1)
            let before = try render(short, cache)
            cache.record(reply: second, rawText: second.acceptedRawText ?? raw2)
            let after = try render(short, cache)
            let actualFull = try render(full, cache)
            var exact = try full.templateInput(replayCache: nil)
            exact.messages[1] = ["role": "assistant", "content": first.acceptedRawText ?? raw1]
            exact.messages[3] = ["role": "assistant", "content": second.acceptedRawText ?? raw2]
            let expectedFull = try tokenizer.applyChatTemplate(messages: exact.messages,
                tools: exact.tools, additionalContext: ["enable_thinking": false])
            #expect((before == after) == enabled)
            #expect((actualFull == expectedFull) == enabled)
            let common = zip(before, after).prefix(while: { $0.0 == $0.1 }).count
            print("AW45 tokenizer history=\(enabled) before=\(before.count) after=\(after.count) common=\(common) full=\(actualFull.count) exact=\(actualFull == expectedFull)")
        }
    }
}
