"""
Simple exception handler
"""
import sys
import traceback


class ExceptionHandler:
    """Simple exception handler that captures detailed error info"""
    
    @staticmethod
    def get_error_details(exception: Exception) -> dict:
        """
        Extract error details from an exception
        
        Returns:
            dict with error_type, message, file, line, and function
        """
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        if exc_traceback is None:
            return {
                'error_type': type(exception).__name__,
                'message': str(exception),
                'file': 'Unknown',
                'line': 'Unknown',
                'function': 'Unknown'
            }
        
        # Get the last frame (where error occurred)
        tb = traceback.extract_tb(exc_traceback)
        last_frame = tb[-1]
        
        return {
            'error_type': exc_type.__name__,
            'message': str(exc_value),
            'file': last_frame.filename,
            'line': last_frame.lineno,
            'function': last_frame.name,
            'code': last_frame.line
        }
    
    @staticmethod
    def print_error(exception: Exception):
        """Print formatted error details"""
        details = ExceptionHandler.get_error_details(exception)
        print(f"ERROR: {details['error_type']}")
        print(f"Message: {details['message']}")
        print(f"File: {details['file']}")
        print(f"Line: {details['line']}")
        print(f"Function: {details['function']}")
        print(f"Code: {details['code']}\n")