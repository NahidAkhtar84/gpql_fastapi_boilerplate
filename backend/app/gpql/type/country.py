import typing
import strawberry
from strawberry.types import Info

from app.db.session import get_db
from app.db.models import Country

db = get_db()

@strawberry.type
class CountryType:
    id: int
    name: str
    code: str
    currency_name: str
    currency_code: str
    currency_number: int
    description: str

@strawberry.type
class Query:
    @strawberry.field
    def country(id: int)->CountryType:
        return db.execute(Country.select().where(Country.id==1)).fetchone()
    
    @strawberry.field
    def countries(self) -> typing.List[CountryType]:
        return db.execute(Country.select()).fetchall()


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_flavour(self, name: str, info: Info) -> bool:
        return True

    @strawberry.mutation
    async def create_country(
        self, 
        name: str, 
        code: str,
        currency_name: str,
        currency_code: str,
        currency_number: int,
        description: str, 
        info: Info) -> int:
        country =  {
            "name": name,
            "code": code,
            "currency_name": currency_name,
            "currency_code": currency_code,
            "currency_number": currency_number,
            "description": description
        }
        result = db.execute(Country.insert(),country)
        return int(result.inserted_primary_key[0])
    @strawberry.mutation
    def update_country(
        self, 
        id:int, 
        name: str, 
        code: str,
        currency_name: str,
        currency_code: str,
        currency_number: int,
        description: str, 
        info: Info) -> str:
        result = db.execute(
            Country.update().where(Country.id == id), {
            "name": name,
            "code": code,
            "currency_name": currency_name,
            "currency_code": currency_code,
            "currency_number": currency_number,
            "description": description
        })
    
        return str(result.rowcount) + " Row(s) updated"

    @strawberry.mutation
    def delete_country(self, id: int) -> bool:
        result = db.execute(Country.delete().where(Country.id == id))
        return result.rowcount > 0
        

    
