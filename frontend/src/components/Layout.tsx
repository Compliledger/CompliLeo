import { NavLink, Outlet } from 'react-router-dom';

const navItems = [
  { to: '/', label: 'Overview', end: true },
  { to: '/demo', label: 'Run Demo' },
  { to: '/results', label: 'Proof Bundle' },
];

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-ink-700/80 bg-ink-900/60 backdrop-blur">
        <div className="mx-auto max-w-6xl px-6 py-4 flex items-center justify-between">
          <NavLink to="/" className="flex items-center gap-2">
            <span className="inline-block h-2.5 w-2.5 rounded-full bg-accent-strong shadow-[0_0_12px_rgba(56,189,248,0.8)]" />
            <span className="font-semibold tracking-tight">
              Compli<span className="text-accent">Leo</span>
            </span>
            <span className="ml-2 text-xs uppercase tracking-widest text-slate-500">
              MVP
            </span>
          </NavLink>
          <nav className="flex items-center gap-1 text-sm">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  [
                    'px-3 py-1.5 rounded-md transition',
                    isActive
                      ? 'bg-ink-700 text-white'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-ink-800',
                  ].join(' ')
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="flex-1">
        <div className="mx-auto max-w-6xl px-6 py-10">
          <Outlet />
        </div>
      </main>

      <footer className="border-t border-ink-700/80 bg-ink-900/40">
        <div className="mx-auto max-w-6xl px-6 py-4 text-xs text-slate-500 flex justify-between">
          <span>CompliLeo MVP &middot; ZK proof orchestration on Aleo</span>
          <span className="font-mono">no wallet integration</span>
        </div>
      </footer>
    </div>
  );
}
