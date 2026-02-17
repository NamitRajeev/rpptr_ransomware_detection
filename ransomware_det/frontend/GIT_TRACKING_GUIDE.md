# Git Tracking Guide

## ✅ What WILL be tracked (committed to Git)

### Source Code
- ✅ All `.py` files in `backend/` (main.py, detection_service.py, etc.)
- ✅ All `.tsx`, `.ts`, `.jsx`, `.js` files in `src/`
- ✅ All configuration files (package.json, tsconfig.json, vite.config.ts, etc.)

### Backend Files
- ✅ `backend/main.py`
- ✅ `backend/detection_service.py`
- ✅ `backend/requirements.txt`
- ✅ `backend/README.md`
- ✅ `backend/start_backend.bat`
- ✅ Directory structure markers (`.gitkeep` files)

### Frontend Files
- ✅ `src/Dashboard.tsx`
- ✅ `src/App.tsx`
- ✅ `src/main.tsx`
- ✅ `src/index.css`
- ✅ `package.json`
- ✅ `tailwind.config.js`
- ✅ `vite.config.ts`
- ✅ All TypeScript config files

### Documentation
- ✅ `README.md`
- ✅ `SETUP_GUIDE.md`
- ✅ `QUICKSTART.md`
- ✅ `DEPLOYMENT.md`
- ✅ All `.md` files

### Configuration
- ✅ `.env.example` (template for environment variables)
- ✅ `.gitignore`
- ✅ `start_frontend.bat`

---

## ❌ What will NOT be tracked (ignored by Git)

### Dependencies
- ❌ `node_modules/` - Node.js packages (install with `npm install`)
- ❌ Python virtual environments (`venv/`, `env/`, `.venv`)
- ❌ `__pycache__/` - Python bytecode cache
- ❌ `*.pyc`, `*.pyo` - Compiled Python files

### Build Output
- ❌ `dist/` - Frontend production build
- ❌ `dist-ssr/` - Server-side rendering build
- ❌ `build/` - Python build artifacts

### User Data & Models
- ❌ `backend/response/` - Your detection modules (except .gitkeep)
- ❌ `backend/data/` - Your CSV and processed data files
- ❌ `backend/model/` - Your Random Forest model files
- ❌ `backend/lstm/` - Your LSTM model files

**Why?** These files are user-specific and may be large. Users need to copy them manually as described in SETUP_GUIDE.md

### Environment & Secrets
- ❌ `.env` - Your actual environment variables (may contain secrets)
- ❌ `.env.local` - Local overrides
- ❌ `*.pem`, `*.key` - Security certificates/keys

### Logs & Temporary Files
- ❌ `logs/` - Application logs
- ❌ `*.log` - Log files
- ❌ `*.tmp`, `*.bak` - Temporary/backup files
- ❌ `.cache/` - Cache directories

### Editor/IDE Files
- ❌ `.vscode/*` (except extensions.json)
- ❌ `.idea/` - JetBrains IDE settings
- ❌ `.DS_Store` - macOS metadata
- ❌ `*.swp`, `*~` - Vim/editor temp files

---

## 📋 Before Pushing to Git

1. **Check what will be committed:**
   ```bash
   git status
   ```

2. **Verify sensitive files are ignored:**
   ```bash
   git status --ignored
   ```

3. **Make sure .env is NOT in the list:**
   - If you see `.env` in `git status`, it means it will be committed (BAD!)
   - Run: `git rm --cached .env` to remove it from tracking

4. **Add all files:**
   ```bash
   git add .
   ```

5. **Commit:**
   ```bash
   git commit -m "Initial commit: R.A.P.T.O.R dashboard with FastAPI backend"
   ```

6. **Push:**
   ```bash
   git push origin main
   ```

---

## 🔄 For New Users Cloning the Repo

After cloning, they need to:

1. **Install frontend dependencies:**
   ```bash
   npm install
   ```

2. **Install backend dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Copy their detection files:**
   - `hybrid_decision.py` → `backend/response/`
   - `labeled_features.csv` → `backend/data/processed/`
   - Model files → `backend/model/` and `backend/lstm/`

4. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```

5. **Start the servers** (see QUICKSTART.md)

---

## 📦 What Gets Shared

When you push to Git, other developers will get:
- ✅ All source code
- ✅ All documentation
- ✅ Configuration templates
- ✅ Directory structure (via .gitkeep files)

They will NOT get:
- ❌ Your dependencies (they install themselves)
- ❌ Your data/model files (they copy their own)
- ❌ Your environment variables (they create their own .env)

This keeps the repository clean and secure! 🎯
