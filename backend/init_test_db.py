from sqlalchemy import create_engine
from app.database import Base
from app.models import kit, user, custody_event, approval_request, maintenance_event

# Create SQLite database
engine = create_engine('sqlite:///./test.db')

# Create all tables
Base.metadata.create_all(bind=engine)
print("Test database initialized successfully!")
