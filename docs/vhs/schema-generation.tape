Output docs/vhs/schema-generation.gif

Set Theme "Monokai Vivid"
Set FontSize 14
Set TypingSpeed 40ms
Set Width 1400
Set Height 800
Set Shell "bash"

Type "# StructKit Schema Generation Demo"
Enter
Sleep 1s

Type "# Generate JSON schema for VSCode autocompletion"
Enter
Type "structkit generate-schema"
Enter
Sleep 3s

Type "# Save schema to a file for VSCode"
Enter
Type "mkdir -p .vscode"
Enter
Type "structkit generate-schema --output .vscode/struct-plugins.schema.json"
Enter
Sleep 2s

Type "# View the generated schema"
Enter
Type "cat .vscode/struct-plugins.schema.json"
Enter
Sleep 3s

Type "# Create VSCode settings to use the schema"
Enter
Type "cat > .vscode/settings.json << EOF"
Enter
Type "{"
Enter
Type '  "yaml.schemas": {'
Enter
Type '    "./.vscode/struct-plugins.schema.json": "*.struct.yaml"'
Enter
Type "  }"
Enter
Type "}"
Enter
Type "EOF"
Enter
Sleep 2s

Type "# Now VSCode will provide autocompletion for structkit names!"
Enter
Type "# when you type 'struct:' in a .struct.yaml file"
Enter
Sleep 2s

Type "# Schema generation enables better IDE support!"
Enter
Sleep 2s
