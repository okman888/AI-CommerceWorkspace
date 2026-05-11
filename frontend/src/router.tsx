import { createBrowserRouter, Navigate } from 'react-router'
import { TopNav } from '@/components/hub/TopNav'
import { DashboardPage } from '@/pages/DashboardPage'
import { WorkspacePage } from '@/pages/WorkspacePage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <TopNav />,
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: <DashboardPage />,
      },
      {
        path: 'workspace',
        element: <WorkspacePage />,
      },
    ],
  },
])
