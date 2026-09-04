/** Explicit AW-0023 arm. The real harness fixture remains required. */
module.exports = function boundedBashResult(pi) {
  pi.on('tool_result', (event) => {
    if (event.toolName !== 'bash' || event.content.length !== 1
        || event.content[0].type !== 'text') return undefined;
    const originalText = event.content[0].text;
    const chars = Array.from(originalText);
    const limit = 1024;
    if (chars.length <= limit) return undefined;
    const marker = `\n[Agentwing: output truncated from ${chars.length} characters; showing head and tail. Use a targeted command for omitted content.]\n`;
    const available = limit - Array.from(marker).length;
    const head = Math.ceil(available * 0.6);
    const tail = available - head;
    const text = chars.slice(0, head).join('') + marker + chars.slice(-tail).join('');
    return {
      content: [{ type: 'text', text }],
      isError: event.isError,
      details: {
        ...(event.details || {}),
        agentwingBoundedResult: { limit, originalCharacters: chars.length, originalText },
      },
    };
  });
};
