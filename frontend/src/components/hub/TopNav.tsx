import { WorkspaceSwitcher } from '@/components/workspace/WorkspaceSwitcher'
import { useUIStore } from '@/stores/uiStore'
import { Menu, Bell, Search } from 'lucide-react'
import { cn } from '@/lib/utils'

export function TopNav() {
  const { toggleSidebar } = useUIStore()

  return (
    <header
      className={cn(
        'h-14 border-b border-border',
        'flex items-center justify-between px-4',
        'bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60'
      )}
    >
      <div className="flex items-center gap-4">
        <button
          onClick={toggleSidebar}
          className={cn(
            'p-2 rounded-lg hover:bg-accent',
            'transition-colors lg:hidden'
          )}
        >
          <Menu className="w-5 h-5" />
        </button>
        <WorkspaceSwitcher />
      </div>

      <div className="flex items-center gap-2">
        <button
          className={cn(
            'p-2 rounded-lg hover:bg-accent',
            'transition-colors hidden sm:flex'
          )}
        >
          <Search className="w-5 h-5" />
        </button>
        <button
          className={cn(
            'p-2 rounded-lg hover:bg-accent',
            'transition-colors relative'
          )}
        >
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-primary rounded-full" />
        </button>
      </div>
    </header>
  )
}
