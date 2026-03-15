# terminal-search

**terminal-search** is a lightweight, pure-Python terminal-based search/research tool powered by the Grok API (xAI).

It is designed to be used **locally** (no pip installation required), runs with only the standard library + `requests`, and offers:

- streaming responses with typewriter animation
- colored output (prompt, headers, links, headings)
- multiple modes (default / think / concise / code)
- easy model switching
- clean CLI interface

Current version: 1.3 (enhanced colors & styling)


## Local installation (no pip)

1. **Clone or download** the project

   ```bash
   # Option A — git (recommended)
   git clone <your-repo-url> terminal-search
   cd terminal-search

   # Option B — just copy the file
   # Create folder and put terminal-search.py inside
   mkdir terminal-search && cd terminal-search
   # ... paste your script as terminal-search.py

   
## Make the script executable (if using single-file style)
   chmod +x terminal-search.py
   
## Set your API key (only once per session or add to shell profile)
   export XAI_API_KEY="xai-........................................"

   You can also add this line permanently to your ~/.zshrc / ~/.bashrc:Bash

   export XAI_API_KEY="xai-your-key-here"

   ## Run it (choose your preferred style)Single-file style

   ./terminal-search.py "what is the current status of Starship flight tests?"

   ## Package style (recommended for cleaner -m usage)Bash

   # From the parent directory (where terminal_search/ folder is)
      python3 -m terminal_search "explain black holes like I'm 12"

# or with mode
python3 -m terminal_search -m think "realistic AGI timeline 2026-2030"

## Global shortcut (optional — very convenient)Bash

# Create symlink (best option)
ln -s "$(pwd)/terminal-search.py" ~/bin/terminal-search
# or if using package style:
ln -s "$(pwd)/terminal_search/main.py" ~/bin/terminal-search

chmod +x ~/bin/terminal-search

# Make sure ~/bin is in PATH (add to ~/.zshrc if needed)
export PATH="$HOME/bin:$PATH"

## Basic Usages

terminal-search "latest Grok-4 news"
terminal-search -m code "fastapi + sqlalchemy async auth example"

## Usage examples

# Basic search
terminal-search "why did Python 3.14 remove the GIL rumors?"

# Deep reasoning mode
terminal-search -m think "will open-source models catch closed frontier models by 2028?"

# Concise answers
terminal-search -m concise "current Grok API available models March 2026"

# Code mode
terminal-search -m code -n 1200 "python asyncio + httpx retry client with exponential backoff"

# Show configured modes
terminal-search -s
# or
terminal-search -m list
