# Polonium Frontend

Next.js frontend for Polonium - AI-powered collaborative workspace for GitHub repositories.

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI component library
- **Monaco Editor** - Code editor (via @monaco-editor/react)
- **Axios** - HTTP client
- **Zustand** - State management (ready for use)

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Backend API running (see backend README)

### Installation

1. Install dependencies:
```bash
npm install
# or
yarn install
# or
pnpm install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run the development server:
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── repositories/      # Repository pages
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   └── globals.css        # Global styles
├── components/
│   ├── ui/                # shadcn/ui components
│   └── repository/        # Repository-specific components
├── lib/
│   ├── api.ts             # API client and types
│   └── utils.ts           # Utility functions
└── public/                # Static assets
```

## Features

### Implemented

- ✅ Repository listing and connection
- ✅ Repository detail page with tabs
- ✅ AI-generated repository overview
- ✅ File browser with search
- ✅ File explanations (AI-powered)
- ✅ Chat interface with message history
- ✅ Real-time status updates during ingestion

### Components

- **RepositoryOverviewTab**: Displays AI-generated overview, architecture, tech stack, and key files
- **RepositoryFilesTab**: File browser with search and file explanations
- **RepositoryChatTab**: Chat interface for repository discussions
- **FileViewer**: Monaco Editor integration for code viewing (ready for implementation)

## API Integration

The frontend communicates with the backend via REST API. See `lib/api.ts` for:
- Type definitions
- API client functions
- Error handling

## Styling

- Uses Tailwind CSS with custom theme
- shadcn/ui components for consistent UI
- Dark mode support (ready)
- Responsive design

## Development

### Adding New Components

1. UI components: Add to `components/ui/` using shadcn/ui patterns
2. Feature components: Add to `components/` organized by feature
3. Pages: Add to `app/` following Next.js App Router conventions

### Code Style

- TypeScript strict mode
- ESLint with Next.js config
- Prefer functional components with hooks
- Use shadcn/ui components when possible

## Next Steps

- [ ] WebSocket integration for real-time chat
- [ ] Monaco Editor for code viewing
- [ ] GitHub OAuth authentication
- [ ] File content viewing
- [ ] Syntax highlighting improvements
- [ ] Dark mode toggle
- [ ] Loading states and error boundaries
- [ ] Optimistic UI updates

## Build

```bash
npm run build
npm start
```

## Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000)


