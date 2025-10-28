
Output docs/vhs/install.gif

Set Theme "Monokai Vivid"
Set FontSize 14
Set TypingSpeed 40ms
Set Width 1400
Set Height 800
Set Shell "bash"

Type "# StructKit Installation Demo"
Enter
Sleep 1s

Type "# Create python virtual environment and install struct"
Enter
Type "python3 -m venv .venv"
Enter
Sleep 2s

Type "source .venv/bin/activate"
Enter
Sleep 1s

Type "# Install StructKit"
Enter
Type "pip install structkit"
Enter
Sleep 5s

Type "# Verify installation"
Enter
Type "structkit --help"
Enter
Sleep 2s

Type "# Check available structures"
Enter
Type "structkit list"
Enter
Sleep 3s

Type "# StructKit is now installed and ready to use!"
Enter
Sleep 2s
