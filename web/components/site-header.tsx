import Link from "next/link";

const navigation = [
  { href: "/", label: "Overview" },
  { href: "/evidence", label: "Evidence" },
  { href: "/institutions", label: "Institutions" },
  { href: "/burkina-faso", label: "Burkina Faso" },
  { href: "/map", label: "Map" },
  { href: "/finance", label: "Finance" },
];

export function SiteHeader() {
  return (
    <header className="site-header">
      <div className="header-inner">
        <Link className="brand" href="/" aria-label="Africa Energy Dignity Studio home">
          <span className="brand-mark">AED</span>
          <span>
            <strong>Africa Energy Dignity</strong>
            <small>Evidence, Geography and Finance Studio</small>
          </span>
        </Link>
        <nav aria-label="Primary navigation">
          <ul className="nav-list">
            {navigation.map((item) => (
              <li key={item.href}>
                <Link href={item.href}>{item.label}</Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </header>
  );
}
