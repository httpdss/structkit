Output docs/vhs/usage.gif

Set Theme "Dracula"
Set FontSize 14
Set Width 1200
Set Height 600
Set Shell "bash"

Type "# StructKit - Basic Usage Demo"
Enter
Sleep 1s

Type "# First, let's see what structures are available"
Enter
Sleep 500ms

Type "structkit list"
Enter
Sleep 2s

Type "# Let's generate a simple Python project"
Enter
Sleep 500ms

Type "structkit generate project/python ./my-python-app"
Enter
Sleep 3s

Type "# Check what was created"
Enter
Sleep 500ms

Type "ls -la my-python-app/"
Enter
Sleep 2s

Type "# View the project structure"
Enter
Sleep 500ms

Type "tree my-python-app/ || find my-python-app/ -type f"
Enter
Sleep 2s

Type "# That's it! StructKit made it easy to bootstrap a project"
Enter
Sleep 1s
