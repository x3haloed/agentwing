/** Explicitly loaded AW-0021 arm; change only Pi's appended cwd hint. */
module.exports = function relativeCwd(pi) {
  pi.on('before_agent_start', (event, context) => {
    const suffix = `\nCurrent working directory: ${context.cwd.replace(/\\/g, '/')}\n`;
    if (!event.systemPrompt.endsWith(suffix)) return undefined;
    return {
      systemPrompt: event.systemPrompt.slice(0, -suffix.length)
        + '\nCurrent working directory: .\n',
    };
  });
};
