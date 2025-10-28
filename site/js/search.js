/* Advanced Search Functionality for Phase 3 */

class AdvancedSearch {
  constructor() {
    this.searchIndex = [];
    this.searchInput = document.getElementById('search-input');
    this.searchResults = document.getElementById('search-results');
    this.isSearchVisible = false;
    this.selectedIndex = -1;

    this.init();
  }

  init() {
    this.buildSearchIndex();
    this.setupEventListeners();
    this.setupKeyboardShortcuts();
  }

  buildSearchIndex() {
    // Index content from different sections
    this.searchIndex = [
      // Commands
      {
        title: 'structkit generate',
        description: 'Generate project structure from YAML configuration',
        category: 'Commands',
        url: '#api-preview',
        content:
          'generate project structure yaml configuration template variables',
      },
      {
        title: 'structkit validate',
        description: 'Validate YAML configuration syntax and structure',
        category: 'Commands',
        url: '#api-preview',
        content: 'validate yaml configuration syntax structure check',
      },
      {
        title: 'structkit list',
        description: 'List available structure templates',
        category: 'Commands',
        url: '#api-preview',
        content: 'list available structure templates browse',
      },

      // Configuration
      {
        title: 'files',
        description: 'Define files to be created in your project',
        category: 'Configuration',
        url: '#quick-reference',
        content: 'files configuration yaml content template create',
      },
      {
        title: 'folders',
        description: 'Define folder structures and nested configurations',
        category: 'Configuration',
        url: '#quick-reference',
        content: 'folders directory structure nested configuration',
      },
      {
        title: 'variables',
        description: 'Define template variables for dynamic content',
        category: 'Configuration',
        url: '#quick-reference',
        content: 'variables template dynamic content jinja2',
      },

      // Features
      {
        title: 'Template Variables',
        description: 'Use Jinja2 syntax for dynamic content generation',
        category: 'Features',
        url: '#features',
        content: 'template variables jinja2 dynamic content generation',
      },
      {
        title: 'Remote Content',
        description: 'Fetch files from GitHub, HTTP/HTTPS, and cloud storage',
        category: 'Features',
        url: '#features',
        content: 'remote content github http https cloud storage fetch',
      },
      {
        title: 'Dry Run Mode',
        description: 'Preview changes before applying them to your project',
        category: 'Features',
        url: '#features',
        content: 'dry run preview changes before applying project',
      },

      // Community
      {
        title: 'GitHub Repository',
        description: 'Contribute to StructKit development and report issues',
        category: 'Community',
        url: '#community',
        content: 'github repository contribute development issues',
      },
      {
        title: 'Discussions',
        description: 'Ask questions and share ideas with the community',
        category: 'Community',
        url: '#community',
        content: 'discussions questions community ideas help',
      },

      // Getting Started
      {
        title: 'Installation',
        description: 'Install StructKit using pip, Docker, or from source',
        category: 'Getting Started',
        url: '#installation',
        content: 'installation install pip docker source setup',
      },
      {
        title: 'Quick Start',
        description: 'Get started with StructKit in minutes using our wizard',
        category: 'Getting Started',
        url: '#wizard',
        content: 'quick start wizard getting started minutes tutorial',
      },
    ];
  }

