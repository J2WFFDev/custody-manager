"""
Constants used throughout the application
"""
from app.models.user import UserRole

# Valid user roles - using UserRole enum
VALID_ROLES = [role.value for role in UserRole]
DEFAULT_ROLE = UserRole.parent.value

# Soft Warning Thresholds (CUSTODY-008, CUSTODY-014)
# These control when warnings are displayed for custody events
EXTENDED_CUSTODY_WARNING_DAYS = 7  # Warn if checked out for more than 7 days
OVERDUE_RETURN_WARNING_DAYS = 0  # Warn immediately when past expected return date

# Responsibility Attestation Text (CUSTODY-012)
# Legal disclaimer for off-site custody
ATTESTATION_TEXT = """
RESPONSIBILITY ATTESTATION FOR OFF-SITE CUSTODY

By digitally signing below, I acknowledge and agree to the following:

1. CUSTODY RESPONSIBILITY: I accept full legal responsibility for the firearm kit and all equipment 
   during the period it is in my custody off-site.

2. SAFE STORAGE: I agree to store the firearm kit in a secure location, in compliance with all 
   applicable federal, state, and local laws regarding firearm storage and safety.

3. SUPERVISION: I understand that the kit must remain under direct adult supervision at all times 
   and will only be used by authorized individuals under my direct supervision.

4. TRANSPORT COMPLIANCE: I agree to transport the kit in accordance with all applicable laws and 
   regulations regarding firearm transportation.

5. RETURN OBLIGATION: I agree to return the kit in the same condition it was received, by the 
   agreed-upon return date, or immediately upon request by the organization.

6. LIABILITY: I understand that I am solely responsible for any loss, damage, theft, or misuse 
   of the kit while it is in my custody.

7. INCIDENT REPORTING: I agree to immediately report any loss, theft, damage, or safety incident 
   involving the kit to the organization.

8. LEGAL COMPLIANCE: I certify that I am legally permitted to possess firearms under federal, 
   state, and local law, and that I will use the kit only in lawful activities.

I understand that failure to comply with these terms may result in immediate revocation of 
custody privileges, legal action, and/or notification of law enforcement authorities.

I have read, understood, and agree to all of the above terms and conditions.
""".strip()
