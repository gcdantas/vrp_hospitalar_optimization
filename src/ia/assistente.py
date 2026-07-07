"""
Camada de integração com a OpenAI API (Item 3 do Tech Challenge — Projeto 2).

Wrapper fino sobre o SDK `openai`: cada função pública recebe o dict produzido
por src.ia.contexto.construir_contexto e devolve texto gerado pela LLM.
Nenhuma função aqui conhece Pygame ou o loop do algoritmo genético — a fronteira
de integração é exclusivamente o contexto estruturado.

Configuração via variáveis de ambiente (carregadas também de um arquivo .env
na raiz do projeto, se existir — ver .env.example):
- OPENAI_API_KEY (obrigatória)
- OPENAI_MODEL (opcional, default gpt-4o-mini)
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Variáveis já definidas no ambiente têm precedência sobre o .env.
load_dotenv()
from src.ia.prompts import SYSTEM_PROMPT_INSTRUCOES, SYSTEM_PROMPT_RELATORIO, SYSTEM_PROMPT_CHAT

MODELO_PADRAO = "gpt-4o-mini"


def _criar_cliente() -> OpenAI:
    """Valida a presença da chave antes de abrir o client, falhando cedo com mensagem clara."""
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "A variável de ambiente OPENAI_API_KEY não está definida. "
            "Copie o arquivo .env.example para .env na raiz do projeto e preencha sua chave, "
            "ou exporte-a no ambiente (ex.: set OPENAI_API_KEY=sk-... no Windows)."
        )
    return OpenAI()


def _obter_modelo() -> str:
    return os.environ.get("OPENAI_MODEL", MODELO_PADRAO)


def _chamar_llm(cliente: OpenAI, system_prompt: str, conteudo_usuario: str) -> str:
    resposta = cliente.chat.completions.create(
        model=_obter_modelo(),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": conteudo_usuario},
        ],
    )
    return resposta.choices[0].message.content


def gerar_instrucoes_motoristas(contexto: dict) -> dict:
    """
    Gera instruções operacionais individualizadas por motorista.

    Faz uma chamada por veículo ativo (mantém cada prompt pequeno e a resposta
    inequivocamente associada a um único motorista).
    Retorna {id_veiculo: texto_da_instrucao}.
    """
    cliente = _criar_cliente()
    instrucoes = {}

    for veiculo in contexto["veiculos"]:
        payload = json.dumps(veiculo, ensure_ascii=False, indent=2)
        instrucoes[veiculo["id_veiculo"]] = _chamar_llm(
            cliente,
            SYSTEM_PROMPT_INSTRUCOES,
            f"Dados do veículo em JSON:\n{payload}",
        )

    return instrucoes


def gerar_relatorio_eficiencia(contexto: dict) -> str:
    """Gera o relatório executivo de eficiência logística da operação completa."""
    cliente = _criar_cliente()
    payload = json.dumps(contexto, ensure_ascii=False, indent=2)
    return _chamar_llm(
        cliente,
        SYSTEM_PROMPT_RELATORIO,
        f"Dados consolidados da operação em JSON:\n{payload}",
    )


def _montar_perguntas_exemplo(contexto: dict) -> list:
    """Monta sugestões de perguntas usando os dados reais do cenário otimizado."""
    perguntas = [
        "Qual é o custo total da operação?",
        "Qual veículo transporta a maior carga?",
        "Quais rotas possuem pontos críticos de urgência médica?",
        "Qual veículo está com a maior ocupação de capacidade?",
    ]
    if contexto["veiculos"]:
        id_exemplo = contexto["veiculos"][0]["id_veiculo"]
        perguntas.append(f"Qual a sequência de entregas do veículo {id_exemplo}?")
    return perguntas


def chat_interativo(contexto: dict) -> None:
    """
    Abre um chat no terminal para perguntas em linguagem natural sobre rotas e entregas.

    O contexto JSON é injetado uma única vez no system prompt; o histórico de
    mensagens é mantido para permitir conversa multi-turno. Digite 'sair' para encerrar.
    """
    cliente = _criar_cliente()
    payload = json.dumps(contexto, ensure_ascii=False, indent=2)

    mensagens = [
        {"role": "system", "content": f"{SYSTEM_PROMPT_CHAT}\n\nDados da operação:\n{payload}"}
    ]

    print("\n" + "=" * 60)
    print("        CHAT INTERATIVO — ASSISTENTE DE LOGÍSTICA")
    print("=" * 60)
    print("O assistente responde perguntas em linguagem natural sobre")
    print("as rotas e entregas otimizadas acima. Ele só responde quando")
    print("você pergunta — nada é gerado automaticamente.")
    print("\nExemplos de perguntas que você pode fazer:")
    for pergunta_exemplo in _montar_perguntas_exemplo(contexto):
        print(f"  - {pergunta_exemplo}")
    print("\nDigite sua pergunta e pressione Enter (ou 'sair' para encerrar).")

    while True:
        try:
            pergunta = input("\nVocê: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not pergunta:
            continue
        if pergunta.lower() in ("sair", "exit", "quit"):
            break

        mensagens.append({"role": "user", "content": pergunta})
        resposta = cliente.chat.completions.create(
            model=_obter_modelo(),
            messages=mensagens,
        )
        texto = resposta.choices[0].message.content
        mensagens.append({"role": "assistant", "content": texto})
        print(f"\nAssistente: {texto}")

    print("\nChat encerrado.")
