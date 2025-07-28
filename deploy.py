#!/usr/bin/env python3
"""
Headout Assignment - Deployment Automation Script
=================================================

This script performs automated deployment of a Java application from GitHub repository.

Author: DevOps Engineer
Date: 2025
"""

import os
import sys
import subprocess
import logging
import time
import signal
import psutil
from pathlib import Path
from typing import Optional, Dict, Any
import json
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class DeploymentError(Exception):
    """Custom exception for deployment errors"""
    pass

class JavaAppDeployment:
    """
    Handles deployment of Java application from GitHub repository
    """
    
    def __init__(self, repo_url: str, repo_name: str, branch: str = "main"):
        self.repo_url = repo_url
        self.repo_name = repo_name
        self.branch = branch
        self.repo_path = Path.cwd() / repo_name
        self.jar_path = self.repo_path / "build" / "libs" / "project.jar"
        self.java_process: Optional[subprocess.Popen] = None
        self.port = 9000
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.cleanup()
        sys.exit(0)
    
    def check_prerequisites(self) -> bool:
        """
        Check if all required tools are available
        """
        logger.info("Checking prerequisites...")
        
        required_tools = {
            'git': 'git --version',
            'java': 'java -version',
            'ssh': 'ssh -V'
        }
        
        for tool, command in required_tools.items():
            try:
                result = subprocess.run(
                    command.split(), 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                if result.returncode != 0 and tool != 'ssh':  # ssh -V returns 1 but still works
                    logger.error(f"{tool} is not available or not working properly")
                    return False
                logger.info(f"✓ {tool} is available")
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                logger.error(f"✗ {tool} check failed: {e}")
                return False
        
        return True
    
    def setup_ssh_config(self) -> bool:
        """
        Setup SSH configuration for GitHub access
        """
        logger.info("Setting up SSH configuration...")
        
        ssh_dir = Path.home() / ".ssh"
        ssh_dir.mkdir(mode=0o700, exist_ok=True)
        
        # Check if SSH key exists
        ssh_key_path = ssh_dir / "id_rsa"
        if not ssh_key_path.exists():
            logger.warning("SSH key not found. Please ensure SSH key is configured for GitHub access.")
            logger.info("You can generate one using: ssh-keygen -t rsa -b 4096 -C 'your_email@example.com'")
            return False
        
        # Test SSH connection to GitHub
        try:
            result = subprocess.run(
                ["ssh", "-T", "-o", "StrictHostKeyChecking=no", "git@github.com"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if "successfully authenticated" in result.stderr:
                logger.info("✓ SSH connection to GitHub successful")
                return True
            else:
                logger.error("✗ SSH connection to GitHub failed")
                logger.error(f"SSH output: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            logger.error("✗ SSH connection to GitHub timed out")
            return False
        except Exception as e:
            logger.error(f"✗ SSH connection test failed: {e}")
            return False
    
    def clone_repository(self) -> bool:
        """
        Clone the GitHub repository using SSH
        """
        logger.info(f"Cloning repository: {self.repo_url}")
        
        try:
            # Remove existing repository if it exists
            if self.repo_path.exists():
                logger.info("Removing existing repository...")
                subprocess.run(["rm", "-rf", str(self.repo_path)], check=True)
            
            # Clone repository
            clone_cmd = [
                "git", "clone", 
                "--branch", self.branch,
                "--depth", "1",  # Shallow clone for faster download
                self.repo_url, 
                str(self.repo_path)
            ]
            
            result = subprocess.run(
                clone_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode != 0:
                logger.error(f"Git clone failed: {result.stderr}")
                return False
            
            logger.info("✓ Repository cloned successfully")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("✗ Repository clone timed out")
            return False
        except Exception as e:
            logger.error(f"✗ Repository clone failed: {e}")
            return False
    
    def verify_jar_file(self) -> bool:
        """
        Verify that the JAR file exists and is valid
        """
        logger.info(f"Verifying JAR file at: {self.jar_path}")
        
        if not self.jar_path.exists():
            logger.error(f"✗ JAR file not found at: {self.jar_path}")
            
            # Try to find JAR files in the repository
            jar_files = list(self.repo_path.rglob("*.jar"))
            if jar_files:
                logger.info("Found JAR files in repository:")
                for jar in jar_files:
                    logger.info(f"  - {jar}")
                # Use the first JAR file found
                self.jar_path = jar_files[0]
                logger.info(f"Using JAR file: {self.jar_path}")
            else:
                logger.error("No JAR files found in the repository")
                return False
        
        # Check if JAR file is valid
        try:
            result = subprocess.run(
                ["java", "-jar", str(self.jar_path), "--help"],
                capture_output=True,
                text=True,
                timeout=30
            )
            # Some applications might not support --help, so we don't fail on non-zero exit
            logger.info("✓ JAR file appears to be valid")
            return True
        except subprocess.TimeoutExpired:
            logger.warning("JAR file validation timed out, proceeding anyway...")
            return True
        except Exception as e:
            logger.warning(f"JAR file validation failed: {e}, proceeding anyway...")
            return True
    
    def check_port_availability(self) -> bool:
        """
        Check if the required port is available
        """
        logger.info(f"Checking if port {self.port} is available...")
        
        try:
            # Check if port is already in use
            for conn in psutil.net_connections():
                if conn.laddr.port == self.port:
                    logger.warning(f"Port {self.port} is already in use by PID: {conn.pid}")
                    
                    # Try to kill the process using the port
                    try:
                        process = psutil.Process(conn.pid)
                        process.terminate()
                        process.wait(timeout=10)
                        logger.info(f"Terminated process {conn.pid} using port {self.port}")
                    except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                        logger.error(f"Failed to terminate process using port {self.port}")
                        return False
            
            logger.info(f"✓ Port {self.port} is available")
            return True
            
        except Exception as e:
            logger.error(f"✗ Port check failed: {e}")
            return False
    
    def start_java_application(self) -> bool:
        """
        Start the Java application
        """
        logger.info("Starting Java application...")
        
        try:
            # Change to repository directory
            os.chdir(self.repo_path)
            
            # Start Java application
            cmd = ["java", "-jar", str(self.jar_path)]
            
            # Set environment variables
            env = os.environ.copy()
            env["SERVER_PORT"] = str(self.port)
            
            self.java_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            logger.info(f"✓ Java application started with PID: {self.java_process.pid}")
            
            # Wait a bit and check if process is still running
            time.sleep(5)
            
            if self.java_process.poll() is None:
                logger.info("✓ Java application is running successfully")
                return True
            else:
                stdout, stderr = self.java_process.communicate()
                logger.error(f"✗ Java application failed to start")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Failed to start Java application: {e}")
            return False
    
    def health_check(self) -> bool:
        """
        Perform health check on the running application
        """
        logger.info("Performing health check...")
        
        try:
            import requests
            
            # Try to connect to the application
            response = requests.get(f"http://localhost:{self.port}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✓ Health check passed")
                return True
        except ImportError:
            logger.warning("requests library not available, skipping HTTP health check")
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
        
        # Alternative health check - just check if port is listening
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', self.port))
            sock.close()
            
            if result == 0:
                logger.info("✓ Application is listening on the port")
                return True
            else:
                logger.error("✗ Application is not listening on the port")
                return False
                
        except Exception as e:
            logger.error(f"✗ Health check failed: {e}")
            return False
    
    def monitor_application(self, duration: int = 300) -> None:
        """
        Monitor the application for specified duration
        """
        logger.info(f"Monitoring application for {duration} seconds...")
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            if self.java_process and self.java_process.poll() is not None:
                logger.error("✗ Java application has stopped unexpectedly")
                stdout, stderr = self.java_process.communicate()
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                break
            
            time.sleep(30)  # Check every 30 seconds
            logger.info("Application is still running...")
        
        logger.info("Monitoring completed")
    
    def cleanup(self) -> None:
        """
        Clean up resources
        """
        logger.info("Cleaning up resources...")
        
        if self.java_process:
            try:
                self.java_process.terminate()
                self.java_process.wait(timeout=10)
                logger.info("✓ Java application terminated")
            except subprocess.TimeoutExpired:
                logger.warning("Java application didn't terminate gracefully, killing...")
                self.java_process.kill()
                self.java_process.wait()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
    
    def deploy(self) -> bool:
        """
        Main deployment method
        """
        logger.info("Starting deployment process...")
        
        try:
            # Check prerequisites
            if not self.check_prerequisites():
                raise DeploymentError("Prerequisites check failed")
            
            # Setup SSH
            if not self.setup_ssh_config():
                raise DeploymentError("SSH setup failed")
            
            # Clone repository
            if not self.clone_repository():
                raise DeploymentError("Repository clone failed")
            
            # Verify JAR file
            if not self.verify_jar_file():
                raise DeploymentError("JAR file verification failed")
            
            # Check port availability
            if not self.check_port_availability():
                raise DeploymentError("Port availability check failed")
            
            # Start application
            if not self.start_java_application():
                raise DeploymentError("Application startup failed")
            
            # Perform health check
            if not self.health_check():
                logger.warning("Health check failed, but continuing...")
            
            logger.info("✓ Deployment completed successfully!")
            return True
            
        except DeploymentError as e:
            logger.error(f"✗ Deployment failed: {e}")
            self.cleanup()
            return False
        except Exception as e:
            logger.error(f"✗ Unexpected error during deployment: {e}")
            self.cleanup()
            return False

def main():
    """
    Main function to run the deployment script
    """
    parser = argparse.ArgumentParser(description="Deploy Java application from GitHub")
    parser.add_argument("--repo-url", required=True, help="GitHub repository URL (SSH)")
    parser.add_argument("--repo-name", required=True, help="Repository name")
    parser.add_argument("--branch", default="main", help="Git branch to clone")
    parser.add_argument("--monitor", type=int, default=300, help="Monitor duration in seconds")
    
    args = parser.parse_args()
    
    # Create deployment instance
    deployment = JavaAppDeployment(
        repo_url=args.repo_url,
        repo_name=args.repo_name,
        branch=args.branch
    )
    
    # Run deployment
    if deployment.deploy():
        logger.info("Starting application monitoring...")
        deployment.monitor_application(args.monitor)
        deployment.cleanup()
        sys.exit(0)
    else:
        logger.error("Deployment failed")
        sys.exit(1)

if __name__ == "__main__":
    main()