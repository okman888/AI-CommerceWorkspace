import { create } from 'zustand'

export interface Workspace {
  id: string
  name: string
  icon: string
  description: string
}

interface WorkspaceState {
  workspaces: Workspace[]
  currentWorkspace: Workspace | null
  setCurrentWorkspace: (workspace: Workspace) => void
  addWorkspace: (workspace: Workspace) => void
  removeWorkspace: (id: string) => void
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  workspaces: [
    {
      id: 'default',
      name: '默认工作区',
      icon: 'Grid3X3',
      description: '默认工作区',
    },
  ],
  currentWorkspace: null,
  setCurrentWorkspace: (workspace) => set({ currentWorkspace: workspace }),
  addWorkspace: (workspace) =>
    set((state) => ({
      workspaces: [...state.workspaces, workspace],
    })),
  removeWorkspace: (id) =>
    set((state) => ({
      workspaces: state.workspaces.filter((w) => w.id !== id),
    })),
}))
