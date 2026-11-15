import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Errors must reach the user, not be retried away silently: one retry for flaky networks at most,
// and never for planning (a plan request is slow and its errors are meaningful).
const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1 }, mutations: { retry: false } },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>,
)
