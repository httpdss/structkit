import yaml
import os
import subprocess


def read_config_file(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def merge_configs(file_config, args):
    args_dict = vars(args)
    for key, value in file_config.items():
        if key in args_dict and args_dict[key] is None:
            args_dict[key] = value
    return args_dict


def get_current_repo():
    try:
        # Get the remote URL
        remote_url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url'], text=True).strip()

        # Handle different remote URL formats (HTTPS and SSH)
        if remote_url.startswith("https://"):
            # Extract "owner/repository" from HTTPS URL
            owner_repo = remote_url.split("github.com/")[1].replace(".git", "")
        elif remote_url.startswith("git@"):
            # Extract "owner/repository" from SSH URL
            owner_repo = remote_url.split(":")[1].replace(".git", "")
        else:
            return "Error: Not a GitHub repository"

        return owner_repo
    except subprocess.CalledProcessError:
        return "Error: Not a Git repository or no remote URL set"


project_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
