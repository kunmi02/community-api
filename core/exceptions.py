from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('django.request')

def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF that improves error responses
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If this is an unhandled exception, log it and return a 500
    if response is None:
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return Response(
            {'detail': 'A server error occurred.', 'type': 'server_error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Add more context to the error response
    if isinstance(exc, ValidationError):
        # For validation errors, keep the detailed field errors
        response.data = {
            'detail': 'Validation error',
            'type': 'validation_error',
            'errors': response.data
        }
    elif isinstance(exc, APIException):
        error_type = exc.__class__.__name__.lower()
        if hasattr(exc, 'default_code') and exc.default_code:
            error_type = exc.default_code
            
        # For other API exceptions, standardize the format
        response.data = {
            'detail': str(exc),
            'type': error_type,
            'status_code': response.status_code
        }
    
    return response


class ServiceUnavailableException(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable, please try again later.'
    default_code = 'service_unavailable'


class RateLimitExceededException(APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Request rate limit exceeded.'
    default_code = 'rate_limit_exceeded'


class InvalidInputException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid input.'
    default_code = 'invalid_input'


class ResourceNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found.'
    default_code = 'resource_not_found'


class UnauthorizedException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication credentials were not provided or are invalid.'
    default_code = 'unauthorized'


class ForbiddenException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'forbidden'
