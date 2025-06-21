from rest_framework.throttling import AnonRateThrottle, UserRateThrottle, ScopedRateThrottle

class AuthRateThrottle(AnonRateThrottle):
    """
    Throttle class for authentication endpoints.
    More restrictive to prevent brute force attacks.
    """
    scope = 'auth'
    rate = '5/minute'


class BurstRateThrottle(UserRateThrottle):
    """
    Throttle class for authenticated users with burst rate limiting.
    Prevents rapid-fire API calls.
    """
    scope = 'burst'
    rate = '20/minute'


class SensitiveEndpointThrottle(ScopedRateThrottle):
    """
    Throttle class for sensitive endpoints like password reset.
    """
    scope = 'sensitive'
    rate = '3/hour'
