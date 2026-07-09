from typing import List
from pydantic import BaseModel, Field


class TrendingStock(BaseModel):
    """Uma empresa que está nos noticiários e chama a atenção de investidores"""

    name: str = Field(description="Nome da empresa")
    ticker: str = Field(description="Símbolo oficial da ação na bolsa de valores")
    description: str = Field(description="Descrição da atividade da empresa")
    reasons: List[str] = Field(
        description="Lista de motivos que justificam existência de tendência"
    )


class TrendingStocksList(BaseModel):
    """Lista de empresas que estão se destacando nas notícias"""

    companies: List[TrendingStock] = Field(
        description="Lista de empresas que se destacam nas notícias e chamam atenção de investidores",
        min_length=2,
        max_length=3,
    )


class TrendingCompanyResearch(BaseModel):
    name: str = Field(description="Nome da empresa")
    market_position: str = Field(
        description="Posição atual no mercado e análise competitiva"
    )
    future_outlook: str = Field(description="Perspectiva de futuro e de crescimento")
    investment_potential: str = Field(
        description="Potencial e adequação de investimento"
    )


class TrendingCompaniesResearchList(BaseModel):
    companies: List[TrendingCompanyResearch] = Field(
        description="Lista de análises de empresas mostrando potencial de crescimento inferido",
        min_length=2,
        max_length=3,
    )


class SelectedCompany(BaseModel):
    name: str = Field(description="Nome da empresa")
    ticker: str = Field(description="Símbolo da empresa na bolsa de valores")
    description: str = Field(description="Descrição da atividade da empresa")
    reasons: List[str] = Field(
        description="Lista de razões pelos quais a empresa possui potencial de crescimento"
    )
