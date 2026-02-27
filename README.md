# DataWeb - Modern SaaS Web App

A modern, dark-themed SaaS web application built with Next.js, TailwindCSS, and ShadCN UI components.

## Features

- 🎨 Modern dark theme with premium design
- 🔐 Beautiful authentication pages (Login/Signup)
- 📓 Notebook-style main app interface
- 📱 Fully responsive design
- ⚡ Built with Next.js 14 App Router
- 🎯 Clean, minimal, and professional UI

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Styling:** TailwindCSS
- **Components:** ShadCN UI
- **Icons:** Lucide React
- **Language:** TypeScript

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Pages

- `/login` - Login page with split-screen layout
- `/signup` - Signup page with same aesthetic
- `/app` - Main application interface with notebook UI

## Project Structure

```
dataweb/
├── app/
│   ├── login/          # Login page
│   ├── signup/         # Signup page
│   ├── app/            # Main app interface
│   ├── layout.tsx      # Root layout
│   ├── page.tsx        # Home (redirects to login)
│   └── globals.css     # Global styles
├── components/
│   └── ui/             # Reusable UI components
│       ├── button.tsx
│       └── input.tsx
└── lib/
    └── utils.ts        # Utility functions
```

## Design System

- **Primary Color:** Green (#10b981)
- **Background:** Neutral-950
- **Panels:** Neutral-900
- **Borders:** Neutral-800
- **Border Radius:** Rounded-xl/2xl
- **Font:** Inter

## License

MIT
