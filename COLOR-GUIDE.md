# COMPLETE UI COLOR GUIDE - Every Named Part

## 1. LIGHT MODE VARIABLES (Lines 1-50 in style.css)
```
--bg-body: #f9f9f9 → **PAGE BACKGROUND**
--text-primary: #0f2746 → **ALL HEADINGS/TEXT** (h1, h2, p)
--primary: #00274d → **BUTTONS/LINKS/ACCOUNT PORTAL BUTTONS**
--success: #10b981 → **SUCCESS ALERTS/SUCCESS BADGES**
```

## 2. DARK MODE VARIABLES (Lines 50-100)
```
--bg-body: #0b1320 → **DARK PAGE BG**
--text-primary: #e7effb → **ALL HEADINGS/TEXT in DARK** (white-ish)
--primary: #7fb1ff → **DARK MODE BUTTONS/LINKS**
```

## 3. NAVBAR COLORS (Lines 250-400)
```
.navbar → **TOP NAV BAR BG**: gradient rgba(0,39,77,0.9)
.nav-link → **NAV LINKS**: #d7e5ff (light blue)
.logo-title → **LOGO TEXT**: #fff (white)
```

## 4. LOGIN PORTAL BUTTONS (Lines 500-600)
```
.btn-primary → **LOGIN BUTTON**: var(--primary) = #00274d (dark blue)
.btn-primary:hover → **HOVER**: var(--primary-dark) = #001c37
.btn-login → **LOGIN BUTTON SPECIAL**: same as primary
```

## 5. DASHBOARD HEADERS (Lines 1000-1100)
```
.dashboard h1 → **"Welcome back" TITLE**: var(--text-primary)
.portal-hero → **BLUE HEADER BG**: #00274d
.portal-hero h1 → **TITLE IN HEADER**: #fff (white)
```

## 6. DASHBOARD NOTIFICATION BOXES/CARDS (Lines 1200-1400)
```
.dashboard-card → **STATS CARDS BG**: rgba(255,255,255,0.92)
.stat-value → **NUMBERS**: var(--primary) blue
.alert → **ALERTS**: var(--primary) border
.alert-success → **GREEN ALERTS**: var(--success)
```

## 7. SIDEBAR (Lines 1400-1500)
```
.sidebar → **LEFT MENU BG**: rgba(255,255,255,0.92)
.sidebar-link → **MENU LINKS**: var(--text-secondary)
```

## 8. HOW TO CHANGE:

**QUICK CHANGES:**
```
1. Find `--primary: #00274d` → Change hex
2. Ctrl+F5 refresh
3. Test light/dark toggle
```

**FULL RE-THEME:**
Edit lines 1-100 → ALL COLORS controlled here.

**EXAMPLE - Purple Theme:**
```
:root { --primary: #8b5cf6; }
:root[data-theme="dark"] { --primary: #c084fc; }
```

**Run & Test:**
```
python alumni-tracking-system-master/run_app.py
```

