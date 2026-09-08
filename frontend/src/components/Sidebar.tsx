import Link from 'next/link';
import { LayoutDashboard, Activity, Settings, User } from "lucide-react";

export default function Sidebar() {
  return (
    <div className="fixed top-0 left-0 h-screen bg-background/90 backdrop-blur-md border-r border-border flex flex-col items-center w-16 hover:w-56 transition-all duration-300 ease-[cubic-bezier(0.2,0.8,0.2,1)] group z-50 overflow-hidden">
      
      {/* Top Section */}
      <div className="flex flex-col w-full mt-6 space-y-2 px-3">
        <NavItem href="/" icon={<LayoutDashboard className="w-5 h-5 flex-shrink-0" />} label="Dashboard" />
        <NavItem href="/signals" icon={<Activity className="w-5 h-5 flex-shrink-0" />} label="Signals" />
      </div>

      {/* Bottom Section */}
      <div className="flex flex-col w-full mt-auto mb-6 space-y-2 px-3">
        <NavItem href="/profile" icon={<User className="w-5 h-5 flex-shrink-0" />} label="Profile" />
        <NavItem href="/settings" icon={<Settings className="w-5 h-5 flex-shrink-0" />} label="Settings" />
      </div>
      
    </div>
  );
}

function NavItem({ href, icon, label }: { href: string; icon: React.ReactNode; label: string }) {
  return (
    <Link 
      href={href}
      className="flex items-center space-x-4 p-2 text-muted-foreground hover:text-foreground hover:bg-accent rounded-lg transition-colors w-full"
    >
      <div className="flex items-center justify-center w-6">{icon}</div>
      <span className="text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300 ease-out whitespace-nowrap">
        {label}
      </span>
    </Link>
  );
}
