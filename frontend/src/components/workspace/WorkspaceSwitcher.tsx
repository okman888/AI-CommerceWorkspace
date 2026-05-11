import { useWorkspaceStore } from '@/stores/workspaceStore'
import { cn } from '@/lib/utils'
import {
  ChevronDown,
  Plus,
  Grid3X3,
  ShoppingCart,
  Settings,
  Users,
} from 'lucide-react'
import { useState, useRef, useEffect } from 'react'

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  Grid3X3,
  ShoppingCart,
  Settings,
  Users,
}

export function WorkspaceSwitcher() {
  const { workspaces, currentWorkspace, setCurrentWorkspace } = useWorkspaceStore()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const activeWorkspace = currentWorkspace || workspaces[0]
  const IconComponent = iconMap[activeWorkspace.icon] || Grid3X3

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'flex items-center gap-2 px-3 py-2 rounded-lg',
          'hover:bg-accent transition-colors',
          'text-sm font-medium'
        )}
      >
        <IconComponent className="w-4 h-4" />
        <span className="hidden sm:inline">{activeWorkspace.name}</span>
        <ChevronDown className={cn('w-4 h-4 transition-transform', isOpen && 'rotate-180')} />
      </button>

      {isOpen && (
        <div
          className={cn(
            'absolute top-full left-0 mt-1 w-64',
            'bg-background border border-border rounded-lg shadow-lg',
            'py-1 z-50'
          )}
        >
          <div className="px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            工作区
          </div>
          {workspaces.map((workspace) => {
            const Icon = iconMap[workspace.icon] || Grid3X3
            return (
              <button
                key={workspace.id}
                onClick={() => {
                  setCurrentWorkspace(workspace)
                  setIsOpen(false)
                }}
                className={cn(
                  'w-full flex items-center gap-3 px-3 py-2 text-sm',
                  'hover:bg-accent transition-colors',
                  activeWorkspace.id === workspace.id && 'bg-accent'
                )}
              >
                <Icon className="w-4 h-4" />
                <span className="flex-1 text-left">{workspace.name}</span>
              </button>
            )
          })}
          <div className="border-t border-border my-1" />
          <button
            className={cn(
              'w-full flex items-center gap-3 px-3 py-2 text-sm',
              'hover:bg-accent transition-colors',
              'text-muted-foreground'
            )}
          >
            <Plus className="w-4 h-4" />
            <span>新建工作区</span>
          </button>
        </div>
      )}
    </div>
  )
}
