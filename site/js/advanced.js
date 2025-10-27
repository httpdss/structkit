// StructKit Advanced Interactive Components - Phase 2

class StructSite {
  constructor() {
    this.initializeSearchFunctionality();
    this.initializeAdvancedStats();
    this.initializeContributorsList();
    this.initializeProjectShowcase();
    this.initializeAdvancedDemoFeatures();
    this.initializeKeyboardShortcuts();
    this.initializeThemeToggle();
    this.initializeProgressiveEnhancement();
  }

  // Advanced Search Functionality
  initializeSearchFunctionality() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    if (!searchInput) return;

    let searchIndex = [];

    // Build search index from page content
    this.buildSearchIndex();

    searchInput.addEventListener(
      'input',
      this.debounce((e) => {
        const query = e.target.value.toLowerCase().trim();

        if (query.length < 2) {
          searchResults.classList.add('hidden');
          return;
        }

        const results = this.performSearch(query);
        this.displaySearchResults(results);
      }, 300)
    );

    // Close search when clicking outside
    document.addEventListener('click', (e) => {
      if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
        searchResults.classList.add('hidden');
      }
    });
  }

  buildSearchIndex() {
    this.searchIndex = [
      {
        title: 'YAML Configuration',
        content: 'Define project structures in simple YAML files',
        section: 'features',
        keywords: ['yaml', 'config', 'configuration', 'structure'],
      },
      {
        title: 'Template Variables',
        content:
          'Dynamic content with Jinja2 templating and interactive prompts',
        section: 'features',
        keywords: ['template', 'variables', 'jinja2', 'dynamic'],
      },
      {
        title: 'Remote Content',
        content: 'Fetch files from GitHub, HTTP/HTTPS, S3, and cloud storage',
        section: 'features',
        keywords: ['remote', 'github', 'http', 's3', 'cloud', 'fetch'],
      },
      {
        title: 'Installation Guide',
        content: 'pip install, Docker, and source installation methods',
        section: 'installation',
        keywords: ['install', 'pip', 'docker', 'setup'],
      },
      {
        title: 'Basic Usage Demo',
        content: 'See how to generate project structures with StructKit',
        section: 'demos',
        keywords: ['demo', 'usage', 'example', 'generate'],
      },
    ];
  }

  performSearch(query) {
    return this.searchIndex.filter(item => {
      return item.title.toLowerCase().includes(query) ||
             item.content.toLowerCase().includes(query) ||
             item.keywords.some(keyword => keyword.includes(query));
    }).slice(0, 5);
  }

  displaySearchResults(results) {
    const searchResults = document.getElementById('search-results');

    if (results.length === 0) {
      searchResults.innerHTML = '<div class="search-no-results">No results found</div>';
    } else {
      searchResults.innerHTML = results.map(result => `
        <div class="search-result-item" onclick="this.scrollToSection('${result.section}')">
          <h4 class="search-result-title">${result.title}</h4>
          <p class="search-result-content">${result.content}</p>
        </div>
      `).join('');
    }

    searchResults.classList.remove('hidden');
  }

  scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
      section.scrollIntoView({ behavior: 'smooth' });
      document.getElementById('search-results').classList.add('hidden');
      document.getElementById('search-input').value = '';
    }
  }

  // Enhanced GitHub Stats with Additional Metrics
  async initializeAdvancedStats() {
    const statsContainer = document.querySelector('.github-stats-advanced');
    if (!statsContainer) return;

    try {
      // Show enhanced loading state
      statsContainer.innerHTML = this.getLoadingStatsHTML();

      // Fetch comprehensive GitHub data
      const [repoData, contributorsData, releasesData] = await Promise.all([
        fetch('https://api.github.com/repos/httpdss/struct').then(r => r.json()),
        fetch('https://api.github.com/repos/httpdss/structkit/contributors').then(r => r.json()),
        fetch('https://api.github.com/repos/httpdss/structkit/releases/latest').then(r => r.json())
      ]);

      // Update with comprehensive stats
      statsContainer.innerHTML = this.getAdvancedStatsHTML(repoData, contributorsData, releasesData);

      // Animate counters
      this.animateCounters();

    } catch (error) {
      console.error('Failed to fetch advanced GitHub stats:', error);
      statsContainer.innerHTML = this.getFallbackStatsHTML();
    }
  }

  getLoadingStatsHTML() {
    return `
      <div class="stats-grid">
        ${Array(6).fill().map(() => `
          <div class="stat-card loading">
            <div class="stat-icon skeleton"></div>
            <div class="stat-value skeleton">...</div>
            <div class="stat-label skeleton">Loading</div>
          </div>
        `).join('')}
      </div>
    `;
  }

  getAdvancedStatsHTML(repo, contributors, release) {
    return `
      <div class="stats-grid">
        <div class="stat-card" data-count="${repo.stargazers_count}">
          <div class="stat-icon">⭐</div>
          <div class="stat-value">${this.formatNumber(repo.stargazers_count)}</div>
          <div class="stat-label">Stars</div>
        </div>
        <div class="stat-card" data-count="${repo.forks_count}">
          <div class="stat-icon">🔀</div>
          <div class="stat-value">${this.formatNumber(repo.forks_count)}</div>
          <div class="stat-label">Forks</div>
        </div>
        <div class="stat-card" data-count="${contributors.length}">
          <div class="stat-icon">👥</div>
          <div class="stat-value">${contributors.length}</div>
          <div class="stat-label">Contributors</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🚀</div>
          <div class="stat-value">${release.tag_name || 'v1.0'}</div>
          <div class="stat-label">Latest Release</div>
        </div>
        <div class="stat-card" data-count="${repo.open_issues_count}">
          <div class="stat-icon">🐛</div>
          <div class="stat-value">${repo.open_issues_count}</div>
          <div class="stat-label">Open Issues</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📦</div>
          <div class="stat-value">${this.formatBytes(repo.size * 1024)}</div>
          <div class="stat-label">Repository Size</div>
        </div>
      </div>
    `;
  }

  // Contributors Showcase
  async initializeContributorsList() {
    const contributorsContainer = document.querySelector('.contributors-showcase');
    if (!contributorsContainer) return;

    try {
      const contributors = await fetch('https://api.github.com/repos/httpdss/structkit/contributors')
        .then(r => r.json());

      contributorsContainer.innerHTML = `
        <h3 class="contributors-title">Contributors</h3>
        <div class="contributors-grid">
          ${contributors.slice(0, 12).map(contributor => `
            <div class="contributor-card">
              <img src="${contributor.avatar_url}" alt="${contributor.login}" class="contributor-avatar">
              <div class="contributor-info">
                <h4 class="contributor-name">${contributor.login}</h4>
                <p class="contributor-contributions">${contributor.contributions} commits</p>
              </div>
              <a href="${contributor.html_url}" target="_blank" class="contributor-link">
                <i class="fab fa-github"></i>
              </a>
            </div>
          `).join('')}
        </div>
        <a href="https://github.com/httpdss/structkit/graphs/contributors" target="_blank" class="btn btn-ghost">
          View All Contributors →
        </a>
      `;
    } catch (error) {
      console.error('Failed to fetch contributors:', error);
    }
  }

  // Project Showcase
  initializeProjectShowcase() {
    const showcaseContainer = document.querySelector('.project-showcase');
    if (!showcaseContainer) return;

    const projects = [
      {
        name: 'Terraform Modules',
        description: 'Generate consistent Terraform module structures',
        tags: ['terraform', 'infrastructure', 'iac'],
        icon: '🏗️'
      },
      {
        name: 'Python Projects',
        description: 'Bootstrap Python applications with best practices',
        tags: ['python', 'fastapi', 'django'],
        icon: '🐍'
      },
      {
        name: 'Next.js Apps',
        description: 'Generate modern React applications',
        tags: ['react', 'nextjs', 'typescript'],
        icon: '⚛️'
      },
      {
        name: 'Microservices',
        description: 'Create microservice architectures',
        tags: ['docker', 'kubernetes', 'api'],
        icon: '🔧'
      }
    ];

    showcaseContainer.innerHTML = `
      <h3 class="showcase-title">Built with StructKit</h3>
      <div class="showcase-grid">
        ${projects.map(project => `
          <div class="showcase-card">
            <div class="showcase-icon">${project.icon}</div>
            <h4 class="showcase-name">${project.name}</h4>
            <p class="showcase-description">${project.description}</p>
            <div class="showcase-tags">
              ${project.tags.map(tag => `<span class="showcase-tag">${tag}</span>`).join('')}
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  // Advanced Demo Features
  initializeAdvancedDemoFeatures() {
    const demoContainer = document.querySelector('.demo-carousel');
    if (!demoContainer) return;

    // Add fullscreen functionality
    const demoVideos = demoContainer.querySelectorAll('.demo-video');
    demoVideos.forEach(video => {
      video.addEventListener('click', () => {
        this.openFullscreenDemo(video);
      });
    });

    // Add demo navigation with keyboard support
    document.addEventListener('keydown', (e) => {
      if (e.target.closest('.demo-carousel')) {
        if (e.key === 'ArrowLeft') this.previousDemo();
        if (e.key === 'ArrowRight') this.nextDemo();
        if (e.key === 'Escape') this.closeFullscreenDemo();
      }
    });
  }

  openFullscreenDemo(video) {
    const modal = document.createElement('div');
    modal.className = 'demo-modal';
    modal.innerHTML = `
      <div class="demo-modal-content">
        <button class="demo-modal-close">&times;</button>
        <img src="${video.src}" alt="${video.alt}" class="demo-modal-video">
        <div class="demo-modal-info">
          <h3>${video.alt}</h3>
          <p>Press ESC to close or click outside the demo</p>
        </div>
      </div>
    `;

    document.body.appendChild(modal);
    modal.addEventListener('click', (e) => {
      if (e.target === modal || e.target.classList.contains('demo-modal-close')) {
        this.closeFullscreenDemo();
      }
    });

    setTimeout(() => modal.classList.add('active'), 10);
  }

  closeFullscreenDemo() {
    const modal = document.querySelector('.demo-modal');
    if (modal) {
      modal.classList.remove('active');
      setTimeout(() => modal.remove(), 300);
    }
  }

  // Keyboard Shortcuts
  initializeKeyboardShortcuts() {
    const shortcuts = {
      'ctrl+k': () => document.getElementById('search-input')?.focus(),
      'ctrl+/': () => this.showShortcutsHelp(),
      'esc': () => {
        document.getElementById('search-results')?.classList.add('hidden');
        this.closeFullscreenDemo();
      }
    };

    document.addEventListener('keydown', (e) => {
      const key = `${e.ctrlKey ? 'ctrl+' : ''}${e.key.toLowerCase()}`;
      if (shortcuts[key]) {
        e.preventDefault();
        shortcuts[key]();
      }
    });
  }

  showShortcutsHelp() {
    const modal = document.createElement('div');
    modal.className = 'shortcuts-modal';
    modal.innerHTML = `
      <div class="shortcuts-content">
        <h3>Keyboard Shortcuts</h3>
        <div class="shortcuts-list">
          <div class="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>K</kbd>
            <span>Search</span>
          </div>
          <div class="shortcut-item">
            <kbd>←</kbd> / <kbd>→</kbd>
            <span>Navigate demos</span>
          </div>
          <div class="shortcut-item">
            <kbd>Esc</kbd>
            <span>Close modals</span>
          </div>
          <div class="shortcut-item">
            <kbd>Ctrl</kbd> + <kbd>/</kbd>
            <span>Show this help</span>
          </div>
        </div>
        <button class="btn btn-ghost" onclick="this.closest('.shortcuts-modal').remove()">
          Close
        </button>
      </div>
    `;

    document.body.appendChild(modal);
    setTimeout(() => modal.classList.add('active'), 10);
  }

  // Theme Toggle (Future Enhancement)
  initializeThemeToggle() {
    const themeToggle = document.querySelector('.theme-toggle');
    if (!themeToggle) return;

    themeToggle.addEventListener('click', () => {
      document.body.classList.toggle('light-theme');
      const isLight = document.body.classList.contains('light-theme');
      localStorage.setItem('theme', isLight ? 'light' : 'dark');
    });

    // Load saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
      document.body.classList.add('light-theme');
    }
  }

  // Progressive Enhancement
  initializeProgressiveEnhancement() {
    // Add 'js-enabled' class for CSS progressive enhancement
    document.documentElement.classList.add('js-enabled');

    // Initialize service worker if supported
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/structkit/sw.js').catch((err) => {
        console.log('ServiceWorker registration failed:', err);
      });
    }

    // Initialize intersection observer for animations
    this.initializeScrollAnimations();
  }

  initializeScrollAnimations() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in');

          // Stagger animations for grid items
          if (entry.target.classList.contains('stagger-parent')) {
            const children = entry.target.querySelectorAll('.stagger-item');
            children.forEach((child, index) => {
              setTimeout(() => {
                child.classList.add('animate-in');
              }, index * 100);
            });
          }
        }
      });
    }, observerOptions);

    // Observe all animatable elements
    document.querySelectorAll('.animate-on-scroll, .stagger-parent').forEach(el => {
      observer.observe(el);
    });
  }

  // Utility Methods
  formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  }

  formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  animateCounters() {
    const statCards = document.querySelectorAll('.stat-card[data-count]');
    statCards.forEach(card => {
      const target = parseInt(card.dataset.count);
      const valueElement = card.querySelector('.stat-value');
      let current = 0;
      const increment = target / 30;
      const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
          current = target;
          clearInterval(timer);
        }
        valueElement.textContent = this.formatNumber(Math.floor(current));
      }, 50);
    });
  }
}

// Initialize advanced features when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new StructSite();
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = StructSite;
}
