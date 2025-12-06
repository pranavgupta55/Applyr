"""
Email discovery and verification engine.
Handles pattern generation, DNS checks, and safe SMTP verification.
"""
import re
import time
import socket
import smtplib
from typing import List, Dict, Optional
import dns.resolver
from email_validator import validate_email, EmailNotValidError


class EmailDiscovery:
    """Discover and verify recruiter email addresses."""

    # Common email patterns (ordered by likelihood)
    PATTERNS = [
        "{first}.{last}",
        "{first}{last}",
        "{f}{last}",
        "{first}",
        "{first}.{l}",
        "{f}.{last}",
        "{last}.{first}",
        "{first}_{last}",
        "{last}",
        "{first}{l}",
    ]

    def __init__(self):
        self.dns_cache = {}
        self.last_smtp_check = 0
        self.min_smtp_delay = 2.0  # Minimum 2 seconds between SMTP checks

    # ==================== PATTERN GENERATION ====================

    def generate_email_candidates(
        self,
        first_name: str,
        last_name: str,
        domain: str
    ) -> List[Dict[str, str]]:
        """
        Generate email address candidates based on common patterns.
        Returns list of dicts: [{email, pattern, confidence}]
        """
        candidates = []

        # Normalize inputs
        first = first_name.lower().strip()
        last = last_name.lower().strip()
        domain = domain.lower().strip()

        # Remove common domain prefixes
        domain = domain.replace('www.', '')

        for pattern in self.PATTERNS:
            try:
                email = pattern.format(
                    first=first,
                    last=last,
                    f=first[0] if first else '',
                    l=last[0] if last else ''
                )
                email = f"{email}@{domain}"

                candidates.append({
                    'email': email,
                    'pattern': pattern,
                    'confidence': 'high' if pattern in ['{first}.{last}', '{first}{last}'] else 'medium'
                })
            except (IndexError, KeyError):
                continue

        return candidates

    # ==================== SYNTAX VALIDATION ====================

    def validate_syntax(self, email: str) -> bool:
        """
        Validate email syntax using regex and email-validator.
        """
        try:
            # Use email-validator library
            valid = validate_email(email, check_deliverability=False)
            return True
        except EmailNotValidError:
            return False

    # ==================== DNS VERIFICATION ====================

    def check_mx_records(self, domain: str) -> Optional[str]:
        """
        Check if domain has valid MX records.
        Returns the primary MX server or None.
        """
        # Check cache first
        if domain in self.dns_cache:
            return self.dns_cache[domain]

        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            if mx_records:
                # Get the MX record with lowest priority (highest preference)
                primary_mx = sorted(mx_records, key=lambda r: r.preference)[0]
                mx_host = str(primary_mx.exchange).rstrip('.')
                self.dns_cache[domain] = mx_host
                return mx_host
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            self.dns_cache[domain] = None
            return None

    # ==================== SMTP VERIFICATION ====================

    def verify_smtp(self, email: str, mx_server: str = None) -> Dict[str, any]:
        """
        Safely verify email via SMTP handshake.
        Returns {valid: bool, status: str, catch_all: bool}

        SAFETY PROTOCOL:
        - Rate limited to 1 check per 2 seconds
        - Only does HELO, MAIL FROM, RCPT TO (no actual sending)
        - Handles catch-all servers gracefully
        """
        # Rate limiting
        elapsed = time.time() - self.last_smtp_check
        if elapsed < self.min_smtp_delay:
            time.sleep(self.min_smtp_delay - elapsed)

        self.last_smtp_check = time.time()

        # Extract domain
        domain = email.split('@')[1]

        # Get MX server if not provided
        if mx_server is None:
            mx_server = self.check_mx_records(domain)
            if mx_server is None:
                return {'valid': False, 'status': 'No MX records', 'catch_all': False}

        try:
            # Connect to SMTP server
            server = smtplib.SMTP(timeout=10)
            server.connect(mx_server)

            # HELO
            server.helo('mail.example.com')

            # MAIL FROM
            server.mail('verify@example.com')

            # RCPT TO (the actual verification step)
            code, message = server.rcpt(email)

            server.quit()

            # Interpret response
            if code == 250:
                # Likely valid OR catch-all
                # Test with a random email to detect catch-all
                catch_all = self._check_catch_all(mx_server, domain)
                return {
                    'valid': True,
                    'status': 'Likely Valid' if not catch_all else 'Risky (Catch-all)',
                    'catch_all': catch_all
                }
            elif code == 550:
                return {'valid': False, 'status': 'User Unknown', 'catch_all': False}
            else:
                return {'valid': False, 'status': f'Unknown ({code})', 'catch_all': False}

        except smtplib.SMTPServerDisconnected:
            return {'valid': False, 'status': 'Server Disconnected', 'catch_all': False}
        except smtplib.SMTPConnectError:
            return {'valid': False, 'status': 'Connection Failed', 'catch_all': False}
        except socket.timeout:
            return {'valid': False, 'status': 'Timeout', 'catch_all': False}
        except Exception as e:
            return {'valid': False, 'status': f'Error: {str(e)[:50]}', 'catch_all': False}

    def _check_catch_all(self, mx_server: str, domain: str) -> bool:
        """
        Check if domain uses catch-all by testing a random email.
        """
        try:
            random_email = f"random_nonexistent_user_12345@{domain}"

            server = smtplib.SMTP(timeout=5)
            server.connect(mx_server)
            server.helo('mail.example.com')
            server.mail('verify@example.com')
            code, _ = server.rcpt(random_email)
            server.quit()

            # If random email also returns 250, it's catch-all
            return code == 250

        except Exception:
            # If we can't verify, assume not catch-all
            return False

    # ==================== FULL VERIFICATION PIPELINE ====================

    def verify_email_full(self, email: str) -> Dict[str, any]:
        """
        Full verification pipeline:
        1. Syntax check
        2. DNS/MX check
        3. SMTP verification

        Returns complete verification result.
        """
        result = {
            'email': email,
            'syntax_valid': False,
            'mx_valid': False,
            'smtp_valid': False,
            'status': 'Unknown',
            'confidence': 'low',
            'mx_server': None,
        }

        # Step 1: Syntax
        if not self.validate_syntax(email):
            result['status'] = 'Invalid Syntax'
            return result

        result['syntax_valid'] = True

        # Step 2: DNS/MX
        domain = email.split('@')[1]
        mx_server = self.check_mx_records(domain)

        if mx_server is None:
            result['status'] = 'No MX Records'
            return result

        result['mx_valid'] = True
        result['mx_server'] = mx_server

        # Step 3: SMTP (optional, can be disabled for speed)
        smtp_result = self.verify_smtp(email, mx_server)

        result['smtp_valid'] = smtp_result['valid']
        result['status'] = smtp_result['status']

        if smtp_result['valid'] and not smtp_result['catch_all']:
            result['confidence'] = 'high'
        elif smtp_result['valid'] and smtp_result['catch_all']:
            result['confidence'] = 'medium'
        else:
            result['confidence'] = 'low'

        return result

    def verify_candidates(
        self,
        candidates: List[Dict[str, str]],
        max_checks: int = 5,
        skip_smtp: bool = False
    ) -> List[Dict[str, any]]:
        """
        Verify a list of email candidates.
        Returns sorted list by confidence.
        """
        results = []

        # Limit the number of SMTP checks to avoid hammering
        smtp_count = 0

        for candidate in candidates[:max_checks]:
            email = candidate['email']

            if skip_smtp or smtp_count >= max_checks:
                # Just do syntax and DNS
                result = {
                    'email': email,
                    'pattern': candidate['pattern'],
                    'syntax_valid': self.validate_syntax(email),
                    'mx_valid': False,
                    'status': 'Not Verified',
                    'confidence': 'low'
                }

                domain = email.split('@')[1]
                mx = self.check_mx_records(domain)
                if mx:
                    result['mx_valid'] = True
                    result['status'] = 'MX Valid (SMTP Skipped)'
                    result['confidence'] = 'medium'

                results.append(result)
            else:
                # Full verification
                result = self.verify_email_full(email)
                result['pattern'] = candidate['pattern']
                results.append(result)
                smtp_count += 1

        # Sort by confidence
        confidence_order = {'high': 0, 'medium': 1, 'low': 2}
        results.sort(key=lambda r: confidence_order.get(r['confidence'], 3))

        return results

    # ==================== LINKEDIN SEARCH HELPER ====================

    def generate_linkedin_search_url(self, company_name: str, role: str = "recruiter") -> str:
        """
        Generate a LinkedIn search URL for finding contacts.
        The user will manually open this and find names.
        """
        query = f'site:linkedin.com/in {company_name} "{role}"'
        # URL encode
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        return f"https://www.google.com/search?q={encoded_query}"


# ==================== HELPER FUNCTIONS ====================

def extract_domain_from_company(company_name: str) -> Optional[str]:
    """
    Infer domain from company name (best effort).
    Returns domain like 'stripe.com'
    """
    # Common mappings
    mappings = {
        'Google': 'google.com',
        'Microsoft': 'microsoft.com',
        'Meta': 'meta.com',
        'Amazon': 'amazon.com',
        'Apple': 'apple.com',
        'SpaceX': 'spacex.com',
        'Tesla': 'tesla.com',
        'OpenAI': 'openai.com',
        'Anthropic': 'anthropic.com',
    }

    if company_name in mappings:
        return mappings[company_name]

    # Otherwise, make a guess
    clean_name = company_name.lower().replace(' ', '').replace(',', '').replace('.', '')
    return f"{clean_name}.com"
