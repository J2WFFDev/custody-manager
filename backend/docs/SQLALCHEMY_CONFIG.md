# SQLAlchemy Configuration Guide

This document explains the SQLAlchemy ORM configuration for the WilcoSS Custody Manager backend.

## Overview

The application uses **SQLAlchemy 2.0**, the latest major version with improved type safety and async support.

## Database Configuration

### Connection Setup

Located in `app/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Database URL from environment
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create engine with connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.DEBUG   # Log SQL queries in debug mode
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Connection Parameters

**`pool_pre_ping=True`**
- Verifies database connections are alive before use
- Prevents "connection lost" errors
- Recommended for production environments

**`echo=settings.DEBUG`**
- Logs all SQL queries when DEBUG=True
- Useful for development and debugging
- Disabled in production for performance

### Database URL Format

```
postgresql://username:password@host:port/database_name
```

Examples:
```bash
# Local development
DATABASE_URL=postgresql://postgres:password@localhost:5432/custody_manager

# Railway (auto-provided)
DATABASE_URL=postgresql://user:pass@containers-us-west-123.railway.app:5432/railway

# With SSL (production)
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

## Base Model

All models inherit from `BaseModel` (defined in `app/models/base.py`):

```python
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.sql import func
from app.database import Base

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### Features

- **`__abstract__ = True`**: Prevents creating a table for BaseModel itself
- **`id`**: Auto-incrementing primary key, indexed for performance
- **`created_at`**: Automatically set on record creation (server-side)
- **`updated_at`**: Automatically updated on modification (server-side)
- **Timezone-aware**: Uses `timezone=True` for proper datetime handling

## Model Examples

### User Model

```python
from sqlalchemy import Column, String, Boolean, Enum as SQLEnum
from app.models.base import BaseModel
import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    armorer = "armorer"
    coach = "coach"
    volunteer = "volunteer"
    parent = "parent"

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.volunteer)
    oauth_provider = Column(String, nullable=True)
    oauth_id = Column(String, nullable=True)
    verified_adult = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
```

### Kit Model with Relationships

```python
from sqlalchemy import Column, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class KitStatus(str, enum.Enum):
    available = "available"
    checked_out = "checked_out"
    maintenance = "maintenance"
    lost = "lost"

class Kit(BaseModel):
    __tablename__ = "kits"
    
    code = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    serial_number = Column(String, nullable=True)  # Encrypted in production
    status = Column(SQLEnum(KitStatus), nullable=False, default=KitStatus.available)
    
    # Relationships
    custody_events = relationship("CustodyEvent", back_populates="kit", cascade="all, delete-orphan")
    maintenance_events = relationship("MaintenanceEvent", back_populates="kit", cascade="all, delete-orphan")
```

### Custody Event with Foreign Keys

```python
from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class CustodyEventType(str, enum.Enum):
    check_out = "check_out"
    check_in = "check_in"
    transfer = "transfer"
    lost = "lost"
    found = "found"

