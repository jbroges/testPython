from pydantic import BaseModel, Field
from typing import Optional

class Address(BaseModel):
    street: str
    suite: str
    city: str
    zipcode: str
    geo: dict[str, float] = Field(default_factory=dict)  # Optional nested dict for geo data

class Company(BaseModel):
    name: str
    catchPhrase: str
    bs: str

class User(BaseModel):
    id: int
    name: str
    username: str
    email: str
    address: Address
    phone: str
    website: str
    company: Company