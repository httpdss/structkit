# Mappings Support

You can provide a mappings YAML file to inject key-value maps into your templates. This is useful for referencing environment-specific values, IDs, or any other mapping you want to use in your generated files.

## What are Mappings?

Mappings are external data files that provide structured key-value pairs for use in your StructKit templates. They allow you to:

- Separate data from templates
- Share common values across multiple structures
- Manage environment-specific configurations
- Centralize reference data like account IDs, team names, or service endpoints

## Mappings File Format

### Basic Structure

```yaml
mappings:
  teams:
    devops: devops-team
    frontend: frontend-team
    backend: backend-team

  aws_account_ids:
    development: 123456789012
    staging: 234567890123
    production: 345678901234

  service_endpoints:
    api_gateway: https://api.example.com
    database: postgres://db.example.com:5432
    redis: redis://cache.example.com:6379
```

### Nested Mappings

```yaml
mappings:
  environments:
    development:
      database_url: postgres://dev-db:5432/myapp
      redis_url: redis://dev-cache:6379
      debug: true

    production:
      database_url: postgres://prod-db:5432/myapp
      redis_url: redis://prod-cache:6379
      debug: false

  regions:
    us_east_1:
      vpc_id: vpc-12345
      subnet_ids:
        - subnet-abc123
        - subnet-def456

    eu_west_1:
      vpc_id: vpc-67890
      subnet_ids:
        - subnet-ghi789
        - subnet-jkl012
```

## Using Mappings in Templates

### Basic Usage

Reference mapping values using the `mappings` variable:

```yaml
files:
  - config.yml:
      content: |
        database_url: {{@ mappings.service_endpoints.database @}}
        api_endpoint: {{@ mappings.service_endpoints.api_gateway @}}

        # Team information
        owner: {{@ mappings.teams.backend @}}
```

### Array Access

For nested structures and arrays:

```yaml
files:
  - terraform/main.tf:
      content: |
        resource "aws_instance" "web" {
          ami           = "ami-12345"
          instance_type = "t3.micro"

          vpc_security_group_ids = [
            "{{@ mappings.regions.us_east_1.vpc_id @}}"
          ]

          subnet_id = "{{@ mappings.regions.us_east_1.subnet_ids[0] @}}"
        }
```

### Dynamic Key Access

Use bracket notation for dynamic keys:

```yaml
files:
  - app.py:
      content: |
        import os

        ENVIRONMENT = "{{@ environment @}}"
        DATABASE_URL = "{{@ mappings.environments[environment].database_url @}}"
        DEBUG = {{@ mappings.environments[environment].debug @}}

variables:
  - environment:
      description: "Target environment"
      type: string
      default: "development"
```

## Using Mappings in the `with` Clause

You can assign values from mappings directly in the `with` clause for folder structkit calls:

```yaml
folders:
  - ./infrastructure:
      struct: terraform/aws-vpc
      with:
        vpc_id: {{@ mappings.regions.us_east_1.vpc_id @}}
        subnet_ids: {{@ mappings.regions.us_east_1.subnet_ids @}}

  - ./backend:
      struct: project/django
      with:
        team: {{@ mappings.teams.backend @}}
        database_url: {{@ mappings.environments.production.database_url @}}
```

This approach allows you to pass specific mapping values as variables to nested structures.

## Command Line Usage

Use the `--mappings-file` argument with the `generate` command:

```sh
# Both commands work identically - file:// is automatically added for .yaml files
structkit generate --mappings-file ./mymap.yaml my-struct.yaml .
structkit generate --mappings-file ./mymap.yaml file://my-struct.yaml .
```

### Multiple Mappings Files

You can specify multiple mappings files that will be merged in order:

```sh
structkit generate \
  --mappings-file ./common-mappings.yaml \
  --mappings-file ./env-specific-mappings.yaml \
  my-struct.yaml .
```

**Merging behavior:**

- Files are processed in the order specified
- Later files override earlier ones for conflicting keys
- Deep merging is performed for nested dictionaries
- This enables clean separation of common vs environment-specific configuration

**Example with environment variable:**

```sh
structkit generate \
  --mappings-file ./mappings/common.yaml \
  --mappings-file ./mappings/${ENVIRONMENT}.yaml \
  infrastructure.yaml \
  ./output
```

## Practical Examples

### Multi-Environment Deployment

**mappings.yaml:**

```yaml
mappings:
  environments:
    dev:
      namespace: myapp-dev
      replicas: 1
      image_tag: latest
      resources:
        cpu: 100m
        memory: 128Mi

    prod:
      namespace: myapp-prod
      replicas: 3
      image_tag: v1.2.3
      resources:
        cpu: 500m
        memory: 512Mi
```

**k8s-deployment.yaml template:**

```yaml
files:
  - k8s/deployment.yaml:
      content: |
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: {{@ app_name @}}
          namespace: {{@ mappings.environments[target_env].namespace @}}
        spec:
          replicas: {{@ mappings.environments[target_env].replicas @}}
          template:
            spec:
              containers:
              - name: app
                image: myapp:{{@ mappings.environments[target_env].image_tag @}}
                resources:
                  requests:
                    cpu: {{@ mappings.environments[target_env].resources.cpu @}}
                    memory: {{@ mappings.environments[target_env].resources.memory @}}

variables:
  - target_env:
      description: "Target environment (dev/prod)"
      type: string
      default: "dev"
  - app_name:
      description: "Application name"
      type: string
```

### Team-Specific Configurations

**teams.yaml:**

```yaml
mappings:
  teams:
    platform:
      email: platform@company.com
      slack: "#platform-team"
      oncall: platform-oncall@company.com

    data:
      email: data@company.com
      slack: "#data-team"
      oncall: data-oncall@company.com
```

**Usage:**

```yaml
folders:
  - ./services/api:
      struct: service/rest-api
      with:
        team_email: {{@ mappings.teams.platform.email @}}
        team_slack: {{@ mappings.teams.platform.slack @}}

  - ./services/etl:
      struct: service/data-pipeline
      with:
        team_email: {{@ mappings.teams.data.email @}}
        team_slack: {{@ mappings.teams.data.slack @}}
```

## Best Practices

1. **Organize by Context**: Group related mappings together (e.g., environments, teams, regions)

2. **Use Consistent Naming**: Follow naming conventions across all mapping files

3. **Version Control**: Keep mappings files in version control alongside your structures

4. **Validate Data**: Ensure mapping values are correct before generating structures

5. **Document Mappings**: Include comments or separate documentation for complex mappings

6. **Environment Separation**: Use separate mapping files for different environments

7. **Default Values**: Provide sensible defaults in your templates for missing mappings

## Error Handling

If a mapping key doesn't exist, StructKit will show an error:

```yaml
files:
  - config.yml:
      content: |
        # This will cause an error if 'nonexistent' key doesn't exist
        value: {{@ mappings.nonexistent.key @}}
```

Use the `default` filter to provide fallbacks:

```yaml
files:
  - config.yml:
      content: |
        # This provides a fallback value
        value: {{@ mappings.team.devops | default "no_team" @}}
```
