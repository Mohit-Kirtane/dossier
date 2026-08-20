import { useEffect, useState } from "react";

const prefersReducedMotion = () =>
  typeof window !== "undefined" &&
  window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

/** Reveals `text` over a short, length-scaled duration instead of all at once -
 * a legible "the model is writing this" cue. Skips the animation entirely for
 * prefers-reduced-motion, and never replays for text that hasn't changed. */
export function useTypewriter(text) {
  const [shown, setShown] = useState(text ?? "");

  useEffect(() => {
    if (!text) {
      setShown("");
      return undefined;
    }
    if (prefersReducedMotion()) {
      setShown(text);
      return undefined;
    }

    setShown("");
    const tickMs = 16;
    const totalMs = Math.min(1100, Math.max(280, text.length * 6));
    const totalTicks = Math.max(1, Math.round(totalMs / tickMs));
    const charsPerTick = Math.max(1, Math.ceil(text.length / totalTicks));

    let shownChars = 0;
    const id = setInterval(() => {
      shownChars += charsPerTick;
      setShown(text.slice(0, shownChars));
      if (shownChars >= text.length) clearInterval(id);
    }, tickMs);

    return () => clearInterval(id);
  }, [text]);

  return { shown, done: shown === text };
}
