#!/bin/bash

# Sentiment and Stance Analysis API Startup Script
# Simple wrapper around the Python startup script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
MODE="dev"
HOST="0.0.0.0"
PORT="8000"
WORKERS="4"
LOG_LEVEL="info"
INSTALL_DEPS=false
FORCE_DEPS=false
CHECK_ONLY=false
NO_RELOAD=false

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Sentiment and Stance Analysis API Startup Script

OPTIONS:
    --mode MODE           Server mode: dev (development) or prod (production) [default: dev]
    --host HOST           Host to bind to [default: 0.0.0.0]
    --port PORT           Port to bind to [default: 8000]
    --workers NUM         Number of workers for production mode [default: 4]
    --log-level LEVEL     Log level: debug, info, warning, error [default: info]
    --install-deps        Install/update dependencies before starting
    --force-deps          Force reinstall all dependencies
    --check-only          Only perform checks, don't start server
    --no-reload           Disable auto-reload in development mode
    -h, --help            Show this help message

EXAMPLES:
    # Start development server with default settings
    $0

    # Start development server on custom port
    $0 --port 8080

    # Start production server with 8 workers
    $0 --mode prod --workers 8

    # Install dependencies and start
    $0 --install-deps

    # Check environment without starting
    $0 --check-only

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --workers)
            WORKERS="$2"
            shift 2
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        --install-deps)
            INSTALL_DEPS=true
            shift
            ;;
        --force-deps)
            FORCE_DEPS=true
            shift
            ;;
        --check-only)
            CHECK_ONLY=true
            shift
            ;;
        --no-reload)
            NO_RELOAD=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Print banner
echo ""
echo "=========================================="
echo "  Sentiment & Stance Analysis API"
echo "=========================================="
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

print_info "Python found: $(python3 --version)"

# Build command
CMD="python3 scripts/start.py --mode $MODE --host $HOST --port $PORT --log-level $LOG_LEVEL"

if [ "$MODE" = "prod" ]; then
    CMD="$CMD --workers $WORKERS"
fi

if [ "$INSTALL_DEPS" = true ]; then
    CMD="$CMD --install-deps"
fi

if [ "$FORCE_DEPS" = true ]; then
    CMD="$CMD --force-deps"
fi

if [ "$CHECK_ONLY" = true ]; then
    CMD="$CMD --check-only"
fi

if [ "$NO_RELOAD" = true ]; then
    CMD="$CMD --no-reload"
fi

# Execute the Python startup script
print_info "Executing: $CMD"
echo ""

exec $CMD