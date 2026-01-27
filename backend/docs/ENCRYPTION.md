# Field-Level Encryption Security Documentation

## Overview

This document describes the field-level encryption implementation for the WilcoSS Custody Manager application, specifically addressing **AUDIT-003**: Serial number encryption in the database.

## Purpose

Serial numbers are considered sensitive information that should be protected from unauthorized access. This implementation ensures that even if the database is compromised in a data breach, serial numbers remain encrypted and cannot be read without access to the encryption key.

## Implementation Details

### Encryption Technology

- **Algorithm**: AES-256 (Advanced Encryption Standard with 256-bit key)
- **Scheme**: Fernet symmetric encryption
- **Library**: `cryptography` package (via `python-jose[cryptography]`)

### Architecture

The implementation uses SQLAlchemy's `TypeDecorator` to create a custom column type that automatically encrypts data before storing it in the database and decrypts it when retrieving it.

#### Key Components

1. **EncryptedString Type** (`backend/app/core/encryption.py`)
   - Custom SQLAlchemy type that handles encryption/decryption transparently
   - Automatically encrypts values in `process_bind_param()` (before database write)
   - Automatically decrypts values in `process_result_value()` (after database read)

2. **Encryption Key Management** (`backend/app/config.py`)
   - Encryption key stored in `ENCRYPTION_KEY` environment variable
   - Key is derived using SHA-256 to ensure proper format for Fernet
   - Auto-generated if not provided (for development only)
   - **CRITICAL**: In production, use a strong, randomly-generated key

3. **Database Schema** (`backend/app/models/kit.py`)
   - `serial_number` column uses `EncryptedString(500)` type
   - Larger storage size (500 chars) to accommodate encryption overhead
   - Column is nullable to support kits without serial numbers

### Data Flow

```
Plaintext Serial Number
        ↓
    (API Layer)
        ↓
  Pydantic Schema
        ↓
   SQLAlchemy ORM
        ↓
EncryptedString.process_bind_param()
        ↓
    Encrypted Text → Database
        ↓
EncryptedString.process_result_value()
        ↓
   Decrypted Text
        ↓
  Pydantic Schema
        ↓
    (API Response)
```

## Security Considerations

### Key Management

**Development:**
- Auto-generated keys are acceptable for local testing
- Keys are ephemeral and regenerated on restart

**Production:**
- **MUST** use a strong, randomly-generated encryption key
- **MUST** store the key securely (environment variables, secrets manager)
- **MUST** backup the key securely - lost keys = lost data
- **SHOULD** rotate keys periodically (requires data re-encryption)

### Key Generation

To generate a secure encryption key for production:

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -base64 32
```

### Access Control

- Encryption keys should only be accessible to:
  - Application servers at runtime
  - Authorized DevOps/SRE personnel for deployment
  - Backup/disaster recovery systems

### Database Security

- Encrypted data in the database appears as random base64-encoded strings
- Without the encryption key, the data cannot be decrypted
- Database backups contain encrypted data and are safe from serial number exposure
- **However**, database access logs, application logs, and API responses contain decrypted data

### Limitations

1. **Searching**: Cannot search encrypted fields efficiently
   - Use kit codes (unencrypted) for lookups instead
   - Serial numbers are reference-only, not used for search

2. **Performance**: Minimal overhead for encryption/decryption
   - Acceptable for low-volume serial number access
   - Not recommended for high-frequency queries on millions of records

3. **Key Rotation**: Changing encryption keys requires:
   - Reading all encrypted data
   - Decrypting with old key
   - Re-encrypting with new key
   - Updating all records

## Configuration

### Environment Variables

Add to `.env` file:

```bash
# Field-level encryption (AUDIT-003)
ENCRYPTION_KEY=your-strong-random-key-here-use-secrets-token-urlsafe-32
```

### Settings Class

The encryption key is loaded in `backend/app/config.py`:

```python
class Settings(BaseSettings):
    # Field-level encryption (AUDIT-003)
    ENCRYPTION_KEY: str = secrets.token_urlsafe(32)
