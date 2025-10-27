# Contribs Sub-Structs

The `contribs` folder contains various sub-structs that can be used to generate specific project structures or configurations. Below is a list of all the YAML files in this folder, along with a brief description of what they do and when to use them.

## Table of content

## Table of Contents

- [Contribs Sub-Structs](#contribs-sub-structs)
  - [Sub-Structs](#sub-structs)
    - [General](#general)
      - [`ansible-playbook`](#ansible-playbook)
      - [`chef-cookbook`](#chef-cookbook)
      - [`ci-cd-pipelines`](#ci-cd-pipelines)
      - [`cloudformation-files`](#cloudformation-files)
      - [`docker-files`](#docker-files)
      - [`documentation-template`](#documentation-template)
      - [`git-hooks`](#git-hooks)
      - [`helm-chart`](#helm-chart)
      - [`kubernetes-manifests`](#kubernetes-manifests)
      - [`vagrant-files`](#vagrant-files)
    - [Configs](#configs)
      - [`configs/codeowners`](#configscodeowners)
      - [`configs/devcontainer`](#configsdevcontainer)
      - [`configs/editor-config`](#configseditor-config)
      - [`configs/eslint`](#configseslint)
      - [`configs/jshint`](#configsjshint)
      - [`configs/prettier`](#configsprettier)
    - [Github](#github)
      - [`github/workflows/execute-tf-workflow`](#githubworkflowsexecute-tf-workflow)
      - [`github/workflows/pre-commit`](#githubworkflowspre-commit)
      - [`github/workflows/labeler`](#githubworkflowslabeler)
      - [`github/workflows/release-drafter`](#githubworkflowsrelease-drafter)
      - [`github/workflows/run-struct`](#githubworkflowsrun-struct)
      - [`github/workflows/stale`](#githubworkflowsstale)
      - [`github/templates`](#githubtemplates)
      - [`github/prompts/generic`](#githubpromptsgeneric)
      - [`github/prompts/react-form`](#githubpromptsreact-form)
      - [`github/prompts/security-api`](#githubpromptssecurity-api)
      - [`github/prompts/struct`](#githubpromptsstruct)
    - [Project](#project)
      - [`project/generic`](#projectgeneric)
      - [`project/java`](#projectjava)
      - [`project/nodejs`](#projectnodejs)
      - [`project/rust`](#projectrust)
      - [`project/python`](#projectpython)
      - [`project/go`](#projectgo)
      - [`project/ruby`](#projectruby)
    - [Terraform](#terraform)
      - [`terraform/modules/generic`](#terraformmodulesgeneric)
      - [`terraform/apps/generic`](#terraformappsgeneric)
      - [`terraform/apps/aws-accounts`](#terraformappsaws-accounts)
      - [`terraform/apps/github-organization`](#terraformappsgithub-organization)
      - [`terraform/apps/environments`](#terraformappsenvironments)
      - [`terraform/apps/init`](#terraformappsinit)

## Sub-Structs

### General

#### `ansible-playbook`

- **Description**: Generates a basic structure for an Ansible playbook, including tasks, variables, handlers, and templates.
- **When to Use**: Use this sub-structkit when you need to create an Ansible playbook for automating infrastructure or application deployments.

#### `chef-cookbook`

- **Description**: Creates a Chef cookbook structure with recipes, attributes, templates, and files.
- **When to Use**: Use this sub-structkit when you need to create a Chef cookbook for automating infrastructure or application deployments.

#### `ci-cd-pipelines`

- **Description**: Provides a structure for setting up CI/CD pipelines.
- **When to Use**: this sub-structkit should only be used as a reference for setting up CI/CD pipelines.

#### `cloudformation-files`

- **Description**: Generates a basic structure for AWS CloudFormation templates, including a deployment script and parameters file.
- **When to Use**: Use this sub-structkit when you need to define and deploy AWS infrastructure using CloudFormation.

#### `docker-files`

- **Description**: Creates a structure for Docker-related files, such as Dockerfiles and docker-compose configurations.
- **When to Use**: Use this sub-structkit when you need to define and build Docker images for your application. Another use case is when you need to define and run multi-container applications using Docker Compose.

#### `documentation-template`

- **Description**: Provides a template for project documentation.
- **Description**: This sub-structkit is useful when you need to create a documentation structure for your project.

#### `git-hooks`

- **Description**: Sets up Git hooks, such as pre-commit, pre-push, and commit-msg hooks.
- **When to Use**: Use this sub-structkit when you need to enforce custom Git workflows or validations.

#### `helm-chart`

- **Description**: Generates a Helm chart structure for Kubernetes deployments, including templates and configuration files.
- **When to Use**: Use this sub-structkit when you need to deploy applications to Kubernetes using Helm.

#### `kubernetes-manifests`

- **Description**: Creates a structure for Kubernetes manifests, such as deployments, services, and ingress configurations.
- **When to Use**: Use this sub-structkit when you need to define and deploy Kubernetes resources for your application.

#### `vagrant-files`

- **Description**: Provides a structure for setting up a Vagrant development environment, including a Vagrantfile and provisioning scripts.
- **When to Use**: Use this sub-structkit when you need to create a Vagrant development environment for your project.

### Configs

#### `configs/codeowners`

- **Description**: Provides a template for the `.github/CODEOWNERS` file.
- **When to Use**: Use this sub-structkit when you need to define code owners for your project's repository.

#### `configs/devcontainer`

- **Description**: Provides a template for the `.devcontainer` folder, which contains configuration files for Visual Studio Code's Remote - Containers extension.
- **When to Use**: Use this sub-structkit when you need to define development container configurations for your project.

#### `configs/editor-config`

- **Description**: Provides a template for the `.editorconfig` file, which defines coding styles and formatting rules for different editors and IDEs.
- **When to Use**: Use this sub-structkit when you need to define coding styles and formatting rules for your project.

#### `configs/eslint`

- **Description**: Provides a template for the `.eslintrc` file, which defines ESLint configurations for JavaScript projects.
- **When to Use**: Use this sub-structkit when you need to define ESLint configurations for your JavaScript project.

#### `configs/jshint`

- **Description**: Provides a template for the `.jshintrc` file, which defines JSHint configurations for JavaScript projects.
- **When to Use**: Use this sub-structkit when you need to define JSHint configurations for your JavaScript project.

#### `configs/prettier`

- **Description**: Provides a template for the `.prettierrc` file, which defines Prettier configurations for code formatting.
- **When to Use**: Use this sub-structkit when you need to define Prettier configurations for your project.

### Github

#### `github/workflows/execute-tf-workflow`

- **Description**: Provides a template for a GitHub Actions workflow that executes Terraform commands.
- **When to Use**: Use this sub-structkit when you need to automate Terraform workflows using GitHub Actions. each terraform app should have a workflow that executes terraform commands.

#### `github/workflows/pre-commit`

- **Description**: Provides a template for a GitHub Actions workflow that runs pre-commit checks.
- **When to Use**: Use this sub-structkit when you need to run pre-commit checks on your codebase using GitHub Actions.

#### `github/workflows/labeler`

- **Description**: Provides a template for a GitHub Actions workflow that labels issues and pull requests.
- **When to Use**: Use this sub-structkit when you need to automatically label issues and pull requests based on certain criteria.

#### `github/workflows/release-drafter`

- **Description**: Provides a template for a GitHub Actions workflow that generates release notes using Release Drafter.
- **When to Use**: Use this sub-structkit when you need to automatically generate release notes for your project using Release Drafter.

#### `github/workflows/run-struct`

- **Description**: Provides a template for a GitHub Actions workflow that runs the structkit CLI.
- **When to Use**: Use this sub-structkit when you need to run the structkit CLI as part of your GitHub Actions workflows.

#### `github/workflows/stale`

- **Description**: Provides a template for a GitHub Actions workflow that closes stale issues and pull requests.
- **When to Use**: Use this sub-structkit when you need to automatically close stale issues and pull requests in your repository.

#### `github/templates`

- **Description**: Provides templates for GitHub issue and pull request templates.
- **When to Use**: Use this sub-structkit when you need to define issue and pull request templates for your GitHub repository.

#### `github/prompts/generic`

- **Description**: Provides a generic prompt for creating a new project structure.
- **When to Use**: Use this sub-structkit when you need to create a new project structure using the structkit CLI.

#### `github/prompts/react-form`

- **Description**: Provides a prompt for creating a React form component.
- **When to Use**: Use this sub-structkit when you need to create a React form component.

#### `github/prompts/security-api`

- **Description**: Provides a prompt for creating a security API.
- **When to Use**: Use this sub-structkit when you need to create a security API.

#### `github/prompts/struct`

- **Description**: Provides a prompt for creating a new .struct.yaml file and workflow to run struct.
- **When to Use**: Use this sub-structkit when you need to create a new .struct.yaml file and workflow to run struct.

### Project

#### `project/generic`

- **Description**: Provides a generic project structure with directories for source code, documentation, and tests.
- **When to Use**: Use this sub-structkit when you need to create a generic project structure for your application.

#### `project/java`

- **Description**: Provides a Java project structure with directories for source code, resources, and tests.
- **When to Use**: Use this sub-structkit when you need to create a Java project structure for your application.

#### `project/nodejs`

- **Description**: Provides a Node.js project structure with directories for source code, tests, and configuration files.
- **When to Use**: Use this sub-structkit when you need to create a Node.js project structure for your application.

#### `project/rust`

- **Description**: Provides a Rust project structure with directories for source code, tests, and configuration files.
- **When to Use**: Use this sub-structkit when you need to create a Rust project structure for your application.

#### `project/python`

- **Description**: Provides a Python project structure with directories for source code, tests, and configuration files.
- **When to Use**: Use this sub-structkit when you need to create a Python project structure for your application.

#### `project/go`

- **Description**: Provides a Go project structure with directories for source code, tests, and configuration files.
- **When to Use**: Use this sub-structkit when you need to create a Go project structure for your application.

#### `project/ruby`

- **Description**: Provides a Ruby project structure with directories for source code, tests, and configuration files.
- **When to Use**: Use this sub-structkit when you need to create a Ruby project structure for your application.

### Terraform

#### `terraform/modules/generic`

- **Description**: Provides a generic Terraform module structure with directories for resources, variables, and outputs.
- **When to Use**: Use this sub-structkit when you need to create a generic Terraform module for your infrastructure.

#### `terraform/apps/generic`

- **Description**: Provides a generic Terraform application structure with directories for modules, environments, and configurations.
- **When to Use**: Use this sub-structkit when you need to create a generic Terraform application for your infrastructure.

#### `terraform/apps/aws-accounts`

- **Description**: Provides a Terraform application structure for managing AWS accounts.
- **When to Use**: Use this sub-structkit when you need to manage AWS accounts using Terraform.

#### `terraform/apps/github-organization`

- **Description**: Provides a Terraform application structure for managing GitHub organizations.
- **When to Use**: Use this sub-structkit when you need to manage GitHub organizations using Terraform.

#### `terraform/apps/environments`

- **Description**: Provides a Terraform application structure for managing environments.
- **When to Use**: Use this sub-structkit when you need to manage environments using Terraform.

#### `terraform/apps/init`

- **Description**: Provides a Terraform application structure for initializing a new project.
- **When to Use**: Use this sub-structkit when you need to initialize a new Terraform project.

---

Each of these sub-structs is designed to simplify the process of setting up specific project structures or configurations. Refer to the individual YAML files for more details on their usage and customization options.
