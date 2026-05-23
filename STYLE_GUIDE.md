# 🗺️ Maps of Power: Styling & Development Guide

This guide establishes the styling rules, user interface specifications, and core development principles for the **Maps of Power** project. All new pages, widgets, backend logic, and stylesheets must strictly adhere to these rules.

---

## 🚀 Core Architectural Principles

### 1. 💋 The KISS Principle (Keep It Simple, Stupid)
- **Simplicity First**: Avoid over-engineered architectures. Write code that is straightforward to read, test, and maintain.
- **Clear Routing**: Keep controller routes in `views.py` focused. Complex data parsing should live inside models or helper functions in `util.py`.
- **Minimal Dependencies**: Do not add external packages unless absolutely necessary. Rely on existing, well-tested Python and Node packages.
- **Readable Templates**: Keep Jinja templates legible. Use simple loops and conditionals. Avoid embedding heavy logical expressions inside templates.

### 2. ☔ The DRY Principle (Don't Repeat Yourself)
- **Reusable Layouts**: All standard web pages must inherit from `layout.html` and reuse the centralized `navbar.html` and standard footers.
- **Jinja Macros**: Standard components (like complex datatables, entity links, or lists) should use Jinja macros (e.g. `macros.html`) rather than duplicating markup blocks.
- **Common Helpers**: Shares utility calculations (like dates formatting, geometry extraction, and relation parsing) inside `mop/util.py` rather than redefining them per view.
- **CSS Variable Reuse**: Never hardcode colors or spacing in component stylesheets. Always reuse the CSS variables defined in `color.css` and `style.css`.

---

## 📐 Code Formatting & Line Limits

- **Python**: Maximum line length of **79 characters** (compliant with PEP 8 standards). Keep import blocks sorted and helper functions short.
- **JavaScript**: Maximum line length of **120 characters**.
- **CSS / SCSS**: Maximum line length of **120 characters**.
- **HTML / Jinja Templates**: Maximum line length of **120 characters** to maintain template readability and prevent excessive wrapping.
- **Bracket Placement**: Closing brackets, braces, and parentheses (e.g., `]})`) must **always reside on the same line as the last statement/value** inside lists, dictionaries, function arguments, or multi-line calls.

---

## 🎨 Aesthetic & Styling Guidelines

### 1. Color Palette & Dark Theme
The design is defined by a sleek, modern palette configured in [color.css](file:///var/www/maps-of-power/mop/static/css/color.css):
- **Primary Color**: Slate Blue `#246d8b` (`--bs-primary`) representing authority and depth.
- **Secondary Color**: Olive Green `#a0c223` (`--bs-secondary`) representing territory and nature.
- **Backgrounds**: Slate Gray / Dark Blue `#384356` (`--bs-dark`) for premium dark backgrounds. Light Gray `#eaedf1` (`--bs-white`) for light content cards.

### 2. Premium Visual Polish
- **Glassmorphism**: When displaying high-importance content cards or overlay panels (like error pages or entity details), use a translucent background with frosted glass styling:
  ```css
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  ```
- **Micro-Animations**: Add subtle transitions (`transition: all 0.2s ease-in-out;`) to buttons, interactive items, and links to make the page feel alive and premium.

---

## 🛡️ Error & Safety Guidelines
- **Route Protection**: Always validate request variables (such as checking if IDs exist in datasets) and gracefully raise `404` errors using Flask `abort(404)` to prevent uncaught system exceptions.
- **API Error Formatting**: Any endpoint under `/api/` must return clean, standard JSON (`{"error": "...", "code": ...}`) rather than HTML markup when failing.
