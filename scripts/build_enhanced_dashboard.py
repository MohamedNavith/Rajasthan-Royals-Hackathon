import re

with open('temp_figma_extract/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Head to support theme initialization script
theme_init_script = """  <script>
    // Theme initialization (check localStorage or system preference)
    (function() {
      const savedTheme = localStorage.getItem('rr_theme');
      if (savedTheme === 'light') {
        document.documentElement.classList.remove('dark');
      } else if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark');
      } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
        document.documentElement.classList.remove('dark');
      } else {
        document.documentElement.classList.add('dark'); // Default to dark command-center
      }
    })();
  </script>
  <!-- CDN Fallbacks for global icons & fonts -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" crossorigin="anonymous">
"""

# Replace in head
html = html.replace('  <!-- Local typography and icon assets', theme_init_script + '\n  <!-- Local typography and icon assets')

# 2. Refine Styles to support both Light and Dark mode seamlessly
css_to_replace = """    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background-color: #F4F7FB;
      color: #0F172A;
    }
    h1, h2, h3, h4, .font-heading {
      font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .rr-gradient-text {
      background: linear-gradient(135deg, #0B1B3D 0%, #E01B6B 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .rr-glass-card {
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03), 0 10px 30px rgba(15, 23, 42, 0.035);
      transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
    }
    .rr-glass-card:hover {
      border-color: rgba(224, 27, 107, 0.35);
      transform: translateY(-1px);
      box-shadow: 0 14px 36px rgba(15, 23, 42, 0.07);
    }
    .active-tab {
      background: #0B1B3D;
      color: #ffffff !important;
      box-shadow: none;
    }
    .text-white,
    .text-slate-100,
    .text-slate-200,
    .text-slate-300 {
      color: #0F172A !important;
    }
    .text-slate-400 { color: #64748B !important; }
    .text-slate-500 { color: #94A3B8 !important; }
    .bg-rr-pink.text-white,
    .bg-rr-navy.text-white,
    .active-tab,
    a.bg-gradient-to-r {
      color: #FFFFFF !important;
    }
    header {
      background: rgba(255, 255, 255, 0.96) !important;
      box-shadow: 0 1px 0 #E2E8F0, 0 8px 28px rgba(15, 23, 42, 0.04);
    }
    header nav {
      scrollbar-width: thin;
      scrollbar-color: #CBD5E1 transparent;
    }
    table tbody tr:hover { background: #F8FAFC; }
    table thead { background: #F8FAFC !important; }
    input[type="range"] { accent-color: #E01B6B !important; }
    .metric-kicker {
      font-size: 0.68rem;
      font-weight: 800;
      letter-spacing: 0.11em;
      text-transform: uppercase;
      color: #64748B;
    }
    .crest-mark {
      width: 48px;
      height: 52px;
      flex: 0 0 auto;
      filter: drop-shadow(0 5px 10px rgba(11, 27, 61, 0.15));
    }
    .player-card-img {
      mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 80%, rgba(0,0,0,0) 100%);
      -webkit-mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 80%, rgba(0,0,0,0) 100%);
    }"""

enhanced_css = """    /* Universal Transitions */
    body, .rr-glass-card, header, footer, nav, table, tr, td, th {
      transition: background-color 0.25s ease, border-color 0.25s ease, color 0.25s ease, box-shadow 0.25s ease;
    }

    h1, h2, h3, h4, .font-heading {
      font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .rr-gradient-text {
      background: linear-gradient(135deg, #0B1B3D 0%, #E01B6B 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    html.dark .rr-gradient-text {
      background: linear-gradient(135deg, #FFFFFF 0%, #E01B6B 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    /* LIGHT THEME (Default) */
    html:not(.dark) body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background-color: #F4F7FB;
      color: #0F172A;
    }
    html:not(.dark) .rr-glass-card {
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03), 0 10px 30px rgba(15, 23, 42, 0.035);
    }
    html:not(.dark) .rr-glass-card:hover {
      border-color: rgba(224, 27, 107, 0.35);
      transform: translateY(-1px);
      box-shadow: 0 14px 36px rgba(15, 23, 42, 0.07);
    }
    html:not(.dark) header {
      background: rgba(255, 255, 255, 0.96) !important;
      box-shadow: 0 1px 0 #E2E8F0, 0 8px 28px rgba(15, 23, 42, 0.04);
    }
    html:not(.dark) .active-tab {
      background: #0B1B3D !important;
      color: #FFFFFF !important;
      box-shadow: none;
    }
    html:not(.dark) .tab-button:not(.active-tab) {
      color: #64748B !important;
    }
    html:not(.dark) .tab-button:not(.active-tab):hover {
      color: #0B1B3D !important;
      background: #EDF2F7;
    }
    html:not(.dark) .text-white,
    html:not(.dark) .text-slate-100,
    html:not(.dark) .text-slate-200,
    html:not(.dark) .text-slate-300 {
      color: #0F172A !important;
    }
    html:not(.dark) .text-slate-400 { color: #64748B !important; }
    html:not(.dark) .text-slate-500 { color: #94A3B8 !important; }
    html:not(.dark) .bg-rr-pink.text-white,
    html:not(.dark) .bg-rr-navy.text-white,
    html:not(.dark) .active-tab,
    html:not(.dark) a.bg-gradient-to-r,
    html:not(.dark) .keep-white {
      color: #FFFFFF !important;
    }
    html:not(.dark) table tbody tr:hover { background: #F8FAFC; }
    html:not(.dark) table thead { background: #F8FAFC !important; }
    html:not(.dark) footer { background: #FFFFFF !important; border-color: #E2E8F0 !important; }

    /* DARK THEME */
    html.dark body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background-color: #0B1120;
      color: #F8FAFC;
    }
    html.dark .rr-glass-card {
      background: #111B2E;
      border: 1px solid #1E293B;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
    }
    html.dark .rr-glass-card:hover {
      border-color: rgba(224, 27, 107, 0.45);
      transform: translateY(-1px);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    html.dark header {
      background: rgba(11, 17, 32, 0.96) !important;
      box-shadow: 0 1px 0 #1E293B, 0 8px 28px rgba(0, 0, 0, 0.5);
    }
    html.dark .active-tab {
      background: #E01B6B !important;
      color: #FFFFFF !important;
      box-shadow: 0 0 15px rgba(224, 27, 107, 0.35);
    }
    html.dark .tab-button:not(.active-tab) {
      color: #94A3B8 !important;
    }
    html.dark .tab-button:not(.active-tab):hover {
      color: #F8FAFC !important;
      background: #1E293B;
    }
    html.dark .text-white { color: #FFFFFF !important; }
    html.dark .text-slate-100 { color: #F1F5F9 !important; }
    html.dark .text-slate-200 { color: #E2E8F0 !important; }
    html.dark .text-slate-300 { color: #CBD5E1 !important; }
    html.dark .text-slate-400 { color: #94A3B8 !important; }
    html.dark .text-slate-500 { color: #94A3B8 !important; }
    html.dark .text-slate-600 { color: #CBD5E1 !important; }
    html.dark .text-rr-navy { color: #F8FAFC !important; }
    html.dark .text-rr-gold { color: #FBBF24 !important; }
    html:not(.dark) .text-rr-gold { color: #B45309 !important; }
    html.dark table tbody tr:hover { background: #172338; }
    html.dark table thead { background: #0E1626 !important; }
    html.dark footer { background: #080D1A !important; border-color: #1E293B !important; }
    html.dark .border-rr-border { border-color: #1E293B !important; }

    header nav {
      scrollbar-width: thin;
      scrollbar-color: #CBD5E1 transparent;
    }
    input[type="range"] { accent-color: #E01B6B !important; }
    .metric-kicker {
      font-size: 0.68rem;
      font-weight: 800;
      letter-spacing: 0.11em;
      text-transform: uppercase;
      color: #64748B;
    }
    html.dark .metric-kicker { color: #94A3B8; }
    .crest-mark {
      width: 48px;
      height: 52px;
      flex: 0 0 auto;
      filter: drop-shadow(0 5px 10px rgba(11, 27, 61, 0.15));
    }
    .player-card-img {
      mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 80%, rgba(0,0,0,0) 100%);
      -webkit-mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 80%, rgba(0,0,0,0) 100%);
    }"""

html = html.replace(css_to_replace, enhanced_css)

# 3. Add Theme Toggle Button and Connect button to Header Action Buttons
header_action_needle = """        <!-- Action Buttons -->
        <div class="flex items-center space-x-3">"""

header_action_replacement = """        <!-- Action Buttons -->
        <div class="flex items-center space-x-2.5">
          <!-- Dark / Light Mode Toggle -->
          <button id="themeToggleBtn" onclick="toggleTheme()" class="inline-flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-bold border border-rr-border hover:border-rr-pink transition shadow-sm bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200" title="Toggle Light / Dark Mode">
            <span id="themeIcon"><i class="fa-solid fa-moon text-indigo-500"></i></span>
            <span id="themeText" class="hidden sm:inline">Theme</span>
          </button>

          <!-- Connect Quick Anchor -->
          <a href="#connect-analyst-section" class="inline-flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-bold border border-rr-border hover:border-rr-pink transition shadow-sm bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200" title="Connect with Mohamed Navith H">
            <i class="fa-solid fa-id-card text-rr-pink"></i>
            <span class="hidden sm:inline">Connect</span>
          </a>"""

html = html.replace(header_action_needle, header_action_replacement)

# 4. Enhance Author Identity in Header with inline quick-connect pills
author_header_needle = """            <div class="flex items-center space-x-2">
              <span class="text-xs font-black uppercase tracking-widest text-rr-pink">SupeRR Selector Season 2</span>
              <span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-rr-pink/10 text-rr-pink border border-rr-pink/20">Authored by Mohamed Navith H</span>
            </div>"""

author_header_replacement = """            <div class="flex flex-wrap items-center gap-2">
              <span class="text-xs font-black uppercase tracking-widest text-rr-pink">SupeRR Selector Season 2</span>
              <span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-rr-pink/10 text-rr-pink border border-rr-pink/20">Authored by Mohamed Navith H</span>
              <div class="hidden md:flex items-center space-x-2 text-xs">
                <a href="https://www.linkedin.com/in/mohamed-navith-bb20892bb/" target="_blank" rel="noopener noreferrer" class="text-slate-400 hover:text-blue-500 transition" title="LinkedIn Profile">
                  <i class="fa-brands fa-linkedin text-sm"></i>
                </a>
                <span class="text-slate-300 dark:text-slate-600 text-[10px]">•</span>
                <button onclick="copyDiscord('navith_stark')" class="text-slate-400 hover:text-indigo-400 transition" title="Discord: navith_stark (Click to copy)">
                  <i class="fa-brands fa-discord text-sm"></i>
                </button>
                <span class="text-slate-300 dark:text-slate-600 text-[10px]">•</span>
                <a href="mailto:mohamednavithh@gmail.com" class="text-slate-400 hover:text-rr-pink transition" title="Email: mohamednavithh@gmail.com">
                  <i class="fa-solid fa-envelope text-sm"></i>
                </a>
              </div>
            </div>"""

html = html.replace(author_header_needle, author_header_replacement)

# 5. Add Dedicated "Connect with Me" Section before the Footer
connect_section = """    <!-- Dedicated "Connect with Me" Analyst Dossier Section -->
    <section id="connect-analyst-section" class="scroll-mt-24">
      <div class="rr-glass-card rounded-2xl p-6 sm:p-8 border border-rr-border">
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div class="flex items-center space-x-4">
            <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-rr-pink via-rr-darkpink to-rr-navy flex items-center justify-center text-white text-2xl shadow-lg shadow-rr-pink/25">
              <i class="fa-solid fa-user-astronaut keep-white"></i>
            </div>
            <div>
              <div class="flex items-center space-x-2.5">
                <h3 class="text-xl font-extrabold font-heading text-white">Mohamed Navith H</h3>
                <span class="px-2.5 py-0.5 text-[10px] font-bold rounded-full bg-rr-pink/10 text-rr-pink border border-rr-pink/30">Lead Analyst</span>
              </div>
              <p class="text-xs text-slate-400 mt-1">SupeRR Selector Season 2 • Rajasthan Royals IPL 2027 Auction Strategy Dossier</p>
            </div>
          </div>

          <!-- Interactive Connect Badges -->
          <div class="flex flex-wrap items-center gap-3 w-full lg:w-auto">
            <!-- LinkedIn -->
            <a href="https://www.linkedin.com/in/mohamed-navith-bb20892bb/" target="_blank" rel="noopener noreferrer" 
               class="flex-1 sm:flex-none inline-flex items-center justify-center space-x-2 px-4 py-2.5 rounded-xl border border-rr-border hover:border-blue-500 bg-white dark:bg-slate-800/90 hover:bg-blue-500/10 transition text-xs font-bold text-white group shadow-sm">
              <i class="fa-brands fa-linkedin text-blue-500 text-base group-hover:scale-110 transition-transform"></i>
              <span>LinkedIn</span>
              <i class="fa-solid fa-arrow-up-right-from-square text-[10px] text-slate-400 group-hover:text-blue-500"></i>
            </a>

            <!-- Discord -->
            <button onclick="copyDiscord('navith_stark')" 
                    class="flex-1 sm:flex-none inline-flex items-center justify-center space-x-2 px-4 py-2.5 rounded-xl border border-rr-border hover:border-indigo-400 bg-white dark:bg-slate-800/90 hover:bg-indigo-500/10 transition text-xs font-bold text-white group shadow-sm"
                    title="Click to copy Discord handle">
              <i class="fa-brands fa-discord text-indigo-400 text-base group-hover:scale-110 transition-transform"></i>
              <span>Discord: <span class="font-mono text-rr-pink">navith_stark</span></span>
              <i class="fa-regular fa-copy text-[10px] text-slate-400 group-hover:text-indigo-400" id="discordCopyIcon"></i>
            </button>

            <!-- Email -->
            <a href="mailto:mohamednavithh@gmail.com" 
               class="flex-1 sm:flex-none inline-flex items-center justify-center space-x-2 px-4 py-2.5 rounded-xl border border-rr-border hover:border-rr-pink bg-white dark:bg-slate-800/90 hover:bg-rr-pink/10 transition text-xs font-bold text-white group shadow-sm">
              <i class="fa-solid fa-envelope text-rr-pink text-base group-hover:scale-110 transition-transform"></i>
              <span>mohamednavithh@gmail.com</span>
              <i class="fa-solid fa-paper-plane text-[10px] text-slate-400 group-hover:text-rr-pink"></i>
            </a>
          </div>
        </div>
      </div>
    </section>

"""

footer_needle = """  <!-- Footer -->
  <footer class="border-t border-rr-border"""

html = html.replace(footer_needle, connect_section + '  <!-- Footer -->\n  <footer class="border-t border-rr-border')

# 6. Add JavaScript functions for Theme Toggle and Copy Discord + Toast
js_to_add = """
    // Theme Switcher & Persistence
    function updateThemeUI(isDark) {
      const themeIcon = document.getElementById('themeIcon');
      const themeText = document.getElementById('themeText');
      if (isDark) {
        if (themeIcon) themeIcon.innerHTML = '<i class="fa-solid fa-sun text-amber-400"></i>';
        if (themeText) themeText.innerText = 'Light';
      } else {
        if (themeIcon) themeIcon.innerHTML = '<i class="fa-solid fa-moon text-indigo-500"></i>';
        if (themeText) themeText.innerText = 'Dark';
      }
      if (typeof middleChart !== 'undefined' && middleChart) {
        initCharts();
      }
    }

    function toggleTheme() {
      const isDark = document.documentElement.classList.toggle('dark');
      localStorage.setItem('rr_theme', isDark ? 'dark' : 'light');
      updateThemeUI(isDark);
    }

    // Copy Discord to Clipboard
    function copyDiscord(handle) {
      navigator.clipboard.writeText(handle).then(() => {
        const icon = document.getElementById('discordCopyIcon');
        if (icon) {
          icon.className = 'fa-solid fa-check text-emerald-400';
          setTimeout(() => { icon.className = 'fa-regular fa-copy text-[10px] text-slate-400 group-hover:text-indigo-400'; }, 2000);
        }
        showToast(`Discord handle "${handle}" copied to clipboard!`);
      }).catch(err => {
        prompt('Copy Discord username:', handle);
      });
    }

    function showToast(msg) {
      let toast = document.getElementById('rr-toast');
      if (!toast) {
        toast = document.createElement('div');
        toast.id = 'rr-toast';
        toast.className = 'fixed bottom-6 right-6 z-50 px-4 py-3 rounded-xl bg-slate-900 text-white border border-rr-pink shadow-2xl text-xs font-bold flex items-center space-x-2 transition-opacity duration-300 pointer-events-none opacity-0';
        document.body.appendChild(toast);
      }
      toast.innerHTML = `<i class="fa-solid fa-circle-check text-rr-pink"></i><span>${msg}</span>`;
      toast.style.opacity = '1';
      setTimeout(() => { toast.style.opacity = '0'; }, 3000);
    }

    // Initial theme UI setup
    window.addEventListener('DOMContentLoaded', () => {
      const isDark = document.documentElement.classList.contains('dark');
      updateThemeUI(isDark);
    });
"""

# 7. Update initCharts to be theme-aware
init_charts_old = """    function initCharts() {
      if (middleChart) middleChart.destroy();
      if (deathChart) deathChart.destroy();"""

init_charts_new = """    function initCharts() {
      if (middleChart) middleChart.destroy();
      if (deathChart) deathChart.destroy();
      const isDark = document.documentElement.classList.contains('dark');
      const textColor = isDark ? '#94A3B8' : '#64748B';
      const gridColor = isDark ? '#1E293B' : '#E2E8F0';
      const legendColor = isDark ? '#F8FAFC' : '#1E293B';"""

html = html.replace(init_charts_old, init_charts_new)
html = html.replace("legend: { labels: { color: '#475569', font: { size: 10 } } }", "legend: { labels: { color: legendColor, font: { size: 11, weight: 'bold' } } }")
html = html.replace("x: { ticks: { color: '#64748B', font: { size: 10 } }, grid: { display: false } },\n              y: { ticks: { color: '#64748B', font: { size: 10 } }, grid: { color: '#E2E8F0' } }", "x: { ticks: { color: textColor, font: { size: 10 } }, grid: { display: false } },\n              y: { ticks: { color: textColor, font: { size: 10 } }, grid: { color: gridColor } }")

# Insert js into script tag right before document.addEventListener('DOMContentLoaded'
onload_needle = "    // On Load\n    document.addEventListener('DOMContentLoaded', () => {"
onload_replacement = js_to_add + "\n    // On Load\n    document.addEventListener('DOMContentLoaded', () => {\n      const isDark = document.documentElement.classList.contains('dark');\n      updateThemeUI(isDark);"

html = html.replace(onload_needle, onload_replacement)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html enhanced and written successfully!")
