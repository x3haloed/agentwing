import Foundation
import Testing
import Tokenizers

@Suite struct FeedbackPromptTests {
    @Test func prepareFeedbackTokensWithoutModel() async throws {
        let env = ProcessInfo.processInfo.environment
        let modelDir = URL(fileURLWithPath: try #require(env["AW55_QPACK_DIR"]))
        let captureURL = URL(fileURLWithPath: try #require(env["AW55_CAPTURE"]))
        let feedbackURL = URL(fileURLWithPath: try #require(env["AW55_FEEDBACK"]))
        let output = URL(fileURLWithPath: try #require(env["AW55_PREPARED"]))
        let capture = try #require(JSONSerialization.jsonObject(with: Data(contentsOf: captureURL)) as? [String: Any])
        var begin = try #require(capture["begin"] as? [String: Any])
        let end = try #require(capture["end"] as? [String: Any])
        let original = try #require(begin["actual_prompt_ids"] as? [Int])
        let generated = try #require(end["generated_ids"] as? [Int])
        try #require(generated.count == 512)
        let feedback = try String(contentsOf: feedbackURL, encoding: .utf8).trimmingCharacters(in: .whitespacesAndNewlines)
        let tokenizer = try await AutoTokenizer.from(modelFolder: modelDir)
        let turn = try tokenizer.applyChatTemplate(messages: [["role": "user", "content": feedback]],
            additionalContext: ["enable_thinking": false])
        let spelling = "<|im_start|>user\n" + feedback + "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
        try #require(turn == tokenizer.encode(text: spelling))
        let suffix = tokenizer.encode(text: "<|im_end|>\n") + turn
        try #require(suffix == tokenizer.encode(text: "<|im_end|>\n" + spelling))
        let prefix = original + generated
        let prepared = prefix + suffix
        try #require(Array(prepared.prefix(prefix.count)) == prefix)
        begin["actual_prompt_ids"] = prepared
        begin["rendered_prompt_ids"] = prepared
        begin["new_prompt_tokens"] = prepared.count
        begin["reused_prompt_tokens"] = 0
        begin["matched_prompt_tokens"] = 0
        begin["admitted_max_new"] = 512
        begin["frequency_penalty"] = 0
        begin["diagnostic_feedback_ids"] = suffix
        begin["diagnostic_source_prefix_tokens"] = prefix.count
        begin["diagnostic_feedback_text"] = feedback
        try JSONSerialization.data(withJSONObject: begin, options: [.sortedKeys, .prettyPrinted])
            .write(to: output, options: [.withoutOverwriting])
        print("AW55 tokenizer-only prepared=\(prepared.count) prefix=\(prefix.count) suffix=\(suffix.count)")
    }
}
