import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from importlib import reload


class TestManageMainFunction(unittest.TestCase):
    """Test cases for the main() function in manage.py"""

    def setUp(self):
        """Set up test fixtures"""
        # Store original sys.argv and environment
        self.original_argv = sys.argv.copy()
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up after tests"""
        # Restore original sys.argv and environment
        sys.argv = self.original_argv
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_successful_execution_with_django(self):
        """Test successful execution when Django is importable"""
        sys.argv = ['manage.py', 'runserver']
        
        with patch('os.environ.setdefault') as mock_setdefault, \
             patch('django.core.management.execute_from_command_line') as mock_execute:
            
            # Import and call main function
            from manage import main
            main()
            
            # Verify environment variable was set
            mock_setdefault.assert_called_once_with(
                'DJANGO_SETTINGS_MODULE', 
                'medical_connect.settings'
            )
            # Verify execute_from_command_line was called with sys.argv
            mock_execute.assert_called_once_with(sys.argv)

    def test_handle_import_error_gracefully(self):
        """Test ImportError handling when django.core.management is not available"""
        sys.argv = ['manage.py']
        
        with patch('os.environ.setdefault'), \
             patch('builtins.__import__', side_effect=ImportError("No module named 'django'")):
            
            from manage import main
            
            # Verify that ImportError is raised with descriptive message
            with self.assertRaises(ImportError) as context:
                main()
            
            # Check that error message is descriptive
            self.assertIn("Couldn't import Django", str(context.exception))

    def test_environment_variable_set_correctly(self):
        """Test that DJANGO_SETTINGS_MODULE is set to correct value"""
        sys.argv = ['manage.py', 'test']
        
        with patch('os.environ.setdefault') as mock_setdefault, \
             patch('django.core.management.execute_from_command_line'):
            
            from manage import main
            main()
            
            # Verify the environment variable key
            call_args = mock_setdefault.call_args
            self.assertEqual(call_args[0][0], 'DJANGO_SETTINGS_MODULE')
            # Verify the settings module value
            self.assertEqual(call_args[0][1], 'medical_connect.settings')

    def test_sys_argv_passed_to_executor(self):
        """Test that sys.argv is correctly passed to execute_from_command_line"""
        test_argv = ['manage.py', 'migrate', '--run-syncdb']
        sys.argv = test_argv.copy()
        
        with patch('os.environ.setdefault'), \
             patch('django.core.management.execute_from_command_line') as mock_execute:
            
            from manage import main
            main()
            
            # Verify execute_from_command_line receives correct argv
            mock_execute.assert_called_once()
            passed_argv = mock_execute.call_args[0][0]
            self.assertEqual(passed_argv, test_argv)

    def test_import_error_message_is_descriptive(self):
        """Test that ImportError message provides helpful information"""
        sys.argv = ['manage.py']
        
        with patch('os.environ.setdefault'), \
             patch('builtins.__import__', side_effect=ImportError("No module named 'django'")):
            
            from manage import main
            
            with self.assertRaises(ImportError) as context:
                main()
            
            error_message = str(context.exception)
            # Check for key helpful information in error message
            self.assertIn("Couldn't import Django", error_message)
            self.assertIn("installed", error_message)
            self.assertIn("PYTHONPATH", error_message)
            self.assertIn("virtual environment", error_message)


if __name__ == '__main__':
    unittest.main()