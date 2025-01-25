# JavaScript Endpoint Extractor

A Python tool to extract endpoints (e.g., API paths) and sensitive information (like secrets or configurations) from JavaScript files. It supports extracting endpoints from single URLs, web pages, or a list of JavaScript URLs in a `.txt` file.

---

## Features

- Extract JavaScript file URLs from HTML pages.
- Process individual JavaScript files or lists of URLs from a `.txt` file.
- Extract sensitive endpoints like `/api/v1`, `/secrets`, `/auth`, etc., using regex.
- Optionally match JavaScript content against secret patterns (via a JSON file).
- Save results to a file for further analysis.

---

## Requirements

- Python 3.7 or higher

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/js-endpoint-extractor.git
   cd js-endpoint-extractor
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Create a `secrets.json` file to define custom patterns for sensitive information (example below).

---

## Usage

### 1. Single JavaScript URL
To extract endpoints from a single JavaScript file:
```bash
python script.py --url "https://example.com/assets/js/main.js"
```

### 2. HTML Page with JavaScript References
To process all JavaScript files linked in an HTML page:
```bash
python script.py --url "https://example.com"
```

### 3. List of JavaScript URLs from a `.txt` File
To extract endpoints from multiple JavaScript files listed in a `.txt` file:
```bash
python script.py --file urls.txt
```

### 4. Match Secrets (Optional)
To match JavaScript content against predefined patterns for secrets:
```bash
python script.py --url "https://example.com/assets/js/main.js" --secrets secrets.json
```

### 5. Save Results to a File
To save the extracted endpoints and secrets to a file:
```bash
python script.py --url "https://example.com" --output results.txt
```

---

## Examples

### Extract from a Single URL:
```bash
python script.py --url "https://example.com/assets/js/main.js"
```

### Extract from a List of URLs:
Prepare a file named `urls.txt` with JavaScript URLs, one per line:
```
https://example.com/assets/js/main.js
https://example.com/scripts/app.js
```
Then run:
```bash
python script.py --file urls.txt
```

### Extract with Secrets Matching:
1. Define your `secrets.json` file:
    ```json
    [
        {
            "name": "API Key",
            "patterns": ["API_KEY=[A-Za-z0-9]+", "api_key='[A-Za-z0-9]+'"]
        },
        {
            "name": "Authorization Token",
            "patterns": ["Bearer [A-Za-z0-9._-]+"]
        }
    ]
    ```

2. Run the script:
    ```bash
    python script.py --url "https://example.com/assets/js/main.js" --secrets secrets.json
    ```

---

## Output

The script displays the extracted endpoints and secrets in a table format in the terminal. Optionally, it can save the results to a file:
- Extracted endpoints (e.g., `/api/v1` or `https://example.com/api/login`)
- Matched secrets (e.g., `API_KEY` or `Bearer token`)

---

## Secrets JSON Example

Here’s an example of a `secrets.json` file that can be used to find sensitive patterns in JavaScript:
```json
[
    {
        "name": "API Key",
        "patterns": ["API_KEY=[A-Za-z0-9]+", "apiKey='[A-Za-z0-9]+'"]
    },
    {
        "name": "JWT Token",
        "patterns": ["Bearer [A-Za-z0-9._-]+"]
    },
    {
        "name": "AWS Access Key",
        "patterns": ["AKIA[0-9A-Z]{16}"]
    }
]
```

---

## Requirements File

Include this in `requirements.txt` to ensure all dependencies are installed:
```
beautifulsoup4==4.12.2
requests==2.31.0
rich==13.5.1
```

---

## Contributing

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/new-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add new feature"
   ```
4. Push the branch:
   ```bash
   git push origin feature/new-feature
   ```
5. Open a pull request on GitHub.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

