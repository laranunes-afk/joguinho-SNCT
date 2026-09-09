import pygame

from configuracoes_tela import FPS


LETRAS_RESPOSTAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_CONTINUAR = object()


class TemaMultiplaEscolha:
    """Agrupa apenas as escolhas visuais de uma tela de perguntas."""

    def __init__(
        self,
        cor_fundo,
        cor_botao,
        cor_botao_hover,
        cor_resposta,
        cor_letra,
        largura_maxima_botao,
        margem_horizontal,
        altura_botao,
        espacamento_botoes,
        inicio_botoes_minimo,
        y_pergunta,
        tamanho_fonte_pergunta,
        tamanho_fonte_resposta,
        tamanho_fonte_letra,
        tamanho_fonte_rodape,
        cor_rodape,
        margem_rodape,
        cor_borda=None,
        espessura_borda=0,
        raio_borda=10,
    ):
        self.cor_fundo = cor_fundo
        self.cor_botao = cor_botao
        self.cor_botao_hover = cor_botao_hover
        self.cor_resposta = cor_resposta
        self.cor_letra = cor_letra
        self.largura_maxima_botao = largura_maxima_botao
        self.margem_horizontal = margem_horizontal
        self.altura_botao = altura_botao
        self.espacamento_botoes = espacamento_botoes
        self.inicio_botoes_minimo = inicio_botoes_minimo
        self.y_pergunta = y_pergunta
        self.tamanho_fonte_pergunta = tamanho_fonte_pergunta
        self.tamanho_fonte_resposta = tamanho_fonte_resposta
        self.tamanho_fonte_letra = tamanho_fonte_letra
        self.tamanho_fonte_rodape = tamanho_fonte_rodape
        self.cor_rodape = cor_rodape
        self.margem_rodape = margem_rodape
        self.cor_borda = cor_borda
        self.espessura_borda = espessura_borda
        self.raio_borda = raio_borda


class LinhaCabecalho:
    """Texto centralizado que aparece acima da pergunta."""

    def __init__(self, texto, tamanho_fonte, cor, y):
        self.texto = texto
        self.tamanho_fonte = tamanho_fonte
        self.cor = cor
        self.y = y


