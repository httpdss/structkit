Output docs/vhs/multiple-mappings.gif

Set Theme "Monokai Vivid"
Set FontSize 14
Set TypingSpeed 40ms
Set Width 1400
Set Height 800
Set Shell "bash"

Type "# StructKit Multiple Mappings Demo"
Enter
Sleep 1s

Type "# Create company info mapping"
Enter
Type "cat > company-info.yaml << EOF"
Enter
Type "mappings:"
Enter
Type "  company:"
Enter
Type '    name: "TechCorp Inc"'
Enter
Type '    website: "https://techcorp.com"'
Enter
Type '    license: "MIT"'
Enter
Type "EOF"
Enter
Sleep 1s

Type "# Create environment mapping"
Enter
Type "cat > environments.yaml << EOF"
Enter
Type "mappings:"
Enter
Type "  environments:"
Enter
Type "    development:"
Enter
Type '      domain: "dev.techcorp.com"'
Enter
Type '      database: "postgres://dev-db:5432/app"'
Enter
Type "    production:"
Enter
Type '      domain: "techcorp.com"'
Enter
Type '      database: "postgres://prod-db:5432/app"'
Enter
Type "EOF"
Enter
Sleep 1s

Type "# Create project using multiple mappings"
Enter
Type "cat > multi-mapping-project.yaml << EOF"
Enter
Type "mappings:"
Enter
Type "  - company-info.yaml"
Enter
Type "  - environments.yaml"
Enter
Type "files:"
Enter
Type "  - config/app.yaml:"
Enter
Type "      content: |"
Enter
Type "        app:"
Enter
Type "          name: MyApp"
Enter
Type "          company: TechCorp Inc"
Enter
Type "          website: https://techcorp.com"
Enter
Type "        environment:"
Enter
Type "          domain: dev.techcorp.com"
Enter
Type "          database: postgres://dev-db:5432/app"
Enter
Type "EOF"
Enter
Sleep 2s

Type "# Generate for development environment"
Enter
Type "structkit generate multi-mapping-project.yaml ./dev-app"
Enter
Sleep 3s

Type "# View the generated config"
Enter
Type "cat dev-app/config/app.yaml"
Enter
Sleep 2s

Type "# Multiple mappings provide powerful data composition!"
Enter
Sleep 2s