class CustodyEvent(BaseModel):
    __tablename__ = "custody_events"
    
    kit_id = Column(Integer, ForeignKey("kits.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(SQLEnum(CustodyEventType), nullable=False)
    notes = Column(Text, nullable=True)
    attestation_accepted = Column(Boolean, default=False)
    expected_return_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    kit = relationship("Kit", back_populates="custody_events")
    user = relationship("User")
```

## Relationship Patterns

### One-to-Many

```python
# Parent model
class Kit(BaseModel):
    custody_events = relationship("CustodyEvent", back_populates="kit")

# Child model
class CustodyEvent(BaseModel):
    kit_id = Column(Integer, ForeignKey("kits.id"))
    kit = relationship("Kit", back_populates="custody_events")
```

### Many-to-One

```python
class CustodyEvent(BaseModel):
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")  # No back_populates if not needed
```

### Cascade Operations

```python
# Delete all custody events when kit is deleted
custody_events = relationship(
    "CustodyEvent",
    back_populates="kit",
    cascade="all, delete-orphan"
)
```

Common cascade options:
- `all` - Propagate all operations
- `delete` - Delete children when parent is deleted
- `delete-orphan` - Delete children when removed from parent
- `save-update` - Propagate add/update operations
- `merge` - Propagate merge operations

## Database Sessions

### Using Sessions in FastAPI

Dependency injection pattern:

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db

@router.get("/kits")
def list_kits(db: Session = Depends(get_db)):
    kits = db.query(Kit).all()
    return kits
```

### Session Management

**Best Practices:**
- Always use `Depends(get_db)` for automatic session cleanup
- Never create sessions manually in route handlers
- Session is automatically closed after request completes
- Transactions are committed automatically on success
- Transactions are rolled back on exceptions

### Manual Session Usage (Services)

```python
from app.database import SessionLocal

def some_background_task():
    db = SessionLocal()
    try:
        # Do database operations
        kit = db.query(Kit).filter(Kit.id == 1).first()
        kit.status = KitStatus.available
        db.commit()
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()
```

## Querying Patterns

### Basic Queries

```python
# Get all records
kits = db.query(Kit).all()

# Get first record
kit = db.query(Kit).first()

# Get by ID
kit = db.query(Kit).filter(Kit.id == 1).first()
# Or using get (deprecated in 2.0)
kit = db.query(Kit).get(1)

# Filter
active_users = db.query(User).filter(User.is_active == True).all()

# Multiple filters
coaches = db.query(User).filter(
    User.role == UserRole.coach,
    User.is_active == True
).all()

# Order by
recent_events = db.query(CustodyEvent).order_by(
    CustodyEvent.created_at.desc()
).all()

# Limit and offset
kits_page = db.query(Kit).offset(10).limit(10).all()

# Count
total_kits = db.query(Kit).count()
```

### Advanced Queries

```python
# Join
events_with_users = db.query(CustodyEvent).join(User).filter(
    User.email == "user@example.com"
).all()

# Left outer join
kits_with_events = db.query(Kit).outerjoin(CustodyEvent).all()

# Group by
from sqlalchemy import func
event_counts = db.query(
    CustodyEvent.kit_id,
    func.count(CustodyEvent.id).label('count')
).group_by(CustodyEvent.kit_id).all()

# Subquery
from sqlalchemy import exists
has_events = db.query(Kit).filter(
    exists().where(CustodyEvent.kit_id == Kit.id)
).all()

# Raw SQL (when needed)
result = db.execute("SELECT * FROM kits WHERE status = :status", {"status": "available"})
```

### Eager Loading

Prevent N+1 queries by loading relationships upfront:

```python
from sqlalchemy.orm import joinedload

# Load kit with all custody events in single query
kit = db.query(Kit).options(
    joinedload(Kit.custody_events)
).filter(Kit.id == 1).first()

# Access events without additional query
for event in kit.custody_events:
    print(event.event_type)
```

## Creating and Updating Records

### Creating Records

```python
# Create new kit
new_kit = Kit(
    code="KIT-001",
    description="Rifle Kit #1",
    status=KitStatus.available
)
db.add(new_kit)
db.commit()
db.refresh(new_kit)  # Get updated fields (id, timestamps)

# Bulk insert
kits = [
    Kit(code=f"KIT-{i:03d}", description=f"Kit {i}")
    for i in range(1, 11)
]
db.add_all(kits)
db.commit()
```

### Updating Records

```python
# Method 1: Query and update
kit = db.query(Kit).filter(Kit.code == "KIT-001").first()
if kit:
    kit.status = KitStatus.maintenance
    db.commit()

# Method 2: Bulk update
db.query(Kit).filter(Kit.status == KitStatus.lost).update({
    "status": KitStatus.available
})
db.commit()

# Method 3: Update from dict
kit_data = {"description": "Updated description", "status": "available"}
db.query(Kit).filter(Kit.id == 1).update(kit_data)
db.commit()
```

### Deleting Records

```python
# Delete single record
kit = db.query(Kit).filter(Kit.id == 1).first()
if kit:
    db.delete(kit)
    db.commit()

# Bulk delete
db.query(Kit).filter(Kit.status == KitStatus.lost).delete()
db.commit()
```

## Transactions

### Explicit Transactions

```python
try:
    # Start transaction
    kit = db.query(Kit).filter(Kit.id == 1).first()
    kit.status = KitStatus.checked_out
    
    # Create custody event
    event = CustodyEvent(
        kit_id=kit.id,
        user_id=user.id,
        event_type=CustodyEventType.check_out
    )
    db.add(event)
    
    # Commit both changes atomically
    db.commit()
except Exception as e:
    # Rollback on error
    db.rollback()
    raise
```

### Nested Transactions (Savepoints)

```python
db.begin_nested()  # Create savepoint
try:
    # Do some risky operations
    kit.status = KitStatus.maintenance
    db.commit()  # Commit savepoint
except:
    db.rollback()  # Rollback to savepoint
    # Outer transaction still active
```

## Performance Optimization

### Indexing

```python
# Single column index
code = Column(String, index=True)

# Unique index
email = Column(String, unique=True, index=True)

# Composite index
from sqlalchemy import Index

class CustodyEvent(BaseModel):
    kit_id = Column(Integer)
    created_at = Column(DateTime)
    
    __table_args__ = (
        Index('ix_kit_created', 'kit_id', 'created_at'),
    )
```

### Query Optimization

```python
# Use count() instead of len(query.all())
count = db.query(Kit).count()  # Good
count = len(db.query(Kit).all())  # Bad - loads all records

# Use exists() instead of count() > 0
from sqlalchemy import exists, select
has_kits = db.query(exists().where(Kit.status == KitStatus.available)).scalar()  # Good
has_kits = db.query(Kit).filter(Kit.status == KitStatus.available).count() > 0  # Less efficient

# Select specific columns
kits = db.query(Kit.id, Kit.code).all()  # Good
kits = db.query(Kit).all()  # Loads all columns
```

### Connection Pooling

Configured in `database.py`:

```python
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,          # Number of persistent connections
    max_overflow=10,      # Additional connections when pool is full
    pool_pre_ping=True,   # Verify connections
    pool_recycle=3600,    # Recycle connections after 1 hour
)
```

## Type Safety with Pydantic

### Schema Definitions

```python
from pydantic import BaseModel, Field

class KitCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    description: str
    serial_number: str | None = None

class KitResponse(BaseModel):
    id: int
    code: str
    description: str
    status: KitStatus
    created_at: datetime
    
    class Config:
        from_attributes = True  # SQLAlchemy 2.0 (was orm_mode)
```

### Using Schemas with SQLAlchemy

```python
@router.post("/kits", response_model=KitResponse)
def create_kit(kit: KitCreate, db: Session = Depends(get_db)):
    # Pydantic validates input
    db_kit = Kit(**kit.dict())
    db.add(db_kit)
    db.commit()
    db.refresh(db_kit)
    # Pydantic serializes output
    return db_kit
```

## Migration Integration

Alembic is configured to auto-detect model changes:

```bash
# Generate migration
alembic revision --autogenerate -m "add serial_number to kits"

# Review generated file in alembic/versions/
# Apply migration
alembic upgrade head
```

Alembic configuration in `alembic/env.py`:

```python
from app.database import Base
from app.models import *  # Import all models

target_metadata = Base.metadata
```

## Best Practices

1. **Always use the BaseModel** for common fields (id, timestamps)
2. **Use Enums for status fields** - Type-safe and database-friendly
3. **Index foreign keys** - Essential for join performance
4. **Use relationships** - Let SQLAlchemy handle joins
5. **Eager load relationships** when you know you'll need them
6. **Use Pydantic schemas** for validation and serialization
7. **Never commit credentials** - Use environment variables
8. **Use migrations** for all schema changes
9. **Test queries** in development with `echo=True`
10. **Handle exceptions** properly with rollback

## Troubleshooting

### Common Issues

**"No such table" errors:**
```bash
# Run migrations
alembic upgrade head
```

**"Connection lost" errors:**
```python
# Enable pool_pre_ping
engine = create_engine(url, pool_pre_ping=True)
```

**Slow queries:**
```python
# Enable SQL logging
engine = create_engine(url, echo=True)
# Look for N+1 queries, missing indexes
```

**Stale data:**
```python
# Refresh object from database
db.refresh(kit)

# Or expire all cached objects
db.expire_all()
```

## Resources

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

**Last Updated:** January 2026  
**Author:** J2WFFDev Team
