from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Float,
    Boolean
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker
)

DATABASE_URL = "sqlite:///store.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)

SessionLocal = sessionmaker(
    bind=engine
)

Base = declarative_base()


class EventDB(Base):

    __tablename__ = "events"

    event_id = Column(
        String,
        primary_key=True
    )

    store_id = Column(String)

    camera_id = Column(String)

    visitor_id = Column(String)

    event_type = Column(String)

    timestamp = Column(String)

    zone_id = Column(String)

    dwell_ms = Column(Integer)

    is_staff = Column(Boolean)

    confidence = Column(Float)

    metadata_json = Column(String)

Base.metadata.create_all(engine)