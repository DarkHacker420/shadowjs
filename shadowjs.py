import requests
from bs4 import BeautifulSoup
import re
from rich.console import Console
from rich.progress import Progress
from rich.prompt import Prompt
from rich.table import Table
import json


def print_logo():
    logo = r"""
 _____  _   _   ___  ______  _____  _    _            ___  _____ 
/  ___|| | | | / _ \ |  _  \|  _  || |  | |          |_  |/  ___|
\ `--. | |_| |/ /_\ \| | | || | | || |  | | ______     | |\ `--. 
 `--. \|  _  ||  _  || | | || | | || |/\| ||______|    | | `--. \
/\__/ /| | | || | | || |/ / \ \_/ /\  /\  /        /\__/ //\__/ /
\____/ \_| |_/\_| |_/|___/   \___/  \/  \/         \____/ \____/ 

        [bold green]SHADOW-JS - JavaScript Endpoint Extractor[/bold green]
    """
    console.print(logo)


# Initialize rich console for styled outputs
console = Console()

def fetch_remote_file(url):
    """Fetch HTML content from a remote URL"""
    try:
        console.print(f"[blue]Fetching HTML content from:[/blue] {url}")
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error fetching URL: {e}[/red]")
        return ""

def fetch_js_content(js_url):
    """Fetch and return the JavaScript content from a URL"""
    try:
        response = requests.get(js_url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error fetching JS file: {e}[/red]")
        return ""

def extract_js_files_from_html(content):
    """Extract JavaScript file URLs from HTML content"""
    soup = BeautifulSoup(content, "html.parser")
    js_files = []

    for script in soup.find_all("script", src=True):
        js_file_url = script["src"]
        js_files.append(js_file_url)

    return js_files

def extract_endpoints_from_js(js_content):
    """Extract endpoints or URLs from JavaScript content"""
    endpoints = []

    # Regex to find common URL patterns (including API or sensitive patterns)
    url_pattern = re.compile(r'(https?://[^\s\'";]+|\/[a-zA-Z0-9/_\-\.]+)')
    matches = url_pattern.findall(js_content)

    # Extract "juice" endpoints (e.g., API paths or secrets)
    juice_pattern = re.compile(r'\/(api|v1|secrets?|auth|login|user|admin|config|configurations)[^\s\'";]*')
    juice_matches = juice_pattern.findall(js_content)

    # Combine general and juice endpoints
    endpoints.extend(matches)
    endpoints.extend(juice_matches)

    # Deduplicate and return found endpoints
    endpoints = list(set(endpoints))
    return endpoints

def check_secrets_against_patterns(js_content, secrets):
    """Check the content against the patterns defined in the secrets file"""
    matched_secrets = []
    
    # Iterate over the secrets and patterns
    for secret in secrets:
        name = secret["name"]
        patterns = secret["patterns"]
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content)
            
            # Flatten the matches to ensure each match is a string
            if matches:
                matched_secrets.append({
                    "name": name,
                    "pattern": pattern,
                    "matches": [str(match) for match in matches]  # Ensure each match is a string
                })
    
    return matched_secrets

def display_results_as_table(js_endpoints, matched_secrets):
    """Display JavaScript endpoints and secrets in tables"""
    # Display JavaScript Endpoints Table
    if js_endpoints:
        js_table = Table(title="Extracted JavaScript Endpoints")
        js_table.add_column("Index", style="cyan", justify="center")
        js_table.add_column("URL/Path", style="magenta", justify="left")
        
        for idx, endpoint in enumerate(js_endpoints, start=1):
            js_table.add_row(str(idx), endpoint)
        
        console.print(js_table)
    else:
        console.print("[yellow]No JavaScript endpoints found.[/yellow]")

    # Display Secrets Table
    if matched_secrets:
        secrets_table = Table(title="Matched Secrets")
        secrets_table.add_column("Index", style="cyan", justify="center")
        secrets_table.add_column("Secret Name", style="magenta", justify="left")
        secrets_table.add_column("Pattern", style="green", justify="left")
        secrets_table.add_column("Matches", style="yellow", justify="left")
        
        for idx, secret in enumerate(matched_secrets, start=1):
            matches = ', '.join(secret["matches"])  # This should now work without issues
            secrets_table.add_row(str(idx), secret["name"], secret["pattern"], matches)
        
        console.print(secrets_table)
    else:
        console.print("[yellow]No secrets matched.[/yellow]")

