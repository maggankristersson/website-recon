import os
import sys
import subprocess
import argparse
from shutil import which

# Define colors for terminal output
RED = "\033[1;31m"
GREEN = "\033[1;32m"
RESET = "\033[0m"

def check_tool_installed(tool):
    """Check if a tool is installed."""
    if which(tool) is None:
        print(f"{RED}Error: {tool} is not installed.{RESET}")
        sys.exit(1)

def create_directory(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"{GREEN}Created directory: {path}{RESET}")

def run_command(command, description):
    """Run a shell command with error checking."""
    print(f"{RED} [+] {description} ... {RESET}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"{RED}Error: Failed to {description}{RESET}")
        sys.exit(1)

def main(domain):
    # Define base recon directory
    base_recon_dir = "recon"
    create_directory(base_recon_dir)

    # Define subdirectories
    base_dir = os.path.join(base_recon_dir, domain)
    info_path = os.path.join(base_dir, "info")
    subdomain_path = os.path.join(base_dir, "subdomains")
    screenshot_path = os.path.join(base_dir, "screenshots")

    # Create directories if they don't exist
    for path in [info_path, subdomain_path, screenshot_path]:
        create_directory(path)

    # Run the commands with error checking
    run_command(f"whois {domain} > {info_path}/whois.txt", "check whois information")
    run_command(f"subfinder -d {domain} > {subdomain_path}/found.txt", "launch subfinder")
    run_command(f"assetfinder {domain} | grep {domain} >> {subdomain_path}/found.txt", "run assetfinder")
    run_command(f"cat {subdomain_path}/found.txt | grep {domain} | sort -u | httprobe -prefer-https | grep https | sed 's/https\\?:\\/\\///' | tee -a {subdomain_path}/alive.txt", "check what's alive")
    run_command(f"gowitness file -f {subdomain_path}/alive.txt -P {screenshot_path}/ --no-http", "take screenshots")

if __name__ == "__main__":
    # Check if the required tools are installed
    for tool in ["whois", "subfinder", "assetfinder", "httprobe", "gowitness"]:
        check_tool_installed(tool)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Domain Reconnaissance Script")
    parser.add_argument("domain", help="Domain to perform reconnaissance on")
    args = parser.parse_args()

    main(args.domain)

