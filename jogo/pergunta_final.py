from layout_perguntas import LayoutPerguntas
from tela_multipla_escolha import (
    LinhaCabecalho,
)




class PerguntaFinal:
    """Configura a tela reutilizável para as perguntas do desafio final."""

    def __init__(self, largura, altura, total_perguntas):
        # As dimensões continuam públicas por compatibilidade com o código atual.
        self.largura = largura
        self.altura = altura
        self.total_perguntas = total_perguntas
        self.tela_pergunta = LayoutPerguntas(4)

    def fazer(self, tela, dados, numero):
        pergunta, respostas, correta = dados
        cabecalho = (
            LinhaCabecalho(
                f"PERGUNTA DIFICIL {numero}/{self.total_perguntas}",
                tamanho_fonte=52,
                cor=(255, 215, 70),
                y=62,
            ),
            LinhaCabecalho(
                "SE ERRAR, VOCE VOLTA AO INICIO DA FASE 1",
                tamanho_fonte=30,
                cor=(255, 145, 125),
                y=105,
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
