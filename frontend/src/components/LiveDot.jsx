export function LiveDot({ className = "" }) {
  return (
    <span className={`relative flex h-1.5 w-1.5 ${className}`}>
      <span className="absolute inline-flex h-full w-full rounded-full bg-ochre-deep opacity-75 motion-safe:animate-ping" />
      <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-ochre-deep" />
    </span>
  );
}
