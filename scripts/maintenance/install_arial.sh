#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-11 11:30:00 (ywatanabe)"
# File: ./scripts/maintenance/install_arial.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

GRAY='\033[0;90m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
echo_header() { echo_info "=== $1 ==="; }
# ---------------------------------------

echo_header "Installing Arial font"

# Detect package manager and install Microsoft core fonts
if command -v apt-get &>/dev/null; then
    echo_info "Detected Debian/Ubuntu system"
    echo_info "Installing ttf-mscorefonts-installer..."
    sudo apt-get update 2>&1 | tee -a "$LOG_PATH"
    echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | sudo debconf-set-selections
    sudo apt-get install -y ttf-mscorefonts-installer 2>&1 | tee -a "$LOG_PATH"
elif command -v dnf &>/dev/null; then
    echo_info "Detected Fedora/RHEL system"
    sudo dnf install -y curl cabextract xorg-x11-font-utils fontconfig 2>&1 | tee -a "$LOG_PATH"
    sudo rpm -i https://downloads.sourceforge.net/project/mscorefonts2/rpms/msttcore-fonts-installer-2.6-1.noarch.rpm 2>&1 | tee -a "$LOG_PATH" || true
elif command -v pacman &>/dev/null; then
    echo_info "Detected Arch Linux system"
    echo_info "Installing ttf-ms-fonts from AUR..."
    if command -v yay &>/dev/null; then
        yay -S --noconfirm ttf-ms-fonts 2>&1 | tee -a "$LOG_PATH"
    elif command -v paru &>/dev/null; then
        paru -S --noconfirm ttf-ms-fonts 2>&1 | tee -a "$LOG_PATH"
    else
        echo_error "Please install ttf-ms-fonts from AUR manually"
        exit 1
    fi
else
    echo_error "Unsupported package manager. Please install Microsoft core fonts manually."
    exit 1
fi

# Rebuild font cache
echo_info "Rebuilding font cache..."
fc-cache -fv 2>&1 | tee -a "$LOG_PATH"

# Clear matplotlib font cache
echo_info "Clearing matplotlib font cache..."
python3 -c "
import matplotlib
import shutil
import os
cache_dir = matplotlib.get_cachedir()
font_cache = os.path.join(cache_dir, 'fontlist-v*.json')
import glob
for f in glob.glob(font_cache):
    os.remove(f)
    print(f'Removed: {f}')
print('Matplotlib font cache cleared')
" 2>/dev/null || echo_warning "Could not clear matplotlib cache (matplotlib may not be installed)"

# Verify installation
echo_info "Verifying Arial installation..."
if fc-list | grep -i "arial" &>/dev/null; then
    echo_success "Arial font installed successfully!"
    fc-list | grep -i "arial" | head -3
else
    echo_error "Arial font not found in font cache"
    exit 1
fi

echo_success "Done! Arial font is now available for matplotlib."

# EOF
