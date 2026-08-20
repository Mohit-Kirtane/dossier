import { useEffect, useState } from "react";

/** Cycles through the real pipeline step labels for the workflow that's
 * currently running, instead of a generic "Loading..." spinner - pass the
 * actual LangGraph node sequence for the workflow so this stays honest. */
export function ReasoningTrace({ steps }) {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    setIndex(0);
    const id = setInterval(() => {
      setIndex((i) => (i + 1) % steps.length);
    }, 850);
    return () => clearInterval(id);
  }, [steps]);

  return (
    <span className="inline-flex items-center gap-2">
      <span className="relative flex h-1.5 w-1.5 shrink-0">
        <span className="absolute inline-flex h-full w-full rounded-full bg-ochre-deep opacity-75 motion-safe:animate-ping" />
        <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-ochre-deep" />
      </span>
      <span className="font-mono text-[11px] tracking-wide">{steps[index]}</span>
    </span>
  );
}
