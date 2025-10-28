from structkit.commands import Command
import os

SUPPORTED_SHELLS = ["bash", "zsh", "fish"]


class CompletionCommand(Command):
  def __init__(self, parser):
    super().__init__(parser)
    parser.description = "Manage CLI shell completions for structkit (shtab-generated)"
    sub = parser.add_subparsers(dest="action")

    install = sub.add_parser("install", help="Print the commands to enable completion for your shell")
    install.add_argument("shell", nargs="?", choices=SUPPORTED_SHELLS, help="Shell type (auto-detected if omitted)")
    install.set_defaults(func=self._install)

  def _detect_shell(self):
    shell = os.environ.get("SHELL", "")
    if shell:
      basename = os.path.basename(shell)
      if basename in SUPPORTED_SHELLS:
        return basename
    # Fallback to zsh if running zsh, else bash
    if os.environ.get("ZSH_NAME") or os.environ.get("ZDOTDIR"):
      return "zsh"
    return "bash"

  def _install(self, args):
    shell = args.shell or self._detect_shell()
    print(f"Detected shell: {shell}")

    if shell == "bash":
      print("\n# Install shtab (once, in your environment):")
      print("python -m pip install shtab")
      print("\n# Generate static bash completion for 'struct':")
      print("mkdir -p ~/.local/share/bash-completion/completions")
      print("structkit --print-completion bash > ~/.local/share/bash-completion/completions/structkit")
      print("\n# Apply now (or open a new shell):")
      print("source ~/.bashrc")

    elif shell == "zsh":
      print("\n# Install shtab (once, in your environment):")
      print("python -m pip install shtab")
      print("\n# Generate static zsh completion for 'struct':")
      print("mkdir -p ~/.zfunc")
      print("structkit --print-completion zsh > ~/.zfunc/_structkit")
      print("\n# Ensure zsh loads user functions/completions (append to ~/.zshrc if needed):")
      print('echo "fpath=(~/.zfunc $fpath)" >> ~/.zshrc')
      print('echo "autoload -U compinit && compinit" >> ~/.zshrc')
      print("\n# Apply now (or open a new shell):")
      print("exec zsh")

    elif shell == "fish":
      print("\n# Install shtab (once, in your environment):")
      print("python -m pip install shtab")
      print("\n# Generate static fish completion for 'struct':")
      print('mkdir -p ~/.config/fish/completions')
      print('structkit --print-completion fish > ~/.config/fish/completions/structkit.fish')
      print("\n# Apply now:")
      print("fish -c 'source ~/.config/fish/completions/structkit.fish'")

    else:
      self.logger.error(f"Unsupported shell: {shell}. Supported: {', '.join(SUPPORTED_SHELLS)}")
      return

    print("\nTip: You can also print completion directly via: structkit --print-completion <shell>")
