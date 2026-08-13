import * as React from "react"
import { Briefcase, LayoutDashboard, Settings, Code, FileText } from "lucide-react"
import { cn } from "../../lib/utils"

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-background overflow-hidden selection:bg-primary selection:text-white">
      {/* Sidebar Navigation */}
      <aside className="w-64 border-r border-border/40 bg-white/50 backdrop-blur-xl flex flex-col hidden md:flex">
        <div className="h-20 flex items-center px-8">
          <Briefcase className="w-6 h-6 mr-3 text-primary" />
          <span className="font-bold text-xl tracking-tight-premium text-primary">DealMind AI</span>
        </div>
        
        <nav className="flex-1 overflow-y-auto py-8 px-4 space-y-2">
          <NavItem icon={<LayoutDashboard size={18} />} label="Research Desk" isActive />
          <NavItem icon={<FileText size={18} />} label="Investment Memos" />
          <NavItem icon={<Code size={18} />} label="API Keys" />
        </nav>
        
        <div className="p-4 mb-4">
          <NavItem icon={<Settings size={18} />} label="Settings" />
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        {/* Mobile Header (visible only on small screens) */}
        <header className="h-16 border-b border-border/40 bg-white/50 backdrop-blur-md flex items-center px-4 md:hidden z-10 sticky top-0">
          <Briefcase className="w-5 h-5 mr-3 text-primary" />
          <span className="font-bold tracking-tight-premium text-primary">DealMind AI</span>
        </header>

        {/* Scrollable Content Container */}
        <main className="flex-1 overflow-auto relative">
          <div className="max-w-5xl mx-auto p-6 md:p-10 lg:p-12 pb-24">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

function NavItem({ 
  icon, 
  label, 
  isActive = false 
}: { 
  icon: React.ReactNode; 
  label: string; 
  isActive?: boolean 
}) {
  return (
    <a
      href="#"
      className={cn(
        "flex items-center px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group",
        isActive 
          ? "bg-primary text-primary-foreground shadow-sm" 
          : "text-muted-foreground hover:bg-muted/80 hover:text-primary"
      )}
    >
      <span className={cn("mr-3 transition-colors", isActive ? "text-primary-foreground" : "text-muted-foreground group-hover:text-primary")}>
        {icon}
      </span>
      {label}
    </a>
  )
}
