# Personal Diary App

Build a fullstack personal diary app from scratch. Users sign up, log in, and write private journal entries. Each entry has a title, body, and mood. The app must be styled with **TailwindCSS** — no other CSS frameworks, no raw CSS files beyond the Tailwind entry point.

## Stack

- **Frontend**: Next.JS + TailwindCSS (port 3000)
- **Backend**: FastAPI + SQLite (3001)
- **Auth**: Session-based (Flask sessions with a secret key)

## Features

### Authentication

Users have an account with an email address and a password. Passwords must be stored hashed — never in plaintext. The app has three auth routes: sign up, log in, and log out.

- **Sign up** (`/signup`): collect email and password. Return `400` if the email is already registered or if either field is missing. On success, create the account, log the user in, and redirect to `/`.
- **Log in** (`/login`): authenticate against the stored hash. Return `400` if credentials are wrong or missing. On success, start a session and redirect to `/`.
- **Log out** (`POST /api/auth/logout`): clear the session.

The frontend should redirect unauthenticated users to `/login` when they try to access any protected page.

### Diary Entries

Each entry belongs to the logged-in user and has:

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer | auto-incremented primary key |
| `title` | string | required, max 120 chars |
| `body` | string | required |
| `mood` | string | one of: `"happy"`, `"neutral"`, `"sad"` |
| `created_at` | datetime | set on creation, UTC |
| `updated_at` | datetime | updated on edit, UTC |

### Pages

**`/login`** — Log in form. Link to `/signup`.

**`/signup`** — Sign up form. Link to `/login`.

**`/`** (dashboard) — List of the user's diary entries, newest first. Each entry shows its title, mood badge, and creation date. Button to create a new entry. Clicking an entry navigates to its detail page.

**`/entries/new`** — Form to write a new entry.

**`/entries/:id`** — Full entry view. Shows title, body, mood, and timestamps. Edit and delete buttons.

**`/entries/:id/edit`** — Edit form pre-filled with existing values.

## UI Requirements

Use these `data-testid` attributes exactly — the test harness depends on them:

### Auth pages

- `data-testid="email-input"` — email field on both login and signup
- `data-testid="password-input"` — password field on both login and signup
- `data-testid="auth-submit"` — submit button on both login and signup
- `data-testid="auth-error"` — error message element (shown on bad credentials or duplicate email)
- `data-testid="logout-btn"` — logout button (visible when logged in, e.g. in nav)

### Dashboard (`/`)

- `data-testid="entry-list"` — the container holding all entry cards
- `data-testid="entry-card"` — each individual entry card (there will be multiple)
- `data-testid="entry-card-title"` — the title text inside each card
- `data-testid="entry-card-mood"` — the mood badge inside each card (text should be the mood value, e.g. `"happy"`)
- `data-testid="new-entry-btn"` — button to navigate to `/entries/new`
- `data-testid="empty-state"` — shown when the user has no entries yet

### Entry form (new and edit)

- `data-testid="title-input"` — title field
- `data-testid="body-input"` — body textarea
- `data-testid="mood-select"` — mood dropdown (`<select>` with options `"happy"`, `"neutral"`, `"sad"`)
- `data-testid="entry-submit"` — save button
- `data-testid="form-error"` — error message when validation fails

### Entry detail (`/entries/:id`)

- `data-testid="entry-title"` — the entry's title
- `data-testid="entry-body"` — the entry's body text
- `data-testid="entry-mood"` — the mood value
- `data-testid="entry-created-at"` — the creation timestamp
- `data-testid="edit-btn"` — navigate to edit page
- `data-testid="delete-btn"` — delete the entry (should redirect to `/` after)

## Tailwind Requirements

- Install Tailwind via the official Vite plugin (`@tailwindcss/vite`).
- Do not use any other CSS framework (no Bootstrap, no MUI, no Chakra).
- You may have a single `index.css` that contains only `@import "tailwindcss"` — no custom rules beyond that.
- Use Tailwind utility classes for all layout, color, spacing, and typography.
- The mood badge on each entry card must use a distinct background color per mood:
  - `happy` → green background (e.g. `bg-green-100 text-green-800`)
  - `neutral` → yellow background (e.g. `bg-yellow-100 text-yellow-800`)
  - `sad` → blue background (e.g. `bg-blue-100 text-blue-800`)

## Data Isolation

A user must never be able to read, edit, or delete another user's entries. Any attempt to access another user's entry by ID must return `404` (not `403` — do not reveal that the entry exists).
