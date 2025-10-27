// StructKit Static Site - Main JavaScript

// Initialize all components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  initializeInstallationTabs();
  initializeDemoCarousel();
  initializeCodeCopyButtons();
  initializeGitHubStats();
  initializeAnimations();
  initializeMobileMenu();
});

// Installation Tabs Component
function initializeInstallationTabs() {
  const tabButtons = document.querySelectorAll('.tab-button');
  const tabPanes = document.querySelectorAll('.tab-pane');

  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      const targetTab = button.dataset.tab;

      // Remove active class from all buttons and panes
      tabButtons.forEach(btn => btn.classList.remove('active'));
      tabPanes.forEach(pane => pane.classList.remove('active'));

      // Add active class to clicked button and corresponding pane
      button.classList.add('active');
      const targetPane = document.getElementById(targetTab);
      if (targetPane) {
        targetPane.classList.add('active');
      }
    });
  });
}

// Demo Carousel Component
function initializeDemoCarousel() {
  const demoTabs = document.querySelectorAll('.demo-tab');
  const demoContents = document.querySelectorAll('.demo-content-item');

  demoTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetDemo = tab.dataset.demo;

      // Remove active class from all tabs and contents
      demoTabs.forEach(t => t.classList.remove('active'));
      demoContents.forEach(content => {
        content.classList.remove('active');
        content.classList.remove('fade-in');
      });

      // Add active class to clicked tab and corresponding content
      tab.classList.add('active');
      const targetContent = document.getElementById(targetDemo);
      if (targetContent) {
        targetContent.classList.add('active');
        // Use setTimeout to ensure the display change happens first
        setTimeout(() => {
          targetContent.classList.add('fade-in');
        }, 10);
      }
    });
  });
}

// Code Copy Buttons
function initializeCodeCopyButtons() {
  const copyButtons = document.querySelectorAll('.copy-button');

  copyButtons.forEach(button => {
    button.addEventListener('click', async () => {
      const codeBlock = button.parentElement.querySelector('code');
      const text = codeBlock.textContent;

      try {
        await navigator.clipboard.writeText(text);

        // Visual feedback
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        button.style.backgroundColor = 'var(--color-success)';

        setTimeout(() => {
          button.textContent = originalText;
          button.style.backgroundColor = '';
        }, 2000);
      } catch (err) {
        console.error('Failed to copy text: ', err);

        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);

        button.textContent = 'Copied!';
        setTimeout(() => {
          button.textContent = 'Copy';
        }, 2000);
      }
    });
  });
}

// GitHub Stats Component
async function initializeGitHubStats() {
  const statsContainer = document.querySelector('.github-stats');
  if (!statsContainer) return;

  try {
    // Show loading state
    statsContainer.innerHTML = `
      <div class="stat-item skeleton">
        <span class="stat-value">...</span>
        <span class="stat-label">Stars</span>
      </div>
      <div class="stat-item skeleton">
        <span class="stat-value">...</span>
        <span class="stat-label">Forks</span>
      </div>
      <div class="stat-item skeleton">
        <span class="stat-value">...</span>
        <span class="stat-label">Issues</span>
      </div>
      <div class="stat-item skeleton">
        <span class="stat-value">...</span>
        <span class="stat-label">PRs</span>
      </div>
    `;

    // Fetch GitHub stats
    const response = await fetch('https://api.github.com/repos/httpdss/struct');
    const data = await response.json();

    // Update stats with real data
    statsContainer.innerHTML = `
      <div class="stat-item fade-in">
        <span class="stat-value">${formatNumber(data.stargazers_count)}</span>
        <span class="stat-label">Stars</span>
      </div>
      <div class="stat-item fade-in">
        <span class="stat-value">${formatNumber(data.forks_count)}</span>
        <span class="stat-label">Forks</span>
      </div>
      <div class="stat-item fade-in">
        <span class="stat-value">${formatNumber(data.open_issues_count)}</span>
        <span class="stat-label">Issues</span>
      </div>
      <div class="stat-item fade-in">
        <span class="stat-value">${formatNumber(data.size)}</span>
        <span class="stat-label">KB</span>
      </div>
    `;
  } catch (error) {
    console.error('Failed to fetch GitHub stats:', error);

    // Fallback to static numbers
    statsContainer.innerHTML = `
      <div class="stat-item">
        <span class="stat-value">⭐</span>
        <span class="stat-label">Stars</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">🔗</span>
        <span class="stat-label">Forks</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">🐛</span>
        <span class="stat-label">Issues</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">📊</span>
        <span class="stat-label">Stats</span>
      </div>
    `;
  }
}

// Format numbers for display
function formatNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
}

// Scroll Animations
function initializeAnimations() {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('fade-in');
      }
    });
  }, observerOptions);

  // Observe all cards and feature elements
  document.querySelectorAll('.card, .feature-card, .stat-item').forEach(el => {
    observer.observe(el);
  });
}

// Mobile Menu (if needed)
function initializeMobileMenu() {
  const mobileMenuButton = document.querySelector('.mobile-menu-button');
  const mobileMenu = document.querySelector('.mobile-menu');

  if (mobileMenuButton && mobileMenu) {
    mobileMenuButton.addEventListener('click', () => {
      mobileMenu.classList.toggle('active');
      mobileMenuButton.classList.toggle('active');
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!mobileMenuButton.contains(e.target) && !mobileMenu.contains(e.target)) {
        mobileMenu.classList.remove('active');
        mobileMenuButton.classList.remove('active');
      }
    });
  }
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});

// Utility functions
const utils = {
  // Debounce function for performance
  debounce: (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  // Check if element is in viewport
  isInViewport: (element) => {
    const rect = element.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
  }
};

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { utils };
}
