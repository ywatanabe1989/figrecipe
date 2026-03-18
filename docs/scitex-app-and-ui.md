<!-- ---
!-- Timestamp: 2026-03-15 03:50:44
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/figrecipe/docs/scitex-app-and-ui.md
!-- --- -->

  But there's a tension: scitex-app is currently a pure Python package with zero dependencies (stdlib only,
  file-oriented SDK). Adding TypeScript/Django templates would change its nature.
● User answered Claude's questions:
  ⎿  · Where should the shared UI components (TS sidebar, templates) live? → sounds scitex-ui as a standalone module
     makes sense; but could you make a plan for name space and project structure?                                                                                                                                                             ❯ it will enable to achieve what ~/proj/scitex-app/README.md /speak                                                                                                                                                                           ● Read 1 file (ctrl+o to expand)                                                                                                                                                                                                              ● I see the vision now — scitex-app provides a write-once backend SDK (files), and scitex-ui would be the write-once     frontend SDK (UI components). App makers write their UI once, it works standalone, cloud, and self-hosted.                                                                                                                                    Let me enter plan mode to design the namespace and structure properly.                                                                                                                                                                      ● Entered plan mode                                                                                                      Claude is now exploring and designing an implementation approach.                                                                                                                                                                           ❯ this is because we already have ~/proj/scitex-python/src/scitex/ui/                                                                                                                                                                         ● There's already a scitex.ui module in the main scitex package. Let me explore that first.
                                                                                                                       ● Explore(Explore scitex.ui module)                                                                                      ⎿  Done (23 tool uses · 50.0k tokens · 1m 8s)                                                                          (ctrl+o to expand)
                                                                                                                       ❯ I am not sure what they are correct there to be placed......                                                                                                                                                                                  /home/ywatanabe/proj/scitex-python/src/scitex/ui/_backends:                                                            drwxr-xr-x 3 ywatanabe ywatanabe 4.0K Mar  4 16:56 .                                                                   drwxr-xr-x 5 ywatanabe ywatanabe 4.0K Mar  4 16:56 ..                                                                  -rwx--x--x 1 ywatanabe ywatanabe 2.4K Jan 30 08:41 _audio.py                                                           -rwx--x--x 1 ywatanabe ywatanabe 8.3K Jan 30 08:41 _config.py                                                          -rwx--x--x 1 ywatanabe ywatanabe 5.8K Jan 30 08:41 _desktop.py                                                         -rwxr-xr-x 1 ywatanabe ywatanabe 8.3K Feb 18 21:29 _emacs.py                                                           -rwxr-xr-x 1 ywatanabe ywatanabe 2.6K Jan 30 08:41 _email.py                                                           -rwx--x--x 1 ywatanabe ywatanabe 1.8K Jan 30 08:41 __init__.py                                                         -rwx--x--x 1 ywatanabe ywatanabe 3.1K Jan 30 08:41 _matplotlib.py                                                      -rwx--x--x 1 ywatanabe ywatanabe 3.4K Jan 30 08:41 _playwright.py                                                      drwxr-xr-x 2 ywatanabe ywatanabe 4.0K Mar  4 16:57 __pycache__                                                         -rwx--x--x 1 ywatanabe ywatanabe 1.2K Jan 30 08:41 _types.py                                                           -rwxr-xr-x 1 ywatanabe ywatanabe 2.2K Jan 30 08:41 _webhook.py                                                                                                                                                                              ● You're right — scitex.ui currently holds notification backends (audio, emacs, email, etc.), which isn't really "UI"    in the frontend sense. That's a naming/organization issue to address separately.                                                                                                                                                              For the shared frontend components (sidebar, templates, TS), let me think about where they actually belong in the      SciTeX ecosystem:                                                                                                                                                                                                                             - scitex.ui = currently notification backends (misplaced name)                                                         - scitex-app = file SDK (pure Python, zero deps)                                                                       - scitex-cloud = Django web app                                                                                                                                                                                                               The frontend components need a home. Let me ask the right question:                                                                                                                                                                         ● User answered Claude's questions:                                                                                      ⎿  · How should we reorganize? The current scitex.ui has notification backends, not frontend UI. → Rename + reuse         scitex.ui                                                                                                                                                                                                                                ● Good — rename notifications to scitex.notify, repurpose scitex.ui for frontend components. Let me now design the full   plan.                                                                                                                                                                                                                                      ● Plan(Plan scitex.ui architecture)                                                                                      ⎿  Done (60 tool uses · 76.1k tokens · 7m 11s)                                                                         (ctrl+o to expand)                                                                                                                                                                                                                          ❯ do you think scitex-app  should dependent on scitex-ui then to create app even in local?                                                                                                                                                    ❯ likes                                                                                                                                                                                                                                       scitex.app.ui                                                                                                                                                                                                                                 ❯ you can use bulk renamer for scitex.ui to scitex.notify                                                                                                                                                                                     ● Let me address all your messages:                                                                                                                                                                                                             1. scitex-app depending on scitex.ui — Yes, makes sense. App makers need UI components even locally. scitex-app would   have scitex_app.ui as a submodule.                                                                                    2. scitex.app.ui namespace — So the UI components live inside scitex-app package as scitex_app.ui, not in a separate   scitex-ui package. This keeps the app SDK self-contained.                                                              3. Bulk renamer for scitex.ui → scitex.notify — Got it, will use mcp__scitex__dev_bulk_rename for the rename.                                                                                                                                 Let me revise the plan with this updated architecture and write the plan file.                                                                                                                                                              ● User answered Claude's questions:                                                                                      ⎿  · To confirm the architecture: scitex_app.ui holds the shared frontend components (TS, CSS, templates), and
     scitex.ui gets renamed to scitex.notify. The TS component + JSON API stay in scitex-cloud's static/shared/ for
     now, while scitex_app.ui provides Python-side metadata/registration. Is this right? → No, TS should be in              scitex-app
                                                                                                                       ● OK — TS/CSS components should ship inside scitex-app itself, so app makers get everything with pip install
  scitex-app. Let me check how existing Python packages ship frontend assets.                                                                                                                                                                 ● Explore(Explore scitex-app structure for TS)                                                                           ⎿  Done (23 tool uses · 60.6k tokens · 1m 18s)                                                                         (ctrl+o to expand)                                                                                                                                                                                                                          ❯ how about to place scitex-app as externals (git submodule) and symlink to current positions for scitex-cloud?                                                                                                                               ❯ or yes, we can use scitex-app's APIs; which is better?                                                                                                                                                                                      ● Good questions — two approaches:                                                                                                                                                                                                              1. Git submodule + symlink: scitex-app repo lives in externals/scitex-app/, symlinked into Django's app discovery      path. Direct file access, Vite sees the TS files natively.                                                             2. pip install + API: scitex-app stays a pip package. scitex-cloud consumes it via Python imports + Django's           AppDirectoriesFinder for static files.                                                                                                                                                                                                      ● User answered Claude's questions:                                                                                      ⎿  · Which approach for scitex-app integration into scitex-cloud? → pip install (editable)                                                                                                                                                  ● Good — pip editable install, the simplest approach. Now let me write the final plan.                                                                                                                                                        ● Updated plan                                                                                                           ⎿  /plan to preview                                                                                                                                                                                                                         ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── Ready to code?                                                                                                                                                                                                                                Here is Claude's plan:                                                                                                ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌ Plan: Package Docs Sidebar + scitex.ui Reorganization                                                                                                                                                                                         Context                                                                                                                                                                                                                                       The docs app (/apps/docs/) has a "Python Packages" landing page that shows package cards but doesn't fully render      per-package Sphinx documentation. The user wants:                                                                      1. Each package's Sphinx docs accessible as individual sidebar entries                                                 2. The sidebar component to be reusable by app makers — not locked inside scitex-cloud                                 3. scitex.ui (currently notification backends) renamed to scitex.notify
 4. scitex_app.ui to become the home for shared frontend components (TS + CSS)
 5. scitex-cloud consumes scitex-app via pip install -e and Django's AppDirectoriesFinder

 ---
 Scope: 3 Projects

 Project A: scitex-python — Rename scitex.ui → scitex.notify

 Use mcp__scitex__dev_bulk_rename to rename across the codebase.

 Files to move/rename:
 - src/scitex/ui/_backends/ → src/scitex/notify/_backends/
 - src/scitex/ui/_backends.py → src/scitex/notify/_backends.py
 - src/scitex/ui/_mcp/ → src/scitex/notify/_mcp/
 - src/scitex/ui/mcp_server.py → src/scitex/notify/mcp_server.py
 - src/scitex/ui/__init__.py → rewrite as deprecation shim

 Import updates (5 consumers):
 - src/scitex/compat/__init__.py — from scitex.ui → from scitex.notify
 - src/scitex/_mcp_tools/ui.py — update handler imports
 - src/scitex/cli/mcp.py — update module path
 - src/scitex/scholar/auth/providers/_notifications.py — update import
 - src/scitex/scholar/auth/sso/BaseSSOAutomator.py — update import

 New src/scitex/ui/__init__.py — deprecation shim:
 import warnings
 def alert(*a, **kw):
     warnings.warn("scitex.ui.alert moved to scitex.notify.alert", DeprecationWarning, stacklevel=2)
     from scitex.notify import alert as _alert
     return _alert(*a, **kw)

 Add to src/scitex/__init__.py: notify = _LazyModule("notify")

 Project B: scitex-app — Add scitex_app.ui with TS/CSS components

 Structure:
 ~/proj/scitex-app/src/scitex_app/
 ├── ui/
 │   ├── __init__.py              # Python: component registry
 │   ├── _registry.py             # register/get/list components
 │   ├── _components/
 │   │   ├── __init__.py
 │   │   └── _package_docs_sidebar.py  # metadata only
 │   └── static/                  # Frontend assets
 │       └── scitex_app/
 │           ├── ts/
 │           │   └── components/
 │           │       └── package-docs-sidebar/
 │           │           ├── index.ts
 │           │           ├── types.ts
 │           │           ├── _PackageDocsSidebar.ts
 │           │           └── _PackageSidebarRenderer.ts
 │           └── css/
 │               └── package-docs-sidebar.css

 pyproject.toml update:
 [tool.setuptools.package-data]
 scitex_app = ["ui/static/**/*"]

 TS component behavior:
 - Fetches from /apps/docs/api/packages/ JSON API
 - Renders grouped package list (Core / Standalone)
 - Click a package → calls onPackageSelect(pkg) callback
 - Embeddable in any container element
 - Configurable via PackageDocsSidebarConfig

 Project C: scitex-cloud — Wire up docs sidebar

 C1. JSON API (already partially done by background agent)
 - apps/workspace/docs_app/views.py — api_packages() view
 - apps/workspace/docs_app/urls.py — path("api/packages/", ...)
 - Returns { groups: [{ label, key, packages: [...] }] }

 C2. Register per-package sidebar entries
 - views.py — Remove python-packages from DOCS_PAGES
 - views.py — Call register_sphinx_packages(DOCS_PAGES, _PAGES_BY_SLUG) after registry init
 - Import register_sphinx_packages from ._sphinx

 C3. Django integration
 - config/settings/settings_shared.py — Add "scitex_app" to INSTALLED_APPS
 - This makes AppDirectoriesFinder discover scitex_app/ui/static/scitex_app/
 - Vite entry discovery: extend vite.entries.ts to scan pip-installed app static dirs

 C4. Docs app template update
 - Remove docs_python_packages.html (old landing page)
 - The pkg-* sidebar entries use existing docs_sphinx_package.html template
 - docs-workspace.ts — no changes needed (AJAX loading already handles pkg-* slugs)

 C5. Cleanup
 - Remove static/docs_app/css/docs-python-packages.css (unused after landing page removal)
 - Remove static/docs_app/ts/rtd-embed.ts (no longer needed)

 ---
 Verification

 1. scitex.notify: python -c "from scitex.notify import alert; print(alert)" works
 2. scitex.ui deprecation: python -c "from scitex.ui import alert" warns but works
 3. JSON API: curl http://127.0.0.1:8000/apps/docs/api/packages/ returns grouped packages
 4. Sidebar: Visit http://127.0.0.1:8000/apps/docs/ — sidebar shows individual package entries (pkg-scitex,
 pkg-figrecipe, etc.)
 5. Sphinx inline: Click any package → Sphinx docs render inline in content area
 6. Component reuse: The TS component can be instantiated from any Django app template

 Implementation Order

 1. Project A first (scitex.notify rename) — unblocks Project B
 2. Project B (scitex_app.ui) — the shared component
 3. Project C (scitex-cloud wiring) — integration + cleanup
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
 Claude has written up a plan and is ready to execute. Would you like to proceed?

 ❯ 1. Yes, clear context (60% used) and auto-accept edits (shift+tab)
   2. Yes, auto-accept edits
   3. Yes, manually approve edits
   4. Type here to tell Claude what to change

 ctrl-g to edit in Gedit · ~/.claude/plans/indexed-meandering-truffle.md

<!-- EOF -->
