#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Function to print step info
print_step() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Required tools
TOOLS="ruff black nbqa isort autoflake"

print_header "Checking required tools"
# Check for required tools
for cmd in $TOOLS; do
    if ! command_exists "$cmd"; then
        echo -e "${RED}Error: $cmd is not installed. Installing required tools...${NC}"
        pip install $TOOLS
        break
    fi
done

print_header "Cleaning Python cache files"
# Remove Python cache files
find . -type f -name "*.py[co]" -delete
find . -type d -name "__pycache__" -delete
find . -type d -name ".pytest_cache" -delete
find . -type d -name ".ruff_cache" -delete

print_header "Running code cleaners and formatters"

print_step "Running autoflake to remove unused imports and variables"
# Remove unused imports and variables
autoflake --in-place --recursive --remove-all-unused-imports --remove-unused-variables --expand-star-imports .
nbqa autoflake . --in-place --remove-all-unused-imports --remove-unused-variables --expand-star-imports

print_step "Running isort to sort imports"
# Sort imports
isort .
nbqa isort .

print_step "Running Black formatter"
# Format code
black --config pyproject.toml .
nbqa black .

print_step "Running Ruff auto-fixes"
# Run Ruff fixes
ruff check . --fix --extend-select ALL
nbqa ruff . --fix --extend-select ALL

print_header "Running final checks"

print_step "Final Ruff check"
# Final linting check
ruff check . --extend-select ALL

# Create pyproject.toml if it doesn't exist
if [ ! -f "pyproject.toml" ]; then
    print_header "Creating pyproject.toml with recommended settings"
    cat > pyproject.toml << EOL
[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.ruff]
line-length = 88
target-version = "py39"
select = ["ALL"]
ignore = ["D203", "D212"]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]

[tool.ruff.mccabe]
max-complexity = 10

[tool.ruff.pydocstyle]
convention = "google"

[tool.ruff.pylint]
max-args = 5
max-statements = 50
EOL
fi

# Check if any of the commands failed
if [ $? -eq 0 ]; then
    print_header "✨ All formatting and linting completed successfully!"
    echo -e "${GREEN}Your code is now clean and formatted!${NC}"
    exit 0
else
    print_header "❌ Some issues could not be auto-fixed"
    echo -e "${RED}Please review the output above and fix remaining issues manually.${NC}"
    exit 1
fi