/* Phase 3: Advanced JavaScript Features & Documentation Integration */

class StructPhase3 {
  constructor() {
    this.currentWizardStep = 0;
    this.wizardData = {};
    this.currentApiTab = 'commands';
    this.currentShowcaseFilter = 'all';
    this.init();
  }

  init() {
    this.initDocumentationFeatures();
    this.initCommunityFeatures();
    this.initGettingStartedWizard();
    this.initAPIPreview();
    this.initProjectShowcase();
    this.initTestimonials();
    this.initPerformanceOptimizations();
  }

  /* ===== DOCUMENTATION INTEGRATION ===== */

  initDocumentationFeatures() {
    this.createQuickReference();
    this.setupQuickReferenceInteractions();
  }

  createQuickReference() {
    const referenceData = [
      {
        title: 'Basic Commands',
        icon: 'fas fa-terminal',
        items: [
          {
            title: 'structkit generate',
            description: 'Generate project structure from configuration',
            code: 'structkit generate config.yaml ./output'
          },
          {
            title: 'structkit validate',
            description: 'Validate YAML configuration file',
            code: 'structkit validate config.yaml'
          },
          {
            title: 'structkit list',
            description: 'List available structure templates',
            code: 'structkit list'
          }
        ]
      },
      {
        title: 'Configuration',
        icon: 'fas fa-file-code',
        items: [
          {
            title: 'files',
            description: 'Define files to be created',
            code: 'files:\n  - README.md:\n      content: "# Project"'
          },
          {
            title: 'folders',
            description: 'Define folder structures',
            code: 'folders:\n  - src/:\n      struct: python/module'
          },
          {
            title: 'variables',
            description: 'Define template variables',
            code: 'variables:\n  - project_name:\n      type: string'
          }
        ]
      },
      {
        title: 'Template Features',
        icon: 'fas fa-magic',
        items: [
          {
            title: 'Variables',
            description: 'Use Jinja2 template variables',
            code: '{{@ project_name @}}'
          },
          {
            title: 'Filters',
            description: 'Apply custom filters',
            code: '{{@ name | slugify @}}'
          },
          {
            title: 'Remote Content',
            description: 'Fetch content from URLs',
            code: 'file: github://user/repo/main/file.txt'
          }
        ]
      }
    ];

    const quickRefSection = document.querySelector('#quick-reference .reference-grid');
    if (quickRefSection) {
      quickRefSection.innerHTML = referenceData.map(section => `
        <div class="reference-card">
          <div class="reference-card-header">
            <i class="${section.icon} reference-icon"></i>
            <h3 class="reference-card-title">${section.title}</h3>
          </div>
          <div class="reference-content">
            ${section.items.map(item => `
              <div class="reference-item">
                <i class="fas fa-chevron-right reference-item-icon"></i>
                <div class="reference-item-content">
                  <div class="reference-item-title">${item.title}</div>
                  <div class="reference-item-description">${item.description}</div>
                  <div class="reference-code">${item.code}</div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      `).join('');
    }
  }

  setupQuickReferenceInteractions() {
    // Copy code functionality
    document.addEventListener('click', (e) => {
      if (e.target.closest('.reference-code')) {
        const code = e.target.closest('.reference-code').textContent;
        this.copyToClipboard(code);
        this.showToast('Code copied to clipboard!');
      }
    });
  }

  /* ===== API DOCUMENTATION PREVIEW ===== */

  initAPIPreview() {
    this.createAPIPreview();
    this.setupAPITabs();
  }

  createAPIPreview() {
    const apiData = {
      commands: {
        title: 'CLI Commands',
        methods: [
          {
            type: 'CMD',
            name: 'structkit generate',
            description: 'Generate project structure from YAML configuration',
            code: `# Basic usage
structkit generate config.yaml ./output

# With variables
structkit generate config.yaml ./output --var project_name="MyProject"

# Dry run
structkit generate config.yaml ./output --dry-run`
          },
          {
            type: 'CMD',
            name: 'structkit validate',
            description: 'Validate YAML configuration syntax and structure',
            code: `# Validate configuration
structkit validate config.yaml

# Validate with verbose output
structkit validate config.yaml --verbose`
          }
        ]
      },
      yaml: {
        title: 'YAML Configuration',
        methods: [
          {
            type: 'YAML',
            name: 'Basic Structure',
            description: 'Define files, folders, and variables in your configuration',
            code: `files:
  - README.md:
      content: |
        # {{@ project_name @}}
        {{@ description @}}

folders:
  - src/:
      struct: python/module
      with:
        module_name: "{{@ project_name | slugify @}}"

variables:
  - project_name:
      description: "Name of your project"
      type: string
      default: "MyProject"
  - description:
      description: "Project description"
      type: string`
          }
        ]
      },
      templates: {
        title: 'Template Features',
        methods: [
          {
            type: 'TPL',
            name: 'Variable Substitution',
            description: 'Use Jinja2 syntax for dynamic content generation',
            code: `# Basic variable
{{@ variable_name @}}

# With default value
{{@ variable_name | default("default_value") @}}

# Apply filters
{{@ project_name | slugify @}}
{{@ version | latest_release @}}
{{@ branch | default_branch @}}`
          }
        ]
      }
    };

    const apiContent = document.querySelector('#api-preview .api-content');
    if (apiContent) {
      apiContent.innerHTML = `
        <div class="api-tabs">
          ${Object.keys(apiData).map(key => `
            <button class="api-tab ${key === 'commands' ? 'active' : ''}" data-tab="${key}">
              ${apiData[key].title}
            </button>
          `).join('')}
        </div>
        ${Object.entries(apiData).map(([key, data]) => `
          <div class="api-panel ${key === 'commands' ? 'active' : ''}" data-panel="${key}">
            <div class="api-section">
              <h3 class="api-section-title">${data.title}</h3>
              ${data.methods.map(method => `
                <div class="api-method">
                  <div class="api-method-header">
                    <span class="api-method-type">${method.type}</span>
                    <span class="api-method-name">${method.name}</span>
                  </div>
                  <div class="api-method-description">${method.description}</div>
                  <div class="api-code-block">
                    <button class="api-code-copy" onclick="structPhase3.copyToClipboard(\`${method.code.replace(/`/g, '\\`')}\`)">
                      <i class="fas fa-copy"></i>
                    </button>
                    <pre>${method.code}</pre>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        `).join('')}
      `;
    }
  }

  setupAPITabs() {
    document.addEventListener('click', (e) => {
      if (e.target.matches('.api-tab')) {
        const tabName = e.target.dataset.tab;
        this.switchAPITab(tabName);
      }
    });
  }

  switchAPITab(tabName) {
    // Update active tab
    document.querySelectorAll('.api-tab').forEach(tab => tab.classList.remove('active'));
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update active panel
    document.querySelectorAll('.api-panel').forEach(panel => panel.classList.remove('active'));
    document.querySelector(`[data-panel="${tabName}"]`).classList.add('active');

    this.currentApiTab = tabName;
  }

  /* ===== GETTING STARTED WIZARD ===== */

  initGettingStartedWizard() {
    this.createWizardSteps();
    this.setupWizardNavigation();
  }

  createWizardSteps() {
    const wizardSteps = [
      {
        title: 'Choose Your Project Type',
        description: 'Select the type of project you want to create with StructKit',
        options: [
          {
            id: 'python',
            title: 'Python Project',
            description: 'Create a Python application or library structure'
          },
          {
            id: 'web',
            title: 'Web Application',
            description: 'Generate a web application with frontend/backend structure'
          },
          {
            id: 'terraform',
            title: 'Infrastructure as Code',
            description: 'Create Terraform modules and infrastructure templates'
          },
          {
            id: 'custom',
            title: 'Custom Structure',
            description: 'Define your own project structure from scratch'
          }
        ]
      },
      {
        title: 'Installation Method',
        description: 'Choose how you want to install StructKit',
        options: [
          {
            id: 'pip',
            title: 'pip install',
            description: 'Install using Python package manager (recommended)'
          },
          {
            id: 'docker',
            title: 'Docker',
            description: 'Use Docker container for isolated environment'
          },
          {
            id: 'source',
            title: 'From Source',
            description: 'Clone and install from GitHub repository'
          }
        ]
      },
      {
        title: 'Configuration',
        description: 'Generate your first StructKit configuration',
        isResult: true
      }
    ];

    const wizardContainer = document.querySelector('#wizard .wizard-content');
    if (wizardContainer) {
      wizardContainer.innerHTML = `
        <div class="wizard-progress">
          <div class="wizard-progress-line" style="width: 0%"></div>
          ${wizardSteps.map((step, index) => `
            <div class="wizard-step ${index === 0 ? 'active' : ''}" data-step="${index}">
              ${index + 1}
            </div>
          `).join('')}
        </div>
        ${wizardSteps.map((step, index) => `
          <div class="wizard-panel ${index === 0 ? 'active' : ''}" data-panel="${index}">
            <h3 class="wizard-panel-title">${step.title}</h3>
            <p class="wizard-panel-description">${step.description}</p>
            ${step.isResult ? this.createWizardResult() : `
              <div class="wizard-options">
                ${step.options.map(option => `
                  <div class="wizard-option" data-value="${option.id}">
                    <div class="wizard-option-title">${option.title}</div>
                    <div class="wizard-option-description">${option.description}</div>
                  </div>
                `).join('')}
              </div>
            `}
            <div class="wizard-actions">
              <button class="wizard-btn wizard-btn-secondary" onclick="structPhase3.previousWizardStep()" ${index === 0 ? 'disabled' : ''}>
                Previous
              </button>
              <button class="wizard-btn" onclick="structPhase3.nextWizardStep()" ${index === wizardSteps.length - 1 ? 'style="display:none"' : ''} ${!step.isResult ? 'disabled style="opacity: 0.5"' : ''}>
                Next
              </button>
              ${index === wizardSteps.length - 1 ? `
                <button class="wizard-btn" onclick="structPhase3.downloadWizardConfig()">
                  Download Configuration
                </button>
              ` : ''}
            </div>
          </div>
        `).join('')}
      `;
    }
  }

  createWizardResult() {
    return `
      <div class="api-code-block">
        <button class="api-code-copy" onclick="structPhase3.copyWizardConfig()">
          <i class="fas fa-copy"></i>
        </button>
        <pre id="wizard-result">Loading configuration...</pre>
      </div>
      <div class="wizard-result-actions">
        <p>Your configuration is ready! You can:</p>
        <ul>
          <li>Copy the configuration above</li>
          <li>Download it as a YAML file</li>
          <li>Start building your project structure</li>
        </ul>
      </div>
    `;
  }

  setupWizardNavigation() {
    document.addEventListener('click', (e) => {
      // Check if the clicked element is a wizard option or its child
      const wizardOption = e.target.closest('.wizard-option');
      if (wizardOption) {
        const panel = wizardOption.closest('.wizard-panel');
        if (!panel || !panel.classList.contains('active')) {
          return; // Only handle clicks in the active panel
        }

        // Remove selection from all options in this panel
        panel.querySelectorAll('.wizard-option').forEach(opt => opt.classList.remove('selected'));
        wizardOption.classList.add('selected');

        const step = parseInt(panel.dataset.panel);
        const value = wizardOption.dataset.value;
        this.wizardData[step] = value;

        console.log(`Wizard step ${step} selected: ${value}`); // Debug log

        // Remove any existing error when selection is made
        const existingError = panel.querySelector('.wizard-error');
        if (existingError) {
          existingError.remove();
        }

        // Enable the Next button
        const nextBtn = panel.querySelector('.wizard-btn:not(.wizard-btn-secondary)');
        if (nextBtn && !nextBtn.textContent.includes('Download')) {
          nextBtn.disabled = false;
          nextBtn.style.opacity = '1';
        }
      }
    });
  }

  nextWizardStep() {
    // Validate that current step has a selection
    if (!this.wizardData[this.currentWizardStep]) {
      this.showWizardError('Please make a selection before continuing.');
      return;
    }

    if (this.currentWizardStep < 2) {
      this.currentWizardStep++;
      this.updateWizardStep();

      // Debug: Log current step and check if panel exists
      console.log(`Advanced to step ${this.currentWizardStep}`);
      const activePanel = document.querySelector('.wizard-panel.active');
      console.log('Active panel:', activePanel);
      console.log('Wizard options in active panel:', activePanel ? activePanel.querySelectorAll('.wizard-option').length : 0);

      if (this.currentWizardStep === 2) {
        this.generateWizardResult();
      }
    }
  }

  previousWizardStep() {
    if (this.currentWizardStep > 0) {
      this.currentWizardStep--;
      this.updateWizardStep();
    }
  }

  showWizardError(message) {
    // Remove any existing error
    const existingError = document.querySelector('.wizard-error');
    if (existingError) {
      existingError.remove();
    }

    // Create and show error message
    const activePanel = document.querySelector('.wizard-panel.active');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'wizard-error';
    errorDiv.style.cssText = `
      background-color: var(--color-error);
      color: white;
      padding: var(--space-3);
      border-radius: var(--radius-md);
      margin: var(--space-4) 0;
      font-size: var(--text-sm);
    `;
    errorDiv.textContent = message;

    const actions = activePanel.querySelector('.wizard-actions');
    actions.parentNode.insertBefore(errorDiv, actions);

    // Auto-hide error after 3 seconds
    setTimeout(() => {
      if (errorDiv.parentNode) {
        errorDiv.remove();
      }
    }, 3000);
  }

  updateWizardStep() {
    // Update progress
    const progress = (this.currentWizardStep / 2) * 100;
    document.querySelector('.wizard-progress-line').style.width = `${progress}%`;

    // Update steps
    document.querySelectorAll('.wizard-step').forEach((step, index) => {
      step.classList.remove('active', 'completed');
      if (index < this.currentWizardStep) {
        step.classList.add('completed');
      } else if (index === this.currentWizardStep) {
        step.classList.add('active');
      }
    });

    // Update panels
    document.querySelectorAll('.wizard-panel').forEach((panel, index) => {
      panel.classList.remove('active');
      if (index === this.currentWizardStep) {
        panel.classList.add('active');

        // Update button states for the active panel
        const nextBtn = panel.querySelector('.wizard-btn:not(.wizard-btn-secondary)');
        const hasSelection = this.wizardData[index] !== undefined;

        if (nextBtn && !nextBtn.textContent.includes('Download')) {
          nextBtn.disabled = !hasSelection;
          nextBtn.style.opacity = hasSelection ? '1' : '0.5';
        }

        // Update Previous button
        const prevBtn = panel.querySelector('.wizard-btn-secondary');
        if (prevBtn) {
          prevBtn.disabled = index === 0;
        }
      }
    });
  }

  generateWizardResult() {
    const projectType = this.wizardData[0] || 'custom';
    const installMethod = this.wizardData[1] || 'pip';

    const configurations = {
      python: `files:
  - README.md:
      content: |
        # {{@ project_name @}}
        {{@ description @}}

        ## Installation
        \`\`\`bash
        pip install -e .
        \`\`\`
  - setup.py:
      content: |
        from setuptools import setup, find_packages

        setup(
            name="{{@ project_name | slugify @}}",
            version="0.1.0",
            packages=find_packages(),
        )
  - requirements.txt:
      content: |
        # Add your dependencies here

folders:
  - {{@ project_name | slugify @}}/:
      struct: python/module
  - tests/:
      struct: python/tests

variables:
  - project_name:
      description: "Name of your Python project"
      type: string
      default: "MyPythonProject"
  - description:
      description: "Project description"
      type: string
      default: "A Python project created with StructKit"`,

      web: `files:
  - README.md:
      content: |
        # {{@ project_name @}}
        {{@ description @}}

        ## Development
        \`\`\`bash
        npm install
        npm start
        \`\`\`
  - package.json:
      content: |
        {
          "name": "{{@ project_name | slugify @}}",
          "version": "1.0.0",
          "description": "{{@ description @}}",
          "main": "src/index.js",
          "scripts": {
            "start": "node src/index.js"
          }
        }

folders:
  - src/:
      struct: web/frontend
  - api/:
      struct: web/backend

variables:
  - project_name:
      description: "Name of your web project"
      type: string
      default: "MyWebApp"
  - description:
      description: "Project description"
      type: string
      default: "A web application created with StructKit"`,
    };

    const config = configurations[projectType] || configurations.python;

    setTimeout(() => {
      document.getElementById('wizard-result').textContent = config;
    }, 500);

    this.generatedConfig = config;
  }

  copyWizardConfig() {
    this.copyToClipboard(this.generatedConfig);
    this.showToast('Configuration copied to clipboard!');
  }

  downloadWizardConfig() {
    const blob = new Blob([this.generatedConfig], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'struct-config.yaml';
    a.click();
    URL.revokeObjectURL(url);
  }

  /* ===== COMMUNITY FEATURES ===== */

  initCommunityFeatures() {
    this.createCommunitySection();
    this.loadGitHubCommunityStats();
  }

  createCommunitySection() {
    const communityData = [
      {
        icon: 'fab fa-github',
        title: 'GitHub Repository',
        description:
          'Contribute to StructKit, report issues, and collaborate with the community',
        action: 'View on GitHub',
        link: 'https://github.com/httpdss/struct',
      },
      {
        icon: 'fas fa-comments',
        title: 'Discussions',
        description:
          'Ask questions, share ideas, and get help from other StructKit users',
        action: 'Join Discussion',
        link: 'https://github.com/httpdss/structkit/discussions',
      },
      {
        icon: 'fas fa-book',
        title: 'Documentation',
        description: 'Comprehensive guides, tutorials, and API documentation',
        action: 'Read Docs',
        link: 'https://httpdss.github.io/structkit/docs/',
      },
      {
        icon: 'fas fa-heart',
        title: 'Support Project',
        description: 'Help keep StructKit development active and growing',
        action: 'Support Us',
        link: 'https://patreon.com/structproject',
      },
    ];

    const communityGrid = document.querySelector('#community .community-grid');
    if (communityGrid) {
      communityGrid.innerHTML = communityData.map(item => `
        <div class="community-card">
          <div class="community-card-icon">
            <i class="${item.icon}"></i>
          </div>
          <h3 class="community-card-title">${item.title}</h3>
          <p class="community-card-description">${item.description}</p>
          <a href="${item.link}" class="community-card-action" target="_blank" rel="noopener">
            ${item.action}
          </a>
        </div>
      `).join('');
    }
  }

  async loadGitHubCommunityStats() {
    try {
      const [repoResponse, contributorsResponse] = await Promise.all([
        fetch('https://api.github.com/repos/httpdss/struct'),
        fetch('https://api.github.com/repos/httpdss/structkit/contributors')
      ]);

      const repo = await repoResponse.json();
      const contributors = await contributorsResponse.json();

      this.updateCommunityStats(repo, contributors);
    } catch (error) {
      console.warn('Failed to load community stats:', error);
    }
  }

  updateCommunityStats(repo, contributors) {
    const statsHTML = `
      <div class="community-stats">
        <div class="stat-item">
          <div class="stat-number">${repo.stargazers_count}</div>
          <div class="stat-label">GitHub Stars</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">${repo.forks_count}</div>
          <div class="stat-label">Forks</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">${contributors.length}</div>
          <div class="stat-label">Contributors</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">${repo.open_issues_count}</div>
          <div class="stat-label">Open Issues</div>
        </div>
      </div>
    `;

    const communityHeader = document.querySelector('#community .community-header');
    if (communityHeader) {
      communityHeader.insertAdjacentHTML('afterend', statsHTML);
    }
  }

  /* ===== TESTIMONIALS ===== */

  initTestimonials() {
    this.createTestimonials();
  }

  createTestimonials() {
    const testimonials = [
      {
        content:
          'StructKit has completely transformed how we scaffold new projects. What used to take hours of manual setup now takes minutes. The YAML configuration is intuitive and the template system is incredibly powerful.',
        author: 'Sarah Chen',
        role: 'Senior DevOps Engineer',
        avatar:
          'https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=100&h=100&fit=crop&crop=face',
      },
      {
        content:
          "The best project structure generator I've used. The ability to fetch content from remote sources and the Jinja2 templating makes it perfect for creating consistent, enterprise-ready project layouts.",
        author: 'Marcus Rodriguez',
        role: 'Platform Architect',
        avatar:
          'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
      },
      {
        content:
          "StructKit's flexibility is unmatched. We use it for everything from microservices to Terraform modules. The hook system allows us to integrate it perfectly into our CI/CD pipeline.",
        author: 'Alex Thompson',
        role: 'Lead Developer',
        avatar:
          'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face',
      },
    ];

    const testimonialsGrid = document.querySelector('#testimonials .testimonials-grid');
    if (testimonialsGrid) {
      testimonialsGrid.innerHTML = testimonials.map(testimonial => `
        <div class="testimonial">
          <div class="testimonial-content">${testimonial.content}</div>
          <div class="testimonial-author">
            <img src="${testimonial.avatar}" alt="${testimonial.author}" class="testimonial-avatar">
            <div class="testimonial-info">
              <div class="testimonial-name">${testimonial.author}</div>
              <div class="testimonial-role">${testimonial.role}</div>
            </div>
          </div>
        </div>
      `).join('');
    }
  }

  /* ===== PROJECT SHOWCASE ===== */

  initProjectShowcase() {
    this.createProjectShowcase();
    this.setupShowcaseFilters();
  }

  createProjectShowcase() {
    const projects = [
      {
        title: 'Terraform AWS Modules',
        description: 'Complete AWS infrastructure modules with best practices and security configurations',
        tags: ['terraform', 'aws', 'infrastructure'],
        icon: 'fas fa-cloud',
        category: 'infrastructure',
        github: 'https://github.com/example/terraform-aws-modules',
        demo: 'https://example.com/demo'
      },
      {
        title: 'Python Microservice Template',
        description: 'FastAPI-based microservice with Docker, testing, and CI/CD pipeline setup',
        tags: ['python', 'fastapi', 'microservice', 'docker'],
        icon: 'fab fa-python',
        category: 'backend',
        github: 'https://github.com/example/python-microservice',
        demo: 'https://example.com/demo'
      },
      {
        title: 'React Component Library',
        description: 'Reusable React components with Storybook, testing, and automated publishing',
        tags: ['react', 'typescript', 'storybook'],
        icon: 'fab fa-react',
        category: 'frontend',
        github: 'https://github.com/example/react-components',
        demo: 'https://example.com/demo'
      },
      {
        title: 'DevOps Toolkit',
        description: 'Complete DevOps setup with monitoring, logging, and deployment automation',
        tags: ['devops', 'kubernetes', 'monitoring'],
        icon: 'fas fa-tools',
        category: 'devops',
        github: 'https://github.com/example/devops-toolkit',
        demo: 'https://example.com/demo'
      }
    ];

    const showcaseGrid = document.querySelector('#project-showcase .showcase-grid');
    if (showcaseGrid) {
      showcaseGrid.innerHTML = projects.map(project => `
        <div class="showcase-project" data-category="${project.category}">
          <div class="showcase-project-image">
            <i class="${project.icon}"></i>
          </div>
          <div class="showcase-project-content">
            <h3 class="showcase-project-title">${project.title}</h3>
            <p class="showcase-project-description">${project.description}</p>
            <div class="showcase-project-tags">
              ${project.tags.map(tag => `<span class="showcase-project-tag">${tag}</span>`).join('')}
            </div>
            <div class="showcase-project-links">
              <a href="${project.github}" class="showcase-project-link" target="_blank" rel="noopener">
                <i class="fab fa-github"></i> Code
              </a>
              <a href="${project.demo}" class="showcase-project-link" target="_blank" rel="noopener">
                <i class="fas fa-external-link-alt"></i> Demo
              </a>
            </div>
          </div>
        </div>
      `).join('');
    }
  }

  setupShowcaseFilters() {
    const filters = ['all', 'infrastructure', 'backend', 'frontend', 'devops'];
    const filtersContainer = document.querySelector('#project-showcase .showcase-filters');

    if (filtersContainer) {
      filtersContainer.innerHTML = filters.map(filter => `
        <button class="showcase-filter ${filter === 'all' ? 'active' : ''}" data-filter="${filter}">
          ${filter.charAt(0).toUpperCase() + filter.slice(1)}
        </button>
      `).join('');
    }

    document.addEventListener('click', (e) => {
      if (e.target.matches('.showcase-filter')) {
        const filter = e.target.dataset.filter;
        this.filterShowcaseProjects(filter);
      }
    });
  }

  filterShowcaseProjects(filter) {
    // Update active filter
    document.querySelectorAll('.showcase-filter').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[data-filter="${filter}"]`).classList.add('active');

    // Filter projects
    const projects = document.querySelectorAll('.showcase-project');
    projects.forEach(project => {
      if (filter === 'all' || project.dataset.category === filter) {
        project.style.display = 'block';
        project.style.animation = 'fadeIn 0.3s ease';
      } else {
        project.style.display = 'none';
      }
    });

    this.currentShowcaseFilter = filter;
  }

  /* ===== PERFORMANCE OPTIMIZATIONS ===== */

  initPerformanceOptimizations() {
    this.setupIntersectionObserver();
    this.setupImageLazyLoading();
    this.optimizeAnimations();
  }

  setupIntersectionObserver() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in');
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    // Observe all cards and interactive elements
    const elementsToObserve = document.querySelectorAll(`
      .reference-card,
      .community-card,
      .testimonial,
      .showcase-project,
      .api-method
    `);

    elementsToObserve.forEach(el => observer.observe(el));
  }

  setupImageLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');

    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
          imageObserver.unobserve(img);
        }
      });
    });

    images.forEach(img => imageObserver.observe(img));
  }

  optimizeAnimations() {
    // Reduce animations for users who prefer reduced motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      document.documentElement.style.setProperty('--animation-duration', '0.1s');
    }
  }

  /* ===== UTILITY METHODS ===== */

  copyToClipboard(text) {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text);
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
    }
  }

  showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: var(--color-primary);
      color: var(--color-bg-primary);
      padding: 1rem 2rem;
      border-radius: 8px;
      z-index: 10000;
      animation: slideInRight 0.3s ease;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
      toast.style.animation = 'slideOutRight 0.3s ease';
      setTimeout(() => {
        document.body.removeChild(toast);
      }, 300);
    }, 3000);
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

// Initialize Phase 3 features when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.structPhase3 = new StructPhase3();
});

// Add CSS animations
const additionalCSS = `
<style>
.animate-in {
  animation: slideInUp 0.6s ease forwards;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideOutRight {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(30px);
  }
}

.community-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: 0.5rem;
}

.stat-label {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', additionalCSS);