def save_results_to_file(results, file_path):
    """Save extracted results to a file"""
    try:
        with open(file_path, "w") as file:
            for result in results:
                file.write(result + "\n")
        console.print(f"[green]Results saved to {file_path}[/green]")  
    except Exception as e:
        console.print(f"[red]Error saving file: {e}[/red]")

def process_js_files(js_files, secrets, output_file=None):
    """Process a list of JavaScript files"""
    with Progress() as progress:
        task = progress.add_task("[green]Processing JavaScript files...", total=len(js_files))
        all_endpoints = []
        all_matched_secrets = []

        for js_file in js_files:
            progress.update(task, description=f"[blue]Fetching {js_file}[/blue]")
            js_content = fetch_js_content(js_file)

            progress.update(task, description=f"[green]Extracting endpoints from {js_file}...[/green]")
            endpoints = extract_endpoints_from_js(js_content)
            all_endpoints.extend(endpoints)

            if secrets:  # Only check secrets if a secrets file was provided
                progress.update(task, description=f"[yellow]Checking for secrets in {js_file}...[/yellow]")
                matched_secrets = check_secrets_against_patterns(js_content, secrets)
                all_matched_secrets.extend(matched_secrets)

            progress.advance(task)

    # Display results in table format
    display_results_as_table(all_endpoints, all_matched_secrets)

    # Save results to file if specified
    if output_file:
        save_results_to_file(all_endpoints, output_file)
    else:
        save_option = Prompt.ask("[cyan]Would you like to save the results to a file? (yes/no)[/cyan]", default="no")
        if save_option.lower() == "yes":
            output_file = Prompt.ask("[cyan]Enter the output file path[/cyan]", default="results.txt")
            save_results_to_file(all_endpoints, output_file)

def main():
    print_logo()
    import argparse
    parser = argparse.ArgumentParser(description="Extract JavaScript endpoints and secrets from a URL or list of URLs.")
    parser.add_argument("-u", "--url", help="URL to fetch JavaScript from", type=str)
    parser.add_argument("-f", "--file", help="Path to a text file containing JavaScript URLs", type=str)
    parser.add_argument("-o", "--output", help="File to save the extracted results", type=str)
    parser.add_argument("-s", "--secrets", help="Path to secrets JSON file", type=str)

    args = parser.parse_args()
    # print_logo()

    if not args.url and not args.file:
        console.print("[red]Error: You must specify a URL or a file with --url or --file.[/red]")
        parser.print_help()
        return

    # Load secrets.json if provided
    secrets = []
    if args.secrets:
        try:
            with open(args.secrets, "r") as secrets_file:
                secrets = json.load(secrets_file)
                console.print(f"[green]Secrets loaded from {args.secrets}[/green]")
        except Exception as e:
            console.print(f"[red]Error loading secrets file: {e}[/red]")
            return

    # Process a single JavaScript file if URL is provided
    if args.url:
        if args.url.endswith(".js"):
            js_files = [args.url]
        else:
            # Fetch HTML content from the provided page URL
            html_content = fetch_remote_file(args.url)

            # Extract JavaScript file URLs
            js_files = extract_js_files_from_html(html_content)

    # Process a list of JavaScript files if a file is provided
    elif args.file:
        js_files = []
        try:
            with open(args.file, "r") as file:
                js_files = [line.strip() for line in file.readlines()]
                console.print(f"[green]URLs loaded from {args.file}[/green]")
        except Exception as e:
            console.print(f"[red]Error loading file: {e}[/red]")
            return

    # Process the list of JavaScript files
    process_js_files(js_files, secrets, args.output)

if __name__ == "__main__":
    main()
