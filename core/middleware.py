import time
import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger('django.request')

class RequestLogMiddleware(MiddlewareMixin):
    """Middleware to log all requests and responses"""
    
    def process_request(self, request):
        request.start_time = time.time()
        
        # Cache the request body for later use in process_response
        if request.method != 'GET' and settings.DEBUG:
            try:
                # Store the body content
                if request.body:
                    request._cached_body = request.body.decode('utf-8', errors='replace')
                else:
                    request._cached_body = ''
            except Exception as e:
                request._cached_body = f'Error reading body: {str(e)}'
    
    def process_response(self, request, response):
        if not hasattr(request, 'start_time'):
            return response
            
        # Calculate request duration
        duration = time.time() - request.start_time
        
        # Get the status code
        status_code = response.status_code
        
        # Get the request path and method
        path = request.path
        method = request.method
        
        # Log the request details
        log_data = {
            'remote_address': request.META.get('REMOTE_ADDR'),
            'server_hostname': request.META.get('SERVER_NAME'),
            'request_method': method,
            'request_path': path,
            'response_status': status_code,
            'duration': round(duration * 1000, 2),  # Convert to milliseconds
            'user': request.user.username if request.user.is_authenticated else 'anonymous',
        }
        
        # Only log request body in debug mode and for non-GET requests
        if settings.DEBUG and method != 'GET' and hasattr(request, '_cached_body'):
            try:
                log_data['request_body'] = json.loads(request._cached_body) if request._cached_body else {}
            except:
                log_data['request_body'] = request._cached_body
        
        # Log based on status code
        if status_code >= 500:
            logger.error(f"Request: {json.dumps(log_data)}")
        elif status_code >= 400:
            logger.warning(f"Request: {json.dumps(log_data)}")
        else:
            logger.info(f"Request: {json.dumps(log_data)}")
            
        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware to add security headers to all responses"""
    
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Only add CSP in production
        if not settings.DEBUG:
            csp = (
                "default-src 'self'; "
                "img-src 'self' data:; "
                "style-src 'self' 'unsafe-inline'; "
                "script-src 'self'; "
                "font-src 'self'; "
                "connect-src 'self';"
            )
            response['Content-Security-Policy'] = csp
            
        return response
