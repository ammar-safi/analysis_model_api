#!/usr/bin/env python3
"""
Startup script for Sentiment and Stance Analysis API
Handles environment setup, health checks, and server startup
"""

import os
import sys
import time
import subprocess
import argparse
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APIStarter:
    """Handles API startup with environment checks and configuration"""
    
    def __init__(self):
        self.project_root = project_root
        self.venv_path = self.project_root / "venv"
        self.requirements_file = self.project_root / "requirements.txt"
        self.main_module = "main:app"
        
    def check_python_version(self) -> bool:
        """Check if Python version is compatible"""
        min_version = (3, 8)
        current_version = sys.version_info[:2]
        
        if current_version < min_version:
            logger.error(f"Python {min_version[0]}.{min_version[1]}+ required, got {current_version[0]}.{current_version[1]}")
            return False
        
        logger.info(f"Python version check passed: {current_version[0]}.{current_version[1]}")
        return True
    
    def check_virtual_environment(self) -> bool:
        """Check if virtual environment exists and is activated"""
        if not self.venv_path.exists():
            logger.warning("Virtual environment not found. Creating one...")
            return self.create_virtual_environment()
        
        # Check if we're in the virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            logger.info("Virtual environment is active")
            return True
        
        logger.warning("Virtual environment exists but not activated")
        return True
    
    def create_virtual_environment(self) -> bool:
        """Create virtual environment"""
        try:
            logger.info("Creating virtual environment...")
            subprocess.run([
                sys.executable, "-m", "venv", str(self.venv_path)
            ], check=True, cwd=self.project_root)
            
            logger.info("Virtual environment created successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create virtual environment: {e}")
            return False
    
    def get_python_executable(self) -> str:
        """Get the Python executable path for the virtual environment"""
        if os.name == 'nt':  # Windows
            return str(self.venv_path / "Scripts" / "python.exe")
        else:  # Unix-like
            return str(self.venv_path / "bin" / "python")
    
    def get_pip_executable(self) -> str:
        """Get the pip executable path for the virtual environment"""
        if os.name == 'nt':  # Windows
            return str(self.venv_path / "Scripts" / "pip.exe")
        else:  # Unix-like
            return str(self.venv_path / "bin" / "pip")
    
    def install_dependencies(self, force: bool = False) -> bool:
        """Install or update dependencies"""
        if not self.requirements_file.exists():
            logger.error("requirements.txt not found")
            return False
        
        try:
            pip_executable = self.get_pip_executable()
            
            # Upgrade pip first
            logger.info("Upgrading pip...")
            subprocess.run([
                pip_executable, "install", "--upgrade", "pip"
            ], check=True, cwd=self.project_root)
            
            # Install requirements
            logger.info("Installing dependencies...")
            cmd = [pip_executable, "install", "-r", str(self.requirements_file)]
            if force:
                cmd.append("--force-reinstall")
            
            subprocess.run(cmd, check=True, cwd=self.project_root)
            logger.info("Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        try:
            python_executable = self.get_python_executable()
            
            # Check critical imports
            critical_modules = [
                "fastapi",
                "uvicorn",
                "vaderSentiment",
                "textblob",
                "pydantic",
                "psutil"
            ]
            
            for module in critical_modules:
                result = subprocess.run([
                    python_executable, "-c", f"import {module}"
                ], capture_output=True, cwd=self.project_root)
                
                if result.returncode != 0:
                    logger.error(f"Required module '{module}' not found")
                    return False
            
            logger.info("All dependencies are available")
            return True
            
        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")
            return False
    
    def setup_environment(self, env_vars: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Setup environment variables"""
        env = os.environ.copy()
        
        # Default environment variables
        defaults = {
            "PYTHONPATH": str(self.project_root),
            "LOG_LEVEL": "info",
            "HOST": "0.0.0.0",
            "PORT": "8000",
            "CACHE_MAX_SIZE": "1000",
            "CACHE_DEFAULT_TTL": "3600",
            "PERFORMANCE_WINDOW_MINUTES": "60",
            "MEMORY_THRESHOLD_MB": "500"
        }
        
        # Apply defaults
        for key, value in defaults.items():
            if key not in env:
                env[key] = value
        
        # Apply custom environment variables
        if env_vars:
            env.update(env_vars)
        
        # Load from .env file if it exists
        env_file = self.project_root / ".env"
        if env_file.exists():
            logger.info("Loading environment variables from .env file")
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env[key.strip()] = value.strip()
        
        return env
    
    def perform_health_check(self, host: str = "localhost", port: int = 8000, timeout: int = 30) -> bool:
        """Perform health check after startup"""
        import requests
        
        url = f"http://{host}:{port}/health"
        start_time = time.time()
        
        logger.info(f"Performing health check at {url}")
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    logger.info("Health check passed")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
        
        logger.error("Health check failed - API not responding")
        return False
    
    def start_development_server(self, host: str = "0.0.0.0", port: int = 8000, 
                                reload: bool = True, log_level: str = "info") -> bool:
        """Start development server with uvicorn"""
        try:
            python_executable = self.get_python_executable()
            
            cmd = [
                python_executable, "-m", "uvicorn", self.main_module,
                "--host", host,
                "--port", str(port),
                "--log-level", log_level
            ]
            
            if reload:
                cmd.append("--reload")
            
            logger.info(f"Starting development server on {host}:{port}")
            logger.info(f"Command: {' '.join(cmd)}")
            
            # Start the server
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                env=self.setup_environment()
            )
            
            # Wait a bit for server to start
            time.sleep(3)
            
            # Perform health check
            if self.perform_health_check(host, port):
                logger.info("API started successfully!")
                logger.info(f"API documentation: http://{host}:{port}/docs")
                logger.info(f"Health check: http://{host}:{port}/health")
                logger.info(f"Metrics: http://{host}:{port}/metrics/performance")
                
                # Wait for process to complete
                process.wait()
                return True
            else:
                logger.error("API failed to start properly")
                process.terminate()
                return False
                
        except KeyboardInterrupt:
            logger.info("Shutting down server...")
            return True
        except Exception as e:
            logger.error(f"Failed to start development server: {e}")
            return False
    
    def start_production_server(self, host: str = "0.0.0.0", port: int = 8000,
                               workers: int = 4, log_level: str = "info") -> bool:
        """Start production server with gunicorn"""
        try:
            python_executable = self.get_python_executable()
            
            # Check if gunicorn is available
            result = subprocess.run([
                python_executable, "-c", "import gunicorn"
            ], capture_output=True, cwd=self.project_root)
            
            if result.returncode != 0:
                logger.error("Gunicorn not found. Installing...")
                subprocess.run([
                    self.get_pip_executable(), "install", "gunicorn"
                ], check=True, cwd=self.project_root)
            
            cmd = [
                python_executable, "-m", "gunicorn", self.main_module,
                "--workers", str(workers),
                "--worker-class", "uvicorn.workers.UvicornWorker",
                "--bind", f"{host}:{port}",
                "--timeout", "30",
                "--log-level", log_level,
                "--access-logfile", "-",
                "--error-logfile", "-"
            ]
            
            logger.info(f"Starting production server with {workers} workers on {host}:{port}")
            logger.info(f"Command: {' '.join(cmd)}")
            
            # Start the server
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                env=self.setup_environment()
            )
            
            # Wait a bit for server to start
            time.sleep(5)
            
            # Perform health check
            if self.perform_health_check(host, port):
                logger.info("Production API started successfully!")
                logger.info(f"API documentation: http://{host}:{port}/docs")
                logger.info(f"Health check: http://{host}:{port}/health")
                logger.info(f"Metrics: http://{host}:{port}/metrics/performance")
                
                # Wait for process to complete
                process.wait()
                return True
            else:
                logger.error("Production API failed to start properly")
                process.terminate()
                return False
                
        except KeyboardInterrupt:
            logger.info("Shutting down production server...")
            return True
        except Exception as e:
            logger.error(f"Failed to start production server: {e}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Sentiment and Stance Analysis API Startup Script")
    
    parser.add_argument("--mode", choices=["dev", "prod"], default="dev",
                       help="Server mode: dev (development) or prod (production)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--workers", type=int, default=4, help="Number of workers (production mode)")
    parser.add_argument("--log-level", choices=["debug", "info", "warning", "error"], 
                       default="info", help="Log level")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload (dev mode)")
    parser.add_argument("--install-deps", action="store_true", help="Install/update dependencies")
    parser.add_argument("--force-deps", action="store_true", help="Force reinstall dependencies")
    parser.add_argument("--check-only", action="store_true", help="Only perform checks, don't start server")
    
    args = parser.parse_args()
    
    # Initialize starter
    starter = APIStarter()
    
    # Perform checks
    logger.info("Starting Sentiment and Stance Analysis API...")
    logger.info("=" * 50)
    
    if not starter.check_python_version():
        sys.exit(1)
    
    if not starter.check_virtual_environment():
        sys.exit(1)
    
    if args.install_deps or args.force_deps:
        if not starter.install_dependencies(force=args.force_deps):
            sys.exit(1)
    
    if not starter.check_dependencies():
        logger.error("Dependencies check failed. Try running with --install-deps")
        sys.exit(1)
    
    if args.check_only:
        logger.info("All checks passed. API is ready to start.")
        return
    
    # Start server
    logger.info("=" * 50)
    
    if args.mode == "dev":
        success = starter.start_development_server(
            host=args.host,
            port=args.port,
            reload=not args.no_reload,
            log_level=args.log_level
        )
    else:
        success = starter.start_production_server(
            host=args.host,
            port=args.port,
            workers=args.workers,
            log_level=args.log_level
        )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()