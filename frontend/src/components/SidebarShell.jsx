// Shared responsive shell for the three module sidebars: a static column on
// large screens, an off-canvas drawer (with backdrop) on small ones, since a
// fixed 320px sidebar next to a chat panel can't fit a phone viewport.
export function SidebarShell({ open, onClose, children }) {
  return (
    <>
      {open && (
        <div
          onClick={onClose}
          aria-hidden="true"
          className="fixed inset-0 z-30 bg-black/60 lg:hidden"
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex h-full w-80 max-w-[85vw] shrink-0 flex-col gap-5 overflow-y-auto border-r border-rule bg-ink-raised p-5 transition-transform duration-200 lg:static lg:z-auto lg:max-w-none lg:translate-x-0 lg:bg-ink-raised/60 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {children}
      </aside>
    </>
  );
}
