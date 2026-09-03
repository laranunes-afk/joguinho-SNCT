import random

from dados_perguntas import PERGUNTAS_POR_FASE, TIPOS_DE_PERGUNTA
from tela_multipla_escolha import (
    LinhaCabecalho,
    TelaMultiplaEscolha,
    TemaMultiplaEscolha,
)


TEMA_PERGUNTAS = TemaMultiplaEscolha(
    cor_fundo=(20, 30, 50),
    cor_botao=(50, 85, 125),
    cor_botao_hover=(75, 135, 185),
    cor_resposta=(255, 255, 255),
    cor_letra=(255, 255, 255),
    largura_maxima_botao=900,
    margem_horizontal=60,
    altura_botao=70,
    espacamento_botoes=18,
    inicio_botoes_minimo=220,
    y_pergunta=140,
    tamanho_fonte_pergunta=44,
    tamanho_fonte_resposta=36,
    tamanho_fonte_letra=36,
    tamanho_fonte_rodape=28,
    cor_rodape=(190, 200, 215),
    margem_rodape=35,
    raio_borda=12,
)


class Perguntas:
    """Seleciona e exibe perguntas específicas de cada fase."""

    def __init__(self):
        self.tipos = TIPOS_DE_PERGUNTA
        self.listas = {
            fase: list(perguntas)
            for fase, perguntas in PERGUNTAS_POR_FASE.items()
        }
        # Os controles acompanham automaticamente as fases presentes nos dados.
        self.indices = {fase: 0 for fase in self.listas}
        self.tela_pergunta = TelaMultiplaEscolha(TEMA_PERGUNTAS)

        for lista in self.listas.values():
            random.shuffle(lista)

    def _proxima_pergunta(self, fase):
        """Seleciona a próxima pergunta e reembaralha ao completar um ciclo."""
        if fase not in self.listas:
            raise ValueError(f"Não existem perguntas para a fase {fase}")

        lista = self.listas[fase]
        if not lista:
            raise ValueError(f"A fase {fase} não possui perguntas cadastradas")

        indice = self.indices[fase]
        if indice and indice % len(lista) == 0:
            random.shuffle(lista)

        self.indices[fase] += 1
        return lista[indice % len(lista)]

    def fazer(self, tela, fase):
        """Mantém o contrato antigo: acerto, erro, saída ou reinício."""
        pergunta, respostas, correta = self._proxima_pergunta(fase)
        cabecalho = (
            LinhaCabecalho(
                f"FASE {fase} - {self.tipos[fase]}",
                tamanho_fonte=58,
                cor=(245, 190, 45),
                y=65,
            ),
        )
        return self.tela_pergunta.fazer(
            tela,
            pergunta,
            respostas,
            correta,
            cabecalho,
            "Responda com A, B, C ou D  |  TAB reinicia o jogo",
        )
