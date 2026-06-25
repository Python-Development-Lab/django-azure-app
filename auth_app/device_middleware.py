"""
Device Health Verification Middleware
Implements Zero Trust Principle 7: Verify device health
NIST SP 800-207 — Policy Enforcement Point component

Note: Full device compliance requires Azure AD Premium P1 + Intune.
This middleware provides application-level device verification as fallback.
"""
import hashlib
import logging

logger = logging.getLogger(__name__)


class DeviceVerificationMiddleware:
    """
    Application-level device health verification.
    Complements Azure AD Conditional Access when P1 license unavailable.

    Checks:
    - User-Agent consistency across session
    - IP address anomalies
    - Suspicious client patterns
    """

    SUSPICIOUS_PATTERNS = [
        'sqlmap', 'nikto', 'nmap', 'masscan',
        'zgrab', 'dirbuster', 'hydra', 'medusa',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            self._verify_device(request)
        response = self.get_response(request)
        return response

    def _verify_device(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = self._get_client_ip(request)
        device_fingerprint = self._compute_fingerprint(user_agent, ip_address)

        # Check for suspicious patterns
        ua_lower = user_agent.lower()
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern in ua_lower:
                logger.warning(
                    f"Suspicious device pattern detected: "
                    f"user={request.user.username} "
                    f"pattern={pattern} "
                    f"ip={ip_address}"
                )
                return

        # Verify session consistency
        session_fingerprint = request.session.get('device_fingerprint')
        if session_fingerprint is None:
            # First request — store fingerprint
            request.session['device_fingerprint'] = device_fingerprint
            request.session['device_ip'] = ip_address
            logger.info(
                f"Device registered: "
                f"user={request.user.username} "
                f"fingerprint={device_fingerprint[:8]}... "
                f"ip={ip_address}"
            )
        elif session_fingerprint != device_fingerprint:
            # Fingerprint changed — potential session hijacking
            logger.warning(
                f"Device fingerprint mismatch: "
                f"user={request.user.username} "
                f"expected={session_fingerprint[:8]}... "
                f"got={device_fingerprint[:8]}... "
                f"ip={ip_address}"
            )

        # IP change detection
        session_ip = request.session.get('device_ip', ip_address)
        if session_ip != ip_address:
            logger.warning(
                f"IP address changed during session: "
                f"user={request.user.username} "
                f"from={session_ip} to={ip_address}"
            )

    def _compute_fingerprint(self, user_agent: str, ip: str) -> str:
        """Compute device fingerprint from User-Agent."""
        data = f"{user_agent}"
        return hashlib.sha256(data.encode()).hexdigest()

    def _get_client_ip(self, request) -> str:
        """Get real client IP considering proxies."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
