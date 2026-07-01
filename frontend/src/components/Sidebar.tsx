type SidebarProps = {
  currentPage: "home" | "guide";
  onNavigate: (sectionId: string) => void;
  onOpenGuide: () => void;
};

export function Sidebar({
  currentPage,
  onNavigate,
  onOpenGuide,
}: SidebarProps) {
  const links = [
    { href: "#inicio", label: "Início", sectionId: "inicio" },
    {
      href: "#preprocessamento",
      label: "Pré-processamento",
      sectionId: "preprocessamento",
    },
    {
      href: "#bases-pre-processadas",
      label: "Bases Pré-Processadas",
      sectionId: "bases-pre-processadas",
    },
    {
      href: "#pre-visualizacao",
      label: "Pré-visualização",
      sectionId: "pre-visualizacao",
    },
    {
      href: "#mineracao",
      label: "Mineração de Dados",
      sectionId: "mineracao",
    },
    {
      href: "#resultados",
      label: "Resultados",
      sectionId: "resultados",
    },
  ];

  return (
    <aside className="sidebar" aria-label="Menu lateral">
      <div className="sidebar-brand">
        <span className="sidebar-eyebrow">Plataforma</span>
        <strong>Mineração Educacional</strong>
      </div>

      <nav className="sidebar-nav" aria-label="Navegação principal">
        {links.map((link) => (
          <a
            key={link.href}
            href={link.href}
            onClick={(event) => {
              event.preventDefault();
              onNavigate(link.sectionId);
            }}
          >
            {link.label}
          </a>
        ))}

        <a
          href="#manual"
          className={currentPage === "guide" ? "active" : undefined}
          onClick={(event) => {
            event.preventDefault();
            onOpenGuide();
          }}
        >
          Guia de Usuário
        </a>
      </nav>

      
    </aside>
  );
}