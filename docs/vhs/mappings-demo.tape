Output docs/vhs/mappings-demo.gif

Set Theme "Monokai Vivid"
Set FontSize 14
Set TypingSpeed 40ms
Set Width 1400
Set Height 800
Set Shell "bash"

Type "# StructKit Mappings Demo"
Enter
Sleep 1s

Type "# Create a simple mapping file with team data"
Enter
Type "cat > team-mapping.yaml << EOF"
Enter
Type "mappings:"
Enter
Type "  team_info:"
Enter
Type "    backend:"
Enter
Type '      lead: "Alice Johnson"'
Enter
Type '      tech_stack: ["Python", "FastAPI", "PostgreSQL"]'
Enter
Type '      repo: "https://github.com/company/backend"'
Enter
Type "EOF"
Enter
Sleep 2s

Type "# Create structure using mapping data"
Enter
Type "cat > project-with-mapping.yaml << EOF"
Enter
Type "mappings:"
Enter
Type "  - team-mapping.yaml"
Enter
Type "files:"
Enter
Type "  - README.md:"
Enter
Type "      content: |"
Enter
Type "        # Backend Team Project"
Enter
Type "        Team Lead: Alice Johnson"
Enter
Type "        Tech Stack: Python, FastAPI, PostgreSQL"
Enter
Type "EOF"
Enter
Sleep 2s

Type "# Generate project for backend team"
Enter
Type "structkit generate project-with-mapping.yaml ./backend-project"
Enter
Sleep 3s

Type "# Check the generated README"
Enter
Type "cat backend-project/README.md"
Enter
Sleep 2s

Type "# Mappings enable data-driven project generation!"
Enter
Sleep 2s
