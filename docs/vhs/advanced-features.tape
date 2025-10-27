Output docs/vhs/advanced-features.gif

Set Theme "Monokai Vivid"
Set FontSize 14
Set TypingSpeed 40ms
Set Width 1400
Set Height 800
Set Shell "bash"

Type "# StructKit Advanced Features Demo"
Enter
Sleep 1s

Type "# Generate schema for VSCode autocompletion"
Enter
Type "mkdir -p .vscode"
Enter
Type "structkit generate-schema --output .vscode/struct-schema.json"
Enter
Sleep 2s

Type "# Show the generated schema"
Enter
Type "cat .vscode/struct-schema.json"
Enter
Sleep 3s

Type "# Create config with remote content"
Enter
Type "cat > remote-demo.yaml << EOF"
Enter
Type "files:"
Enter
Type "  - LICENSE:"
Enter
Type "      file: https://raw.githubusercontent.com/licenses/license-templates/master/templates/mit.txt"
Enter
Type "  - .gitignore:"
Enter
Type "      file: https://raw.githubusercontent.com/github/gitignore/refs/heads/main/Python.gitignore"
Enter
Type "EOF"
Enter
Sleep 2s

Type "# Generate with remote content"
Enter
Type "structkit generate remote-demo.yaml ./remote-project"
Enter
Sleep 3s

Type "# Check what was downloaded"
Enter
Type "ls -la remote-project/"
Enter
Sleep 2s

Type "# Advanced features make StructKit incredibly powerful!"
Enter
Sleep 2s
