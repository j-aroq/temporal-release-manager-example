# Temporal Release Management Frontend

React-based dashboard for viewing and monitoring Temporal workflow release states.

## Features

- **Release List View** - Browse all releases with state information
- **Release Detail View** - Drill down into complete entity hierarchy
- **Real-time Updates** - Automatic polling for state changes
- **JWT Authentication** - Secure access to release information
- **Responsive Design** - Built with Chakra UI for all screen sizes
- **TypeScript** - Full type safety throughout the application

## Prerequisites

- **Node.js 18+**
- **npm** (comes with Node.js)
- **Backend API running** at http://localhost:8000/api

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env if your backend is running on a different URL
```

### 3. Start Development Server

```bash
npm start
```

The application will be available at http://localhost:3000

## Development

### Available Scripts

```bash
# Start development server (with hot reload)
npm start

# Build for production
npm build

# Run unit tests
npm test

# Run unit tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui

# Lint TypeScript code
npm run lint

# Fix linting issues
npm run lint:fix

# Format code with Prettier
npm run format

# Check formatting
npm run format:check

# Type checking
npm run type-check
```

### Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── ReleaseList.tsx  # Release list table
│   │   ├── ReleaseDetail.tsx # Release detail page
│   │   ├── EntityHierarchy.tsx # Hierarchical entity display
│   │   ├── Login.tsx        # Login form
│   │   ├── Layout.tsx       # Common layout wrapper
│   │   └── ProtectedRoute.tsx # Route guard
│   ├── pages/               # Page-level components
│   │   ├── Dashboard.tsx    # Main dashboard page
│   │   ├── ReleasePage.tsx  # Release detail page
│   │   └── LoginPage.tsx    # Login page
│   ├── services/            # API client services
│   │   ├── api.ts           # Axios configuration
│   │   ├── authService.ts   # Authentication service
│   │   └── releaseService.ts # Release data fetching
│   ├── hooks/               # Custom React hooks
│   │   ├── useAuth.ts       # Authentication hook
│   │   ├── useReleases.ts   # Release list data
│   │   ├── useReleaseDetail.ts # Release detail data
│   │   └── usePolling.ts    # Real-time polling hook
│   ├── types/               # TypeScript type definitions
│   │   ├── entities.ts      # Release, Wave, Cluster, Bundle, App
│   │   └── auth.ts          # User, Token types
│   ├── App.tsx              # Root application component
│   └── index.tsx            # Application entry point
├── tests/
│   ├── unit/                # Component unit tests
│   └── e2e/                 # Playwright E2E tests
├── package.json             # Dependencies and scripts
├── tsconfig.json            # TypeScript configuration
├── .env.example             # Example environment variables
└── README.md                # This file
```

## Testing

### Unit Tests

```bash
# Run all unit tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode (default)
npm test -- --watch
```

### E2E Tests

```bash
# Run E2E tests
npm run test:e2e

# Run with UI mode (interactive)
npm run test:e2e:ui

# Run in headed mode (see browser)
npm run test:e2e:headed
```

## Authentication

The application requires authentication to access release information.

### Default Credentials (Development)

- **Email**: `admin@example.com`
- **Password**: `admin123`

The application stores the JWT token in `localStorage` and includes it in all API requests.

## Entity Hierarchy

The application displays a 5-level entity hierarchy:

```
Release (N)
  └── Wave (N per release)
        └── Cluster (N per wave)
              └── Bundle (1 per cluster)
                    └── App (N per bundle)
```

### Navigation Flow

1. **Dashboard** - View list of all releases
2. **Click Release** - Navigate to release detail page
3. **View Hierarchy** - See complete entity tree with states
4. **Auto-Update** - States refresh every 3 seconds (configurable)

## Configuration

### Environment Variables

- `REACT_APP_API_URL` - Backend API base URL (required)
- `REACT_APP_ENABLE_POLLING` - Enable real-time polling (default: true)
- `REACT_APP_POLLING_INTERVAL` - Polling interval in ms (default: 3000)
- `REACT_APP_DEBUG` - Enable debug logging (default: false)

### Customization

#### Polling Interval

Edit `.env` to change the polling frequency:

```env
# Update every 5 seconds instead of 3
REACT_APP_POLLING_INTERVAL=5000
```

#### Theme

The application uses Chakra UI's default theme. To customize:

1. Create `src/theme.ts`
2. Extend Chakra's theme
3. Import and apply in `App.tsx`

## Troubleshooting

### Frontend won't start

**Check Node.js version**:
```bash
node --version  # Should be 18+
```

**Clear node_modules and reinstall**:
```bash
rm -rf node_modules package-lock.json
npm install
```

### Login fails

**Verify backend is running**:
```bash
curl http://localhost:8000/health
```

**Check API URL**: Ensure `REACT_APP_API_URL` matches backend URL

**Check credentials**: Default is `admin@example.com` / `admin123`

### API requests fail

**Check CORS**: Backend must allow `http://localhost:3000` in CORS origins

**Check console**: Open browser DevTools → Console for error messages

**Verify token**: Check if token is stored in localStorage

### Real-time updates not working

**Check polling is enabled**:
```env
REACT_APP_ENABLE_POLLING=true
```

**Check polling interval**: Should be set in milliseconds (e.g., `3000` for 3 seconds)

**Check browser console**: Look for polling-related errors

## Building for Production

```bash
# Create production build
npm run build

# Output will be in build/ directory
# Deploy the build/ directory to your web server
```

### Production Checklist

1. **Set production API URL**:
   ```env
   REACT_APP_API_URL=https://api.your-domain.com/api
   ```

2. **Disable debug mode**:
   ```env
   REACT_APP_DEBUG=false
   ```

3. **Build the application**:
   ```bash
   npm run build
   ```

4. **Deploy build/ directory** to your web server (nginx, Apache, S3, etc.)

5. **Configure web server** for Single Page Application (SPA) routing

## Resources

- [React Documentation](https://react.dev/)
- [Chakra UI Documentation](https://chakra-ui.com/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [React Router Documentation](https://reactrouter.com/)
- [Playwright Documentation](https://playwright.dev/)

## Support

For issues or questions:
1. Check browser console for errors
2. Review network requests in DevTools
3. Ensure backend is running and accessible
4. Consult spec and architecture docs in `specs/001-temporal-bff-system/`
5. File an issue if problem persists
