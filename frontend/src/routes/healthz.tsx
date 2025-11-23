// routes/hello.ts
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/healthz')({
  server: {
    handlers: {
      GET: async ({ request }) => {
        return new Response('ok')
      },
    },
  },
})