  setupEventListeners() {
    if (!this.searchInput || !this.searchResults) return;

    // Search input events
    this.searchInput.addEventListener(
      'input',
      this.debounce(this.handleSearch.bind(this), 300)
    );
    this.searchInput.addEventListener('focus', () => {
      if (this.searchInput.value.trim()) {
        this.showSearchResults();
      }
    });
    this.searchInput.addEventListener('blur', () => {
      // Delay hiding to allow clicking on results
      setTimeout(() => this.hideSearchResults(), 150);
    });

    // Navigation with arrow keys
    this.searchInput.addEventListener(
      'keydown',
      this.handleKeyNavigation.bind(this)
    );

    // Close search when clicking outside
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.search-container')) {
        this.hideSearchResults();
      }
    });
  }

  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Ctrl+K or Cmd+K to focus search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        this.focusSearch();
      }

      // Escape to close search
      if (e.key === 'Escape' && this.isSearchVisible) {
        this.hideSearchResults();
        this.searchInput.blur();
      }
    });
  }

  handleSearch(e) {
    const query = e.target.value.trim().toLowerCase();

    if (query.length < 2) {
      this.hideSearchResults();
      return;
    }

    const results = this.searchIndex
      .filter((item) => {
        const searchText =
          `${item.title} ${item.description} ${item.content}`.toLowerCase();
        return searchText.includes(query);
      })
      .slice(0, 8); // Limit to 8 results

    this.displaySearchResults(results, query);
  }

  displaySearchResults(results, query) {
    if (results.length === 0) {
      this.searchResults.innerHTML = `
        <div class="search-no-results">
          <i class="fas fa-search"></i>
          <p>No results found for "${query}"</p>
          <small>Try different keywords or check our documentation</small>
        </div>
      `;
    } else {
      this.searchResults.innerHTML = results
        .map(
          (result, index) => `
        <div class="search-result-item ${
          index === this.selectedIndex ? 'selected' : ''
        }"
             data-url="${result.url}" data-index="${index}">
          <div class="search-result-category">${result.category}</div>
          <div class="search-result-title">${this.highlightMatch(
            result.title,
            query
          )}</div>
          <div class="search-result-description">${this.highlightMatch(
            result.description,
            query
          )}</div>
        </div>
      `
        )
        .join('');

      // Add click handlers
      this.searchResults
        .querySelectorAll('.search-result-item')
        .forEach((item) => {
          item.addEventListener('click', () => {
            this.navigateToResult(item.dataset.url);
          });
        });
    }

    this.showSearchResults();
  }

  highlightMatch(text, query) {
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  }

  handleKeyNavigation(e) {
    if (!this.isSearchVisible) return;

    const results = this.searchResults.querySelectorAll('.search-result-item');

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        this.selectedIndex = Math.min(
          this.selectedIndex + 1,
          results.length - 1
        );
        this.updateSelection();
        break;

      case 'ArrowUp':
        e.preventDefault();
        this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
        this.updateSelection();
        break;

      case 'Enter':
        e.preventDefault();
        if (this.selectedIndex >= 0 && results[this.selectedIndex]) {
          this.navigateToResult(results[this.selectedIndex].dataset.url);
        }
        break;
    }
  }

  updateSelection() {
    const results = this.searchResults.querySelectorAll('.search-result-item');
    results.forEach((item, index) => {
      item.classList.toggle('selected', index === this.selectedIndex);
    });
  }

  navigateToResult(url) {
    this.hideSearchResults();
    this.searchInput.blur();

    // Navigate to the URL
    if (url.startsWith('#')) {
      const element = document.querySelector(url);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });

        // Add highlight effect
        element.style.outline = '2px solid var(--color-primary)';
        element.style.outlineOffset = '4px';
        setTimeout(() => {
          element.style.outline = '';
          element.style.outlineOffset = '';
        }, 2000);
      }
    } else {
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  }

  focusSearch() {
    if (this.searchInput) {
      this.searchInput.focus();
      this.searchInput.select();
    }
  }

  showSearchResults() {
    if (this.searchResults) {
      this.searchResults.classList.remove('hidden');
      this.isSearchVisible = true;
      this.selectedIndex = -1;
    }
  }

  hideSearchResults() {
    if (this.searchResults) {
      this.searchResults.classList.add('hidden');
      this.isSearchVisible = false;
      this.selectedIndex = -1;
    }
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
}

// Enhanced search styles
const searchStyles = `
<style>
.search-container {
  position: relative;
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  max-height: 400px;
  overflow-y: auto;
  z-index: 1000;
  margin-top: 4px;
}

.search-results.hidden {
  display: none;
}

.search-result-item {
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.2s ease;
}

.search-result-item:last-child {
  border-bottom: none;
}

.search-result-item:hover,
.search-result-item.selected {
  background: rgba(0, 255, 136, 0.1);
  border-left: 3px solid var(--color-primary);
}

.search-result-category {
  font-size: 0.75rem;
  color: var(--color-primary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.25rem;
}

.search-result-title {
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 0.25rem;
}

.search-result-description {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  line-height: 1.4;
}

.search-result-item mark {
  background: rgba(0, 255, 136, 0.3);
  color: var(--color-primary);
  padding: 0 2px;
  border-radius: 2px;
}

.search-no-results {
  padding: 2rem;
  text-align: center;
  color: var(--color-text-secondary);
}

.search-no-results i {
  font-size: 2rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.search-no-results p {
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.search-no-results small {
  opacity: 0.7;
}

/* Search input enhancements */
.search-input {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  color: var(--color-text-primary);
  font-size: 0.875rem;
  width: 300px;
  transition: all 0.3s ease;
  margin-left: var(--space-4); /* Add proper spacing from navigation */
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 3px rgba(0, 255, 136, 0.1);
}

.search-input::placeholder {
  color: var(--color-text-secondary);
}

.search-icon {
  position: absolute;
  left: calc(var(--space-4) + 0.75rem); /* Adjust for the margin */
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-secondary);
  pointer-events: none;
}

@media (max-width: 1024px) {
  .search-input {
    width: 250px;
    margin-left: var(--space-3);
  }

  .search-icon {
    left: calc(var(--space-3) + 0.75rem);
  }
}

@media (max-width: 768px) {
  .search-input {
    width: 200px;
    margin-left: var(--space-2);
    font-size: 0.8rem;
    padding: 0.6rem 0.8rem 0.6rem 2.2rem;
  }

  .search-results {
    left: -50px;
    right: -50px;
  }

  .search-icon {
    left: calc(var(--space-2) + 0.6rem);
    font-size: 0.8rem;
  }
}

@media (max-width: 640px) {
  .search-input {
    width: 160px;
    margin-left: var(--space-1);
  }

  .search-icon {
    left: calc(var(--space-1) + 0.6rem);
  }
}

@media (max-width: 480px) {
  .search-container {
    display: none; /* Hide search on very small screens to save space */
  }
}
</style>
`;

// Initialize advanced search when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Add search styles
  document.head.insertAdjacentHTML('beforeend', searchStyles);

  // Initialize search
  window.advancedSearch = new AdvancedSearch();
});
