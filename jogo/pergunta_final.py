from tela_multipla_escolha import (
    LinhaCabecalho,
    TelaMultiplaEscolha,
    TemaMultiplaEscolha,
)


TEMA_PERGUNTA_FINAL = TemaMultiplaEscolha(
    cor_fundo=(18, 24, 45),
    cor_botao=(48, 75, 112),
    cor_botao_hover=(80, 135, 180),
    cor_resposta=(255, 255, 255),
    cor_letra=(255, 215, 70),
    largura_maxima_botao=820,
    margem_horizontal=50,
    altura_botao=58,
    espacamento_botoes=18,
    inicio_botoes_minimo=225,
    y_pergunta=155,
    tamanho_fonte_pergunta=44,
    tamanho_fonte_resposta=38,
    tamanho_fonte_letra=50,
    tamanho_fonte_rodape=30,
    cor_rodape=(225, 230, 245),
    margem_rodape=28,
    cor_borda=(140, 195, 235),
    espessura_borda=2,
    raio_borda=9,
)


class PerguntaFinal:
    """Configura a tela reutilizável para as perguntas do desafio final."""

    def __init__(self, largura, altura, total_perguntas):
        # As dimensões continuam públicas por compatibilidade com o código atual.
        self.largura = largura
        self.altura = altura
        self.total_perguntas = total_perguntas
        self.tela_pergunta = TelaMultiplaEscolha(TEMA_PERGUNTA_FINAL)

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
