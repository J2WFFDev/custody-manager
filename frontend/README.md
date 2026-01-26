# WilcoSS Custody Manager - Frontend

React-based frontend for the WilcoSS Custody & Equipment Manager, built with Vite, TypeScript, and TailwindCSS.

## 🎯 Overview

A modern, responsive web application for managing firearm kits, equipment custody, and maintenance tracking with QR-based operations and comprehensive audit trails.

## 🏗️ Tech Stack

- **React 18** - UI library
- **TypeScript 5** - Type safety
- **Vite 5** - Build tool and dev server
- **TailwindCSS 3** - Utility-first CSS framework
- **React Router 6** - Client-side routing

## 📋 Prerequisites

- **Node.js** 18+ (recommended: 20.x LTS)
- **npm** 8+ or **yarn** 1.22+

## 🚀 Getting Started

### Installation

1. Clone the repository and navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` and configure the API URL:
```
VITE_API_URL=http://localhost:8000
```

### Development

Start the development server with hot module replacement:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Build

Build for production:
```bash
npm run build
```

The optimized build will be output to the `dist/` directory.

### Preview Production Build

Preview the production build locally:
```bash
npm run preview
```

### Linting

Run ESLint to check code quality:
```bash
npm run lint
```

## 📁 Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # Reusable UI components
│   │   └── Layout.tsx   # Main layout wrapper
│   ├── pages/           # Route-level page components
│   │   ├── Home.tsx     # Landing page
│   │   ├── Login.tsx    # Authentication page
│   │   ├── Kits.tsx     # Kit management page
│   │   └── Audit.tsx    # Audit trail viewer
│   ├── services/        # API client layer (coming soon)
│   ├── hooks/           # Custom React hooks (coming soon)
│   ├── utils/           # Helper functions (coming soon)
│   ├── App.tsx          # Root component with routing
│   ├── main.tsx         # Application entry point
│   └── index.css        # Global styles with Tailwind directives
├── .env.example         # Environment variables template
├── tailwind.config.js   # Tailwind configuration
├── vite.config.ts       # Vite configuration
├── tsconfig.json        # TypeScript configuration
└── package.json         # Dependencies and scripts
```

## 🎨 Features

### Current Features
- ✅ Responsive layout with mobile-first design
- ✅ Client-side routing with React Router
- ✅ TailwindCSS styling system
- ✅ TypeScript for type safety
- ✅ Fast development with Vite HMR

### Coming Soon
- 🔄 OAuth authentication (Google & Microsoft)
- 🔄 QR code scanning interface
- 🔄 Kit management CRUD operations
- 🔄 Custody event tracking
- 🔄 Maintenance scheduling
- 🔄 Audit log viewer with filtering
- 🔄 CSV/JSON export functionality

## 🌐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `http://localhost:8000` |

## 📦 Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server at http://localhost:5173 |
| `npm run build` | Build for production (runs TypeScript check + Vite build) |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint on TypeScript files |

## 🎨 Styling with TailwindCSS

This project uses TailwindCSS for styling. Key features:

- **Utility-first**: Style components with utility classes
- **Responsive**: Mobile-first breakpoints (`sm:`, `md:`, `lg:`, `xl:`)
- **Customizable**: Extend theme in `tailwind.config.js`

Example:
```tsx
<div className="bg-blue-600 text-white p-4 rounded-lg hover:bg-blue-700 transition-colors">
  Button
</div>
```

## 🔗 Related Documentation

- [Main Project README](../README.md)
- [Architecture Guide](../ARCHITECTURE.md)
- [User Stories](../USER_STORIES.md)
- [Contributing Guide](../CONTRIBUTING.md)

## 🐛 Troubleshooting

### Port already in use
If port 5173 is already in use, Vite will automatically try the next available port (5174, etc.).

### Module not found errors
Clear node_modules and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

### TypeScript errors
Ensure TypeScript is properly configured:
```bash
npm run build
```

## 📄 License

This project is private and proprietary.

---

Built with ❤️ for youth shooting sports safety and accountability.