class TelaMultiplaEscolha:
    """Controla eventos e desenho comuns a qualquer pergunta de alternativas."""

    def __init__(self, tema):
        self.tema = tema
        self._fontes = {}
        self._selecionada = 0

    def _fonte(self, tamanho):
        """Reaproveita fontes, evitando recriá-las durante o laço da tela."""
        if tamanho not in self._fontes:
            self._fontes[tamanho] = pygame.font.Font(None, tamanho)
        return self._fontes[tamanho]

    def _criar_botoes(self, largura, altura, quantidade):
        largura_disponivel = max(1, largura - self.tema.margem_horizontal * 2)
        largura_botao = min(self.tema.largura_maxima_botao, largura_disponivel)
        inicio_y = max(self.tema.inicio_botoes_minimo, altura // 3)
        margem_inferior = max(self.tema.margem_rodape + 32, 64)
        espaco_disponivel = max(quantidade, altura - margem_inferior - inicio_y)
        espacamento = self.tema.espacamento_botoes
        altura_botao = self.tema.altura_botao

        altura_ideal = (
            quantidade * altura_botao
            + max(0, quantidade - 1) * espacamento
        )
        if altura_ideal > espaco_disponivel:
            espacamento = min(espacamento, 8)
            altura_botao = max(
                28,
                (
                    espaco_disponivel
                    - max(0, quantidade - 1) * espacamento
                ) // quantidade,
            )

        passo_vertical = altura_botao + espacamento

        return [
            pygame.Rect(
                (largura - largura_botao) // 2,
                inicio_y + indice * passo_vertical,
                largura_botao,
                altura_botao,
            )
            for indice in range(quantidade)
        ]

    def _mapear_teclas(self, quantidade):
        return {
            getattr(pygame, f"K_{letra.lower()}"): indice
            for indice, letra in enumerate(LETRAS_RESPOSTAS[:quantidade])
        }

    def _validar_respostas(self, respostas, correta):
        if not respostas:
            raise ValueError("A pergunta precisa ter ao menos uma resposta")
        if len(respostas) > len(LETRAS_RESPOSTAS):
            raise ValueError("Há mais respostas do que letras disponíveis")
        if not 0 <= correta < len(respostas):
            raise ValueError("O índice da resposta correta é inválido")

    def fazer(
        self,
        tela,
        pergunta,
        respostas,
        correta,
        cabecalho,
        rodape,
    ):
        """Retorna True, False, None ou ``reiniciar``, como as telas antigas."""
        self._validar_respostas(respostas, correta)
        largura, altura = tela.get_size()
        botoes = self._criar_botoes(largura, altura, len(respostas))
        teclas = self._mapear_teclas(len(respostas))
        self._selecionada = 0
        textos_fixos = self._preparar_textos(
            pergunta,
            respostas,
            cabecalho,
            rodape,
        )
        clock = pygame.time.Clock()

        while True:
            pos_mouse = pygame.mouse.get_pos()
            resultado = self._processar_eventos(botoes, teclas, correta)
            if resultado is not _CONTINUAR:
                return resultado

            self._desenhar(tela, botoes, pos_mouse, textos_fixos, altura)
            pygame.display.flip()
            clock.tick(FPS)

    def _processar_eventos(self, botoes, teclas, correta):
        """Traduz eventos em uma resposta ou mantém a tela aberta."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return None

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return None
                if evento.key == pygame.K_TAB:
                    return "reiniciar"
                if evento.key in (pygame.K_UP, pygame.K_LEFT):
                    self._selecionada = (self._selecionada - 1) % len(botoes)
                elif evento.key in (pygame.K_DOWN, pygame.K_RIGHT):
                    self._selecionada = (self._selecionada + 1) % len(botoes)
                if evento.key in teclas:
                    return teclas[evento.key] == correta
                if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return self._selecionada == correta

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for indice, botao in enumerate(botoes):
                    if botao.collidepoint(evento.pos):
                        return indice == correta

        return _CONTINUAR

    def _preparar_textos(self, pergunta, respostas, cabecalho, rodape):
        linhas_cabecalho = [
            (
                self._fonte(linha.tamanho_fonte).render(
                    linha.texto,
                    True,
                    linha.cor,
                ),
                linha.y,
            )
            for linha in cabecalho
        ]
        texto_pergunta = self._fonte(
            self.tema.tamanho_fonte_pergunta
        ).render(pergunta, True, (255, 255, 255))
        texto_rodape = self._fonte(self.tema.tamanho_fonte_rodape).render(
            rodape,
            True,
            self.tema.cor_rodape,
        )

        respostas_renderizadas = []
        for indice, resposta in enumerate(respostas):
            letra = self._fonte(self.tema.tamanho_fonte_letra).render(
                f"{LETRAS_RESPOSTAS[indice]})",
                True,
                self.tema.cor_letra,
            )
            texto = self._fonte(self.tema.tamanho_fonte_resposta).render(
                resposta,
                True,
                self.tema.cor_resposta,
            )
            respostas_renderizadas.append((letra, texto))

        return linhas_cabecalho, texto_pergunta, respostas_renderizadas, texto_rodape

    def _desenhar(self, tela, botoes, mouse, textos_fixos, altura):
        cabecalho, pergunta, respostas, rodape = textos_fixos
        tela.fill(self.tema.cor_fundo)

        for texto, y in cabecalho:
            tela.blit(texto, texto.get_rect(center=(tela.get_width() // 2, y)))

        tela.blit(
            pergunta,
            pergunta.get_rect(center=(tela.get_width() // 2, self.tema.y_pergunta)),
        )

        for indice, (botao, textos_resposta) in enumerate(zip(botoes, respostas)):
            self._desenhar_botao(
                tela,
                botao,
                textos_resposta,
                mouse,
                indice == self._selecionada,
            )

        tela.blit(
            rodape,
            rodape.get_rect(
                center=(tela.get_width() // 2, altura - self.tema.margem_rodape)
            ),
        )

    def _desenhar_botao(self, tela, botao, textos, mouse, selecionado):
        cor = (
            self.tema.cor_botao_hover
            if selecionado or botao.collidepoint(mouse)
            else self.tema.cor_botao
        )
        pygame.draw.rect(tela, cor, botao, border_radius=self.tema.raio_borda)

        if self.tema.cor_borda and self.tema.espessura_borda:
            pygame.draw.rect(
                tela,
                self.tema.cor_borda,
                botao,
                width=self.tema.espessura_borda,
                border_radius=self.tema.raio_borda,
            )

        letra, resposta = textos
        separacao = 12
        largura_textos = letra.get_width() + separacao + resposta.get_width()
        inicio_x = botao.centerx - largura_textos // 2
        tela.blit(letra, letra.get_rect(midleft=(inicio_x, botao.centery)))
        tela.blit(
            resposta,
            resposta.get_rect(
                midleft=(
                    inicio_x + letra.get_width() + separacao,
                    botao.centery,
                )
            ),
        )
