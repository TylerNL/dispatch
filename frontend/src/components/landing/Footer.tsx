type LinkList = { heading: string; items: { label: string; href: string }[] };

const cols: LinkList[] = [
  {
    heading: 'Product',
    items: [
      { label: 'How it works', href: '#how-it-works' },
      { label: "What's inside", href: '#whats-inside' },
      { label: 'Ask', href: '#ask' },
      { label: 'Archive', href: '#archive' },
    ],
  },
  {
    heading: 'Sources',
    items: [
      { label: 'Hacker News', href: '#' },
      { label: 'arXiv', href: '#' },
      { label: 'AI Labs', href: '#' },
      { label: 'All sources', href: '#' },
    ],
  },
  {
    heading: 'Company',
    items: [
      { label: 'About', href: '#' },
      { label: 'Changelog', href: '#' },
      { label: 'Privacy', href: '#' },
      { label: 'Contact', href: '#' },
    ],
  },
];

export default function Footer() {
  return (
    <footer className="border-t border-border px-5 md:px-8 pt-16 pb-8">
      <div className="mx-auto max-w-container">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-[1.4fr_1fr_1fr_1fr] gap-10">
          <div>
            <a href="#" className="flex items-center gap-2.5">
              <span className="w-2 h-2 rounded-full bg-accent" />
              <span className="text-[17px] font-medium tracking-[-0.015em]">
                dispatch
              </span>
            </a>
            <p className="mt-4 text-[14px] leading-[1.55] text-text-dim max-w-[280px]">
              The tech news firehose, filtered &amp; answered. One email every morning,
              plus a chat that cites its sources.
            </p>
          </div>
          {cols.map((col) => (
            <div key={col.heading}>
              <h5 className="font-mono text-[11px] uppercase tracking-[0.14em] text-text-mute mb-4">
                {col.heading}
              </h5>
              <ul className="flex flex-col gap-2.5">
                {col.items.map((item) => (
                  <li key={item.label}>
                    <a
                      href={item.href}
                      className="text-[14px] text-text-dim hover:text-text transition-colors duration-150"
                    >
                      {item.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="mt-14 pt-6 border-t border-border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 font-mono text-[11.5px] text-text-mute">
          <span>© 2026 dispatch</span>
          <span>Built for people who ship</span>
        </div>
      </div>
    </footer>
  );
}
