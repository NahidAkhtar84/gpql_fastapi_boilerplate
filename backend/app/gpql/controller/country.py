import strawberry
from strawberry.asgi import GraphQL

from fastapi import APIRouter

from app.db.models import Country
from app.db.session import get_db
from app.gpql.type import Query, Mutation

db = get_db()
gpql_country = APIRouter()

schema = strawberry.Schema(Query, Mutation)
graphql_app = GraphQL(schema)

gpql_country.add_route("/graphql", graphql_app)