```

## Testing

Comprehensive tests are provided in `backend/tests/test_encryption.py`:

- **test_fernet_key_generation**: Verifies key derivation
- **test_encrypted_string_type**: Tests encryption/decryption cycle
- **test_kit_serial_number_encryption**: Validates database encryption
- **test_kit_serial_number_decryption**: Validates database decryption
- **test_kit_without_serial_number**: Tests NULL value handling
- **test_serial_number_update**: Tests updating encrypted values
- **test_encryption_key_consistency**: Verifies consistent keys
- **test_different_values_encrypt_differently**: Security validation
- **test_empty_string_encryption**: Edge case testing

Run tests with:

```bash
cd backend
python -m pytest tests/test_encryption.py -v
```

## Migration

Database migration is provided in `backend/alembic/versions/008_add_encrypted_serial_number.py`:

```bash
# Apply migration
cd backend
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

## API Usage

### Creating a Kit with Serial Number

```bash
POST /api/v1/kits/
{
  "code": "KIT-001",
  "name": "Test Kit",
  "description": "A test kit",
  "serial_number": "SN-12345-ABCDE"
}
```

### Retrieving Kit with Serial Number

```bash
GET /api/v1/kits/1

Response:
{
  "id": 1,
  "code": "KIT-001",
  "name": "Test Kit",
  "serial_number": "SN-12345-ABCDE",  # Automatically decrypted
  ...
}
```

## Compliance

This implementation addresses:

- **AUDIT-003**: Serial numbers encrypted in database
- **Data Protection**: Sensitive data protected at rest
- **Breach Mitigation**: Encrypted data useless without key
- **Defense in Depth**: Additional security layer beyond database access control

## Monitoring and Auditing

### What to Monitor

1. Failed decryption attempts (may indicate key mismatch)
2. Encryption/decryption performance metrics
3. Key access patterns
4. Database access to encrypted columns

### Logging

- Encryption/decryption operations are transparent to application code
- No plaintext serial numbers should appear in database logs
- Application logs may contain decrypted values - secure accordingly
- API access logs contain decrypted responses - secure accordingly

## Incident Response

### If Encryption Key is Compromised

1. Generate a new encryption key immediately
2. Re-encrypt all data with the new key
3. Rotate the compromised key out of all systems
4. Investigate how the key was compromised
5. Review access logs for unauthorized data access

### If Database is Breached

1. Encrypted serial numbers remain protected
2. Investigate breach vector and remediate
3. Consider rotating encryption key as precaution
4. Review whether encryption key was also exposed

## Best Practices

1. **Never** commit encryption keys to version control
2. **Always** use environment variables or secrets managers
3. **Regularly** backup encryption keys securely
4. **Document** key rotation procedures
5. **Test** backup and restore procedures
6. **Monitor** for encryption failures
7. **Audit** access to encrypted data

## Future Enhancements

Potential improvements to consider:

1. **Key Rotation**: Automated key rotation with graceful migration
2. **Hardware Security Modules (HSM)**: For key storage in high-security environments
3. **Envelope Encryption**: Using multiple encryption layers
4. **Field-Level Access Control**: Restricting which users can see decrypted data
5. **Audit Logging**: Tracking who accesses serial numbers and when
6. **Regional Encryption**: Different keys per region for compliance

## References

- [Fernet Specification](https://github.com/fernet/spec/)
- [SQLAlchemy TypeDecorator](https://docs.sqlalchemy.org/en/20/core/custom_types.html#typedecorator)
- [Python Cryptography Library](https://cryptography.io/)
- [NIST Encryption Guidelines](https://csrc.nist.gov/publications/detail/sp/800-175b/rev-1/final)

## Support

For questions or issues related to encryption:

1. Review this documentation
2. Check test cases for examples
3. Review code in `backend/app/core/encryption.py`
4. Contact the security team for key management questions
