"""
Ponto de entrada do módulo de IA (Item 3 do Tech Challenge — Projeto 2).

Roda a otimização genética de forma headless (sem Pygame, sem callback) e
alimenta a camada de LLM: instruções por motorista, relatório de eficiência
e chat interativo sobre as rotas.

Pré-requisito: variável de ambiente OPENAI_API_KEY definida.
O main.py original continua controlando apenas a simulação visual.
"""

import random
from main import gerar_pontos_aleatorios
from src.core.models import Veiculo
from src.core.genetic_alg import OtimizadorVRP
from src.ia.contexto import construir_contexto
from src.ia.assistente import (
    gerar_instrucoes_motoristas,
    gerar_relatorio_eficiencia,
    chat_interativo,
)


def rodar_pipeline_ia():
    print("=== Otimização de Rotas (headless) + Integração com LLM ===")

    QUANTIDADE_PONTOS = 20
    pontos = gerar_pontos_aleatorios(QUANTIDADE_PONTOS)

    modelos_veiculos = [
        Veiculo(id_veiculo=1, capacidade_max=75.0, autonomia_max=200.0),
        Veiculo(id_veiculo=2, capacidade_max=75.0, autonomia_max=200.0),
        Veiculo(id_veiculo=3, capacidade_max=75.0, autonomia_max=200.0),
        Veiculo(id_veiculo=4, capacidade_max=75.0, autonomia_max=200.0),
        Veiculo(id_veiculo=5, capacidade_max=75.0, autonomia_max=200.0),
    ]

    otimizador = OtimizadorVRP(
        pontos=pontos,
        modelos_veiculos=modelos_veiculos,
        tamanho_populacao=100,
        max_geracoes=300,
        max_estagnacao=40,
        taxa_mutacao=0.15,
        taxa_elitismo=0.03,
    )

    print(f"\nEvoluindo rotas para {QUANTIDADE_PONTOS} pontos (sem interface gráfica)...")
    melhor_solucao = otimizador.executar()
    print(f"Melhor Custo Final: {melhor_solucao.fitness:.2f}")

    contexto = construir_contexto(pontos, melhor_solucao)

    print("\n================ INSTRUÇÕES AOS MOTORISTAS ================")
    instrucoes = gerar_instrucoes_motoristas(contexto)
    for id_veiculo, texto in instrucoes.items():
        print(f"\n--- Veículo {id_veiculo} ---")
        print(texto)

    print("\n================ RELATÓRIO DE EFICIÊNCIA ================")
    relatorio = gerar_relatorio_eficiencia(contexto)
    print(relatorio)

    chat_interativo(contexto)


if __name__ == "__main__":
    # Mesma seed do main.py para permitir comparar o cenário com a simulação visual.
    # Comente ou altere o valor para gerar cenários diferentes a cada execução.
    random.seed(42)
    rodar_pipeline_ia()
