#!/usr/bin/env python3
"""
Unit tests for the deployment script
"""

import unittest
import tempfile
import os
import subprocess
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import sys

# Add the parent directory to the path so we can import deploy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deploy import JavaAppDeployment, DeploymentError

class TestJavaAppDeployment(unittest.TestCase):
    """Test cases for JavaAppDeployment class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.deployment = JavaAppDeployment(
            repo_url="git@github.com:test/repo.git",
            repo_name="test-repo",
            branch="main"
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self, 'temp_dir'):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test proper initialization of JavaAppDeployment"""
        self.assertEqual(self.deployment.repo_url, "git@github.com:test/repo.git")
        self.assertEqual(self.deployment.repo_name, "test-repo")
        self.assertEqual(self.deployment.branch, "main")
        self.assertEqual(self.deployment.port, 9000)
    
    @patch('subprocess.run')
    def test_check_prerequisites_success(self, mock_run):
        """Test successful prerequisites check"""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = self.deployment.check_prerequisites()
        
        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 3)  # git, java, ssh
    
    @patch('subprocess.run')
    def test_check_prerequisites_failure(self, mock_run):
        """Test failed prerequisites check"""
        mock_run.side_effect = FileNotFoundError("Command not found")
        
        result = self.deployment.check_prerequisites()
        
        self.assertFalse(result)
    
    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    def test_setup_ssh_config_success(self, mock_exists, mock_run):
        """Test successful SSH configuration"""
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0, stderr="successfully authenticated")
        
        result = self.deployment.setup_ssh_config()
        
        self.assertTrue(result)
    
    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    def test_setup_ssh_config_no_key(self, mock_exists, mock_run):
        """Test SSH configuration with no key"""
        mock_exists.return_value = False
        
        result = self.deployment.setup_ssh_config()
        
        self.assertFalse(result)
    
    @patch('subprocess.run')
    def test_clone_repository_success(self, mock_run):
        """Test successful repository cloning"""
        mock_run.return_value = MagicMock(returncode=0)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            self.deployment.repo_path = Path(temp_dir) / "test-repo"
            result = self.deployment.clone_repository()
        
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_clone_repository_failure(self, mock_run):
        """Test failed repository cloning"""
        mock_run.return_value = MagicMock(returncode=1, stderr="Permission denied")
        
        result = self.deployment.clone_repository()
        
        self.assertFalse(result)
    
    @patch('pathlib.Path.exists')
    def test_verify_jar_file_exists(self, mock_exists):
        """Test JAR file verification when file exists"""
        mock_exists.return_value = True
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = self.deployment.verify_jar_file()
        
        self.assertTrue(result)
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.rglob')
    def test_verify_jar_file_search_alternative(self, mock_rglob, mock_exists):
        """Test JAR file verification with alternative search"""
        mock_exists.return_value = False
        mock_rglob.return_value = [Path("alternative/path/app.jar")]
        
        result = self.deployment.verify_jar_file()
        
        self.assertTrue(result)
        self.assertEqual(self.deployment.jar_path, Path("alternative/path/app.jar"))
    
    @patch('psutil.net_connections')
    def test_check_port_availability_free(self, mock_connections):
        """Test port availability check when port is free"""
        mock_connections.return_value = []
        
        result = self.deployment.check_port_availability()
        
        self.assertTrue(result)
    
    @patch('psutil.net_connections')
    @patch('psutil.Process')
    def test_check_port_availability_in_use(self, mock_process_class, mock_connections):
        """Test port availability check when port is in use"""
        mock_conn = MagicMock()
        mock_conn.laddr.port = 9000
        mock_conn.pid = 1234
        mock_connections.return_value = [mock_conn]
        
        mock_process = MagicMock()
        mock_process_class.return_value = mock_process
        
        result = self.deployment.check_port_availability()
        
        self.assertTrue(result)  # Should be True after killing the process
        mock_process.terminate.assert_called_once()
    
    @patch('subprocess.Popen')
    @patch('os.chdir')
    def test_start_java_application_success(self, mock_chdir, mock_popen):
        """Test successful Java application startup"""
        mock_process = MagicMock()
        mock_process.pid = 1234
        mock_process.poll.return_value = None  # Process is running
        mock_popen.return_value = mock_process
        
        with patch('time.sleep'):
            result = self.deployment.start_java_application()
        
        self.assertTrue(result)
        self.assertEqual(self.deployment.java_process, mock_process)
    
    @patch('subprocess.Popen')
    @patch('os.chdir')
    def test_start_java_application_failure(self, mock_chdir, mock_popen):
        """Test failed Java application startup"""
        mock_process = MagicMock()
        mock_process.pid = 1234
        mock_process.poll.return_value = 1  # Process exited with error
        mock_process.communicate.return_value = ("stdout", "stderr")
        mock_popen.return_value = mock_process
        
        with patch('time.sleep'):
            result = self.deployment.start_java_application()
        
        self.assertFalse(result)
    
    @patch('socket.socket')
    def test_health_check_socket_success(self, mock_socket_class):
        """Test successful health check using socket"""
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 0  # Success
        mock_socket_class.return_value = mock_socket
        
        result = self.deployment.health_check()
        
        self.assertTrue(result)
    
    @patch('socket.socket')
    def test_health_check_socket_failure(self, mock_socket_class):
        """Test failed health check using socket"""
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 1  # Failure
        mock_socket_class.return_value = mock_socket
        
        result = self.deployment.health_check()
        
        self.assertFalse(result)
    
    def test_cleanup_no_process(self):
        """Test cleanup when no process is running"""
        self.deployment.java_process = None
        
        # Should not raise any exception
        self.deployment.cleanup()
    
    @patch('subprocess.Popen.terminate')
    @patch('subprocess.Popen.wait')
    def test_cleanup_with_process(self, mock_wait, mock_terminate):
        """Test cleanup with running process"""
        mock_process = MagicMock()
        self.deployment.java_process = mock_process
        
        self.deployment.cleanup()
        
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()
    
    def test_deploy_integration(self):
        """Test full deployment integration"""
        with patch.object(self.deployment, 'check_prerequisites', return_value=True), \
             patch.object(self.deployment, 'setup_ssh_config', return_value=True), \
             patch.object(self.deployment, 'clone_repository', return_value=True), \
             patch.object(self.deployment, 'verify_jar_file', return_value=True), \
             patch.object(self.deployment, 'check_port_availability', return_value=True), \
             patch.object(self.deployment, 'start_java_application', return_value=True), \
             patch.object(self.deployment, 'health_check', return_value=True):
            
            result = self.deployment.deploy()
            
            self.assertTrue(result)
    
    def test_deploy_failure(self):
        """Test deployment failure handling"""
        with patch.object(self.deployment, 'check_prerequisites', return_value=False):
            result = self.deployment.deploy()
            
            self.assertFalse(result)

class TestDeploymentScript(unittest.TestCase):
    """Test cases for the deployment script functionality"""
    
    def test_deployment_error_exception(self):
        """Test DeploymentError exception"""
        with self.assertRaises(DeploymentError):
            raise DeploymentError("Test error")

if __name__ == '__main__':
    # Configure test logging
    import logging
    logging.basicConfig(level=logging.CRITICAL)  # Suppress logs during testing
    
    # Run tests
    unittest.main(verbosity=2)