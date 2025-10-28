Output docs/vhs/yaml-config.gif

Set Theme "Monokai Vivid"
Set FontSize 14
Set TypingSpeed 40ms
Set Width 1400
Set Height 800
Set Shell "bash"

Type "# StructKit YAML Configuration Demo"
Enter
Sleep 1s

Type "# Create a simple project structure configuration"
Enter
Type "cat > my-project.yaml << EOF"
Enter
Type "files:"
Enter
Type "  - README.md:"
Enter
Type "      content: |"
Enter
Type "        # My Project"
Enter
Type "        Generated with StructKit"
Enter
Type "  - .gitignore:"
Enter
Type "      file: https://raw.githubusercontent.com/github/gitignore/refs/heads/main/Python.gitignore"
Enter
Type "EOF"
Enter
Sleep 3s

Type "# Validate the configuration"
Enter
Type "structkit validate my-project.yaml"
Enter
Sleep 2s

Type "# Generate the project"
Enter
Type "structkit generate my-project.yaml ./my-custom-project"
Enter
Sleep 3s

Type "# Check the generated structure"
Enter
Type "ls -la my-custom-project/"
Enter
Sleep 2s

Type "cat my-custom-project/README.md"
Enter
Sleep 2s

Type "# YAML configuration makes StructKit highly flexible!"
Enter
Sleep 2s
Sleep 2s

Type "# YAML configuration makes StructKit highly flexible!" Enter
Sleep 2s
