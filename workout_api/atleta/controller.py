from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4

from fastapi import Query
from fastapi_pagination import Page, paginate
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from workout_api.atleta.models import AtletaModel
from workout_api.atleta.schemas import AtletaIn, AtletaOut 
from workout_api.categorias.models import CategoriaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.contrib.dependencies import DatabaseDependency

router = APIRouter()

@router.post(
    '/',
    summary='Criar um novo atleta',
    status_code=status.HTTP_201_CREATED
)
async def create(
    db_session: DatabaseDependency,
    atleta_in: AtletaIn = Body(...)
):
    categoria_nome = atleta_in.categoria.nome
    centro_treinamento_nome = atleta_in.centro_treinamento.nome

    categoria = (await db_session.execute(
        select(CategoriaModel).filter_by(nome=categoria_nome))
    ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'A categoria {categoria_nome} não foi encontrada.'
        )

    centro_treinamento = (await db_session.execute(
        select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome))
    ).scalars().first()

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'O centro de treinamento {centro_treinamento_nome} não foi encontrado.'
        )
    
    try:
        atleta = AtletaModel(
            id=uuid4(),
            nome=atleta_in.nome,
            cpf=atleta_in.cpf,
            idade=atleta_in.idade,
            peso=atleta_in.peso,
            altura=atleta_in.altura,
            sexo=atleta_in.sexo,
            created_at=datetime.utcnow(),
            categoria_id=categoria.pk_id,
            centro_treinamento_id=centro_treinamento.pk_id
        )
        db_session.add(atleta)
        await db_session.commit()

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f"Já existe um atleta cadastrado com o cpf: {atleta_in.cpf}"
        )

    return atleta_in


@router.get(
    '/',
    summary='Consultar todos os Atletas',
    status_code=status.HTTP_200_OK,
    response_model=Page[AtletaOut],
)
async def get_all(
    db_session: DatabaseDependency,
    nome: str = Query(None, description="Filtrar atleta pelo nome"),
    cpf: str = Query(None, description="Filtrar atleta pelo CPF")
) -> Page[AtletaOut]:
    
    query = (
        select(AtletaModel.nome, CentroTreinamentoModel.nome.label('centro_treinamento'), CategoriaModel.nome.label('categoria'))
        .join(CentroTreinamentoModel, AtletaModel.centro_treinamento_id == CentroTreinamentoModel.pk_id)
        .join(CategoriaModel, AtletaModel.categoria_id == CategoriaModel.pk_id)
    )

    if nome:
        query = query.filter(AtletaModel.nome == nome)
    if cpf:
        query = query.filter(AtletaModel.cpf == cpf)

    atletas = (await db_session.execute(query)).all()

    atletas_out = [AtletaOut(nome=a.nome, centro_treinamento=a.centro_treinamento, categoria=a.categoria) for a in atletas]

    return paginate(atletas_out)
