from typing import Annotated
from pydantic import Field
from workout_api.contrib.schemas import BaseSchema


class Atleta(BaseSchema):
    nome: Annotated[str, Field(description='Nome do atleta', example='Joao', max_length=50)]
    cpf: Annotated[str, Field(description='CPF do atleta', example='12345678900', max_length=11)]
    idade: Annotated[int, Field(description='Idade do atleta', example=25)]
    peso: Annotated[float, Field(description='Peso do atleta', example=75.5)]
    altura: Annotated[float, Field(description='Altura do atleta', example=1.70)]
    sexo: Annotated[str, Field(description='Sexo do atleta', example='M', max_length=1)]


class AtletaOut(BaseSchema):
    nome: Annotated[str, Field(description='Nome do atleta', example='Joao', max_length=50)]
    centro_treinamento: Annotated[str, Field(description='Nome do centro de treinamento', example='CT King', max_length=20)]
    categoria: Annotated[str, Field(description='Nome da categoria', example='Scale', max_length=10)]
