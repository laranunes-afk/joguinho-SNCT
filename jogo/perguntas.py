import random

from layout_perguntas import LayoutPerguntas

from dados_perguntas import PERGUNTAS_POR_FASE, TIPOS_DE_PERGUNTA
from tela_multipla_escolha import (
    LinhaCabecalho,
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
        self.tela_pergunta = LayoutPerguntas(1)

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
        self.tela_pergunta.definir_fase(fase)
        cabecalho = (
            LinhaCabecalho(
                f"FASE {fase} - {self.tipos[fase]}",
                tamanho_fonte=58,
                cor=self.tela_pergunta.tema.cor_letra,
                y=65,
            ),
        )
        return self.tela_pergunta.fazer(
            tela,
            pergunta,
            respostas,
            correta,
            cabecalho,
            "SETAS + ENTER  |  Clique ou A-D respondem  |  TAB reinicia",
        )
