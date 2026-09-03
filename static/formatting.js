/* Small, dependency-free formatter for model output. User messages remain plain text. */
(() => {
  const escapeHtml = (value) => value.replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  })[char]);

  function inlineFormat(value) {
    return value
      .replace(/`([^`\n]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/__([^_]+)__/g, "<strong>$1</strong>")
      .replace(/\*([^*\n]+)\*/g, "<em>$1</em>")
      .replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
  }

  function toHtml(rawText) {
    const codeBlocks = [];
    let text = rawText.replace(/```([\w-]*)\n?([\s\S]*?)```/g, (_, language, code) => {
      const token = `@@CODE_${codeBlocks.length}@@`;
      codeBlocks.push(`<pre><code${language ? ` data-language="${escapeHtml(language)}"` : ""}>${escapeHtml(code.trim())}</code></pre>`);
      return token;
    });

    text = escapeHtml(text);
    const lines = text.split("\n").map((line) => {
      if (/^###\s+/.test(line)) return `<h3>${inlineFormat(line.replace(/^###\s+/, ""))}</h3>`;
      if (/^##\s+/.test(line)) return `<h2>${inlineFormat(line.replace(/^##\s+/, ""))}</h2>`;
      if (/^#\s+/.test(line)) return `<h1>${inlineFormat(line.replace(/^#\s+/, ""))}</h1>`;
      if (/^&gt;\s?/.test(line)) return `<blockquote>${inlineFormat(line.replace(/^&gt;\s?/, ""))}</blockquote>`;
      if (/^[-*]\s+/.test(line)) return `<span class="md-list-item">${inlineFormat(line.replace(/^[-*]\s+/, ""))}</span>`;
      const ordered = line.match(/^(\d+)\.\s+(.*)$/);
      if (ordered) return `<span class="md-list-item numbered" data-number="${ordered[1]}">${inlineFormat(ordered[2])}</span>`;
      return inlineFormat(line);
    });

    return lines.join("\n").replace(/@@CODE_(\d+)@@/g, (_, index) => codeBlocks[Number(index)]);
  }

  function formatAssistantMessage(element) {
    const rawText = element.textContent;
    if (!rawText || element.dataset.formattedText === rawText) return;
    element.dataset.formattedText = rawText;
    element.innerHTML = toHtml(rawText);
  }

  const timers = new WeakMap();
  function queueFormatting(element) {
    clearTimeout(timers.get(element));
    // Wait until streaming pauses so partial Markdown is never reformatted mid-response.
    timers.set(element, setTimeout(() => formatAssistantMessage(element), 700));
  }

  const observer = new MutationObserver((records) => {
    const targets = new Set();
    records.forEach((record) => {
      const node = record.target.nodeType === Node.TEXT_NODE ? record.target.parentElement : record.target;
      const message = node?.closest?.(".message.assistant .message-content");
      if (message) targets.add(message);
      record.addedNodes.forEach((added) => {
        if (added.nodeType !== Node.ELEMENT_NODE) return;
        if (added.matches?.(".message.assistant .message-content")) targets.add(added);
        added.querySelectorAll?.(".message.assistant .message-content").forEach((item) => targets.add(item));
      });
    });
    targets.forEach(queueFormatting);
  });

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".message.assistant .message-content").forEach(formatAssistantMessage);
    observer.observe(document.body, { childList: true, characterData: true, subtree: true });
  });
})();
