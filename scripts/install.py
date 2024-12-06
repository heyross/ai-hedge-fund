#!/usr/bin/env python3
import os
import platform
import subprocess
import sys
from pathlib import Path
import logging
import json
import urllib.request
import shutil
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.is_windows = self.system == "windows"
        self.is_linux = self.system == "linux"
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.project_root = Path(__file__).parent.parent

    def check_python_version(self):
        """Check if Python version meets requirements."""
        if sys.version_info < (3, 10):
            logger.error("Python 3.10 or higher is required")
            sys.exit(1)
        logger.info(f"Python version check passed: {self.python_version}")

    def install_poetry(self):
        """Install Poetry if not already installed."""
        try:
            subprocess.run(["poetry", "--version"], check=True, capture_output=True)
            logger.info("Poetry is already installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.info("Installing Poetry...")
            try:
                if self.is_windows:
                    subprocess.run([
                        "powershell",
                        "-Command",
                        "(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -"
                    ], check=True)
                else:
                    subprocess.run([
                        "curl", "-sSL", "https://install.python-poetry.org", "|", "python3", "-"
                    ], check=True)
                logger.info("Poetry installed successfully")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install Poetry: {e}")
                sys.exit(1)

    def install_ollama(self):
        """Install Ollama based on the operating system."""
        try:
            subprocess.run(["ollama", "--version"], check=True, capture_output=True)
            logger.info("Ollama is already installed")
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.info("Installing Ollama...")
            
        try:
            if self.is_windows:
                # Download Windows installer
                url = "https://ollama.ai/download/windows"
                installer_path = os.path.join(os.getenv("TEMP"), "ollama-installer.exe")
                urllib.request.urlretrieve(url, installer_path)
                subprocess.run([installer_path], check=True)
            elif self.is_linux:
                # Install Ollama on Linux
                subprocess.run([
                    "curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"
                ], check=True)
            logger.info("Ollama installed successfully")
        except Exception as e:
            logger.error(f"Failed to install Ollama: {e}")
            sys.exit(1)

    def install_system_dependencies(self):
        """Install system-specific dependencies."""
        try:
            if self.is_windows:
                # Install Visual C++ Build Tools if needed
                subprocess.run([
                    "powershell",
                    "-Command",
                    "if (-not (Get-Command cl.exe -ErrorAction SilentlyContinue)) { " +
                    "Write-Host 'Installing Visual C++ Build Tools...'; " +
                    "$webClient = New-Object System.Net.WebClient; " +
                    "$url = 'https://aka.ms/vs/17/release/vs_BuildTools.exe'; " +
                    "$file = $env:temp + '\\vs_BuildTools.exe'; " +
                    "$webClient.DownloadFile($url, $file); " +
                    "Start-Process -FilePath $file -ArgumentList '--quiet --wait --norestart --nocache " +
                    "--installPath C:\\BuildTools --add Microsoft.VisualStudio.Workload.VCTools' -Wait; }"
                ], check=True)
            elif self.is_linux:
                subprocess.run([
                    "sudo", "apt", "update"
                ], check=True)
                subprocess.run([
                    "sudo", "apt", "install", "-y",
                    "build-essential", "python3-dev", "python3-pip",
                    "git", "curl", "libssl-dev", "libffi-dev"
                ], check=True)
            logger.info("System dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install system dependencies: {e}")
            sys.exit(1)

    def setup_project(self):
        """Setup the project using Poetry."""
        try:
            os.chdir(self.project_root)
            subprocess.run(["poetry", "install"], check=True)
            logger.info("Project dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to setup project: {e}")
            sys.exit(1)

    def create_env_file(self):
        """Create .env file from template if it doesn't exist."""
        env_template = self.project_root / "src" / ".env.template"
        env_file = self.project_root / "src" / ".env"
        
        if not env_file.exists() and env_template.exists():
            shutil.copy(env_template, env_file)
            logger.info("Created .env file from template")

    def check_hardware_requirements(self):
        """Check if system meets hardware requirements."""
        import psutil
        
        # Check RAM
        ram_gb = psutil.virtual_memory().total / (1024 ** 3)
        if ram_gb < 16:
            logger.warning("System has less than 16GB RAM. This may impact performance.")
        
        # Check disk space
        disk = psutil.disk_usage('/')
        free_space_gb = disk.free / (1024 ** 3)
        if free_space_gb < 50:
            logger.warning("Less than 50GB free disk space available.")
        
        logger.info(f"System has {ram_gb:.1f}GB RAM and {free_space_gb:.1f}GB free disk space")

    def validate_versions(self):
        """Validate installed package versions meet requirements."""
        try:
            import pkg_resources

            required = {
                'numpy': '>=1.25.0,<2.0.0',
                'matplotlib': '==3.9.2',
                'pandas': '==2.2.0',
                'fastapi': '==0.95.1',
                'uvicorn': '==0.22.0',
                'langchain': '==0.0.350',
                'langchain-openai': '==0.0.2',
                'langchain-community': '==0.0.21'
            }
            
            logger.info("Validating package versions...")
            pkg_resources.require([f"{pkg}{ver}" for pkg, ver in required.items()])
            logger.info("Package version validation successful")
            
        except pkg_resources.VersionConflict as e:
            logger.error(f"Package version conflict: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error validating package versions: {e}")
            sys.exit(1)

    def validate_environment(self):
        """Validate required environment variables are set."""
        required_env_vars = {
            'OPENAI_API_KEY': 'OpenAI API key for GPT models',
            'ALPACA_API_KEY': 'Alpaca trading API key',
            'ALPACA_SECRET_KEY': 'Alpaca trading secret key',
            'DEFAULT_LLM_MODEL': 'Default LLM model (openai or ollama)',
            'OPENAI_MODEL': 'OpenAI model name (e.g., gpt-3.5-turbo)',
            'OLLAMA_MODEL': 'Ollama model name (e.g., llama2)'
        }
        
        missing_vars = []
        env_file_path = os.path.join(self.project_root, 'src', '.env')
        
        if not os.path.exists(env_file_path):
            logger.warning(f"Environment file not found at {env_file_path}")
            return
            
        # Load environment variables from .env file
        load_dotenv(env_file_path)
        
        for var, description in required_env_vars.items():
            if not os.getenv(var):
                missing_vars.append(f"- {var}: {description}")
        
        if missing_vars:
            logger.warning("The following environment variables are not set:")
            for var in missing_vars:
                logger.warning(var)
            logger.warning("Please set these variables in your .env file before running the application")
        else:
            logger.info("All required environment variables are set")

    def run(self):
        """Run the complete installation process."""
        logger.info(f"Starting installation on {self.system}")
        
        self.check_python_version()
        self.check_hardware_requirements()
        self.install_system_dependencies()
        self.install_poetry()
        self.install_ollama()
        self.setup_project()
        self.validate_versions()
        self.create_env_file()
        self.validate_environment()
        
        logger.info("""
Installation completed successfully!

Next steps:
1. Configure your .env file in the src directory
2. Start Ollama service
3. Run 'poetry shell' to activate the virtual environment
4. Start the application using 'poetry run python src/server.py'

For more information, please refer to the documentation.
""")

if __name__ == "__main__":
    installer = SystemInstaller()
    installer.run()
