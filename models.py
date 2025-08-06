from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    api_key = Column(Text, nullable=True)
    api_secret = Column(Text, nullable=True)

    # Configuration du robot par utilisateur
    tracked_assets = Column(Text, default="")  # format CSV: BTC,ETH
    target_profit_percent = Column(Float, default=10.0)  # Par défaut +10%
    active_bot = Column(Boolean, default=False)
