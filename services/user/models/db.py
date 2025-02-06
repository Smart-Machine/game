from sqlalchemy import Column, Integer, String
from sqlalchemy.types import TypeDecorator
from passlib.context import CryptContext

from repository.db import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        """Hash password before storing it in the database."""
        if value is not None:
            return pwd_context.hash(value)
        return value

    def process_result_value(self, value, dialect):
        """Return the hashed password (or None)."""
        return value

    def __repr__(self):
        return "<PasswordType>"


class Users(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(PasswordType, nullable=False)
    bio = Column(String, server_default="nil")
    archtype = Column(String, server_default="nil")
