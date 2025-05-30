#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

header() {
    clear
    echo -e "${BLUE}"
    echo '
    dMMMMb  .aMMMb  dMP dMP dMP dMP dMMMMb 
   dMP VMP dMP"dMP dMK.dMP dMP dMP dMP"dMP 
  dMP dMP dMP dMP .dMMMK" dMP dMP dMMMMK"  
 dMP.aMP dMP.aMP dMP"AMF dMP.aMP dMP.aMF   
dMMMMP"  VMMMP" dMP dMP  VMMMP" dMMMMP" 
'
    echo -e "${YELLOW}=== DoxUB Installer ===${NC}"
    echo -e "${BLUE}GitHub: solorblaze/DoxUB_I${NC}"
    echo ""
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Error: Command '$1' not found${NC}"
        return 1
    fi
    return 0
}

install_pyrogram() {
    echo -e "${YELLOW}[*] Installing Pyrogram...${NC}"
    pip3 install pyrogram --break-system-packages
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install Pyrogram${NC}"
        exit 1
    fi
    echo -e "${GREEN}[+] Pyrogram installed successfully${NC}"
}

install_dependencies() {
    echo -e "${YELLOW}[*] Checking dependencies...${NC}"
    
    if ! check_command python3; then
        echo -e "${RED}Python3 not installed. Please install Python3 and try again.${NC}"
        exit 1
    fi
    
    if ! check_command pip3; then
        echo -e "${YELLOW}[!] pip3 not found. Attempting to install...${NC}"
        if check_command apt-get; then
            sudo apt-get install -y python3-pip
        elif check_command yum; then
            sudo yum install -y python3-pip
        elif check_command pacman; then
            sudo pacman -S --noconfirm python-pip
        else
            echo -e "${RED}Cannot detect package manager. Please install pip3 manually.${NC}"
            exit 1
        fi
    fi
    
    if ! check_command git; then
        echo -e "${YELLOW}[!] git not found. Attempting to install...${NC}"
        if check_command apt-get; then
            sudo apt-get install -y git
        elif check_command yum; then
            sudo yum install -y git
        elif check_command pacman; then
            sudo pacman -S --noconfirm git
        else
            echo -e "${RED}Cannot detect package manager. Please install git manually.${NC}"
            exit 1
        fi
    fi
    
    install_pyrogram
    echo -e "${GREEN}[+] All dependencies installed${NC}"
}

install_program() {
    echo -e "${YELLOW}[*] Installing DoxUB...${NC}"
    
    INSTALL_DIR="$HOME/.local/share/DoxUB"
    BIN_DIR="$HOME/.local/bin"
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"
    
    echo -e "${BLUE}[*] Downloading program...${NC}"
    wget -q https://raw.githubusercontent.com/solorblaze/DoxUB_I/main/main.py -O "$INSTALL_DIR/DoxUB.py"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error downloading program${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}[*] Creating executable...${NC}"
    echo "#!/bin/bash" > "$BIN_DIR/doxub"
    echo "python3 $INSTALL_DIR/DoxUB.py \"\$@\"" >> "$BIN_DIR/doxub"
    chmod +x "$BIN_DIR/doxub"
    
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        echo -e "${YELLOW}[!] Adding $BIN_DIR to PATH...${NC}"
        echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$HOME/.bashrc"
        source "$HOME/.bashrc"
    fi
    
    echo -e "${GREEN}[+] Installation completed successfully!${NC}"
}

verify_installation() {
    echo -e "${YELLOW}[*] Verifying installation...${NC}"
    
    if [ -f "$HOME/.local/share/DoxUB/DoxUB.py" ] && [ -f "$HOME/.local/bin/doxub" ]; then
        echo -e "${GREEN}[+] DoxUB successfully installed to $HOME/.local/share/DoxUB/${NC}"
        echo -e "${GREEN}[+] Executable created at $HOME/.local/bin/doxub${NC}"
        echo -e "\nRun the program with: ${BLUE}doxub${NC}"
    else
        echo -e "${RED}[-] Error installing DoxUB${NC}"
        exit 1
    fi
}

main() {
    header
    echo -e "${YELLOW}This installer will perform the following actions:${NC}"
    echo "1. Check required dependencies"
    echo "2. Install Pyrogram (Telegram library)"
    echo "3. Install DoxUB to ~/.local/share/DoxUB"
    echo "4. Create executable in ~/.local/bin"
    echo ""
    
    read -p "Continue with installation? (y/n): " choice
    case "$choice" in
        y|Y )
            install_dependencies
            install_program
            verify_installation
            ;;
        * )
            echo -e "${RED}Installation cancelled${NC}"
            exit 0
            ;;
    esac
}

main
