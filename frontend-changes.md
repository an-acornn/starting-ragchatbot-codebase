# Frontend Changes: Dark/Light Theme Toggle

## Files Modified

### `frontend/index.html`
- Added a theme toggle button (`#themeToggle`) with sun and moon SVG icons, positioned fixed in the top-right corner
- Includes `aria-label` and `title` attributes for accessibility
- Bumped CSS and JS cache-busting versions

### `frontend/style.css`
- Added `[data-theme="light"]` CSS variables block with light-appropriate colors (light backgrounds, dark text, adjusted surfaces and borders)
- Added `--code-bg` variable to both themes so code blocks adapt properly
- Added `.theme-toggle` styles: fixed positioning, circular button, hover/focus states
- Added icon transition animations (sun/moon crossfade with rotation and scale)
- Added global `transition` rule on `body *` for smooth color changes when toggling

### `frontend/script.js`
- Added `initTheme()` — reads saved theme from `localStorage` and applies it on load (called before DOM ready to prevent flash)
- Added `toggleTheme()` — switches `data-theme` attribute on `<body>` between `"light"` and `"dark"`, persists to `localStorage`
- Wired toggle button click listener in `setupEventListeners()`

## How It Works

1. Theme is controlled via `data-theme` attribute on `<body>`
2. CSS variables change based on `[data-theme="light"]` selector; dark is the default (no attribute or `data-theme="dark"`)
3. `localStorage` persists the user's choice across sessions
4. `initTheme()` runs before DOMContentLoaded to apply the saved theme immediately
5. All color transitions are animated at 0.3s for a smooth switch
