export function Logo({ className }) {
  return (
    <svg
      viewBox="0 0 28 28"
      className={className}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <path
        d="M4 3.5C4 2.67 4.67 2 5.5 2H17l6 6v16.5c0 .83-.67 1.5-1.5 1.5h-16C4.67 26 4 25.33 4 24.5V3.5Z"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinejoin="round"
      />
      <path d="M17 2v5.5c0 .28.22.5.5.5H23" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
      <path d="M8 15h9M8 18.5h9" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
      <circle cx="9.5" cy="10.5" r="2" fill="var(--color-ochre)" />
    </svg>
  );
}
