Output docs/vhs/remote-content.gif

Set Theme "Monokai Vivid"
Set FontSize 14
Set TypingSpeed 40ms
Set Width 1400
Set Height 800
Set Shell "bash"

Type "# StructKit Remote Content Demo"
Enter
Sleep 1s

Type "# Create configuration with remote files"
Enter
Type "cat > remote-example.yaml << EOF"
Enter
Type "files:"
Enter
Type "  - .gitignore:"
Enter
Type "      file: https://raw.githubusercontent.com/github/gitignore/refs/heads/main/Python.gitignore"
Enter
Type "  - LICENSE:"
Enter
Type "      file: https://raw.githubusercontent.com/licenses/license-templates/master/templates/mit.txt"
Enter
Type "  - README.md:"
Enter
Type "      content: |"
Enter
Type "        # Remote Content Demo"
Enter
Type "        This project uses remote content from various sources."
Enter
Type "EOF"
Enter
Sleep 2s

Type "# Generate project with remote content"
Enter
Type "structkit generate remote-example.yaml ./remote-demo"
Enter
Sleep 4s

Type "# Check downloaded files"
Enter
Type "ls -la remote-demo/"
Enter
Sleep 2s

Type "# View the .gitignore from GitHub"
Enter
Type "head -10 remote-demo/.gitignore"
Enter
Sleep 2s

Type "# View the LICENSE file"
Enter
Type "head -5 remote-demo/LICENSE"
Enter
Sleep 2s

Type "# Remote content makes reusing existing resources easy!"
Enter
Sleep 2s
