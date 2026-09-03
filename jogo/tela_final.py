import pygame

from configuracoes_tela import FPS
from ranking import Ranking


class _FontesTelaFinal:
    def __init__(self, titulo, resumo, pequena):
        self.titulo = titulo
        self.resumo = resumo
        self.pequena = pequena


class _LayoutTelaFinal:
    def __init__(self, campo_nome, botao_novamente, botao_sair):
        self.campo_nome = campo_nome
        self.botao_novamente = botao_novamente
        self.botao_sair = botao_sair


class _EstadoTelaFinal:
    def __init__(self, ranking, nome="", salvo=False, mensagem=None):
        self.ranking = ranking
        self.nome = nome
        self.salvo = salvo
        self.mensagem = mensagem or (
            "Digite seu nome e pressione Enter para salvar no ranking."
        )


class TelaFinal:
    """Exibe o resultado da partida e mantém o ranking local dos jogadores."""

    LIMITE_NOME = 16

    def _criar_fontes(self):
        return _FontesTelaFinal(
            titulo=pygame.font.Font(None, 68),
            resumo=pygame.font.Font(None, 38),
            pequena=pygame.font.Font(None, 26),
        )

    def _criar_layout(self, largura, altura):
        return _LayoutTelaFinal(
            campo_nome=pygame.Rect(largura // 2 - 220, 180, 440, 50),
            botao_novamente=pygame.Rect(
                largura // 2 - 240,
                altura - 85,
                220,
                55,
            ),
            botao_sair=pygame.Rect(
                largura // 2 + 20,
                altura - 85,
                220,
                55,
            ),
        )

    def _formatar_tempo(self, total_segundos):
        minutos, segundos = divmod(total_segundos, 60)
        return f"{minutos:02d}:{segundos:02d}"

    def _registrar_resultado(
        self,
        estado,
        repositorio,
        segundos_decorridos,
        lupas_coletadas,
    ):
        """Registra o resultado no máximo uma vez e informa eventuais falhas."""
        if estado.salvo:
            return

        try:
            estado.ranking = repositorio.salvar_resultado(
                estado.ranking,
                estado.nome,
                segundos_decorridos,
                lupas_coletadas,
            )
        except (OSError, TypeError, ValueError):
            estado.mensagem = "Não foi possível salvar o ranking."
            return

        estado.salvo = True
        if repositorio.ultimo_resultado_entrou_no_top_10:
            estado.mensagem = "Resultado salvo no Top 10!"
        else:
            estado.mensagem = "Resultado não entrou no Top 10."

    def _tratar_evento(
        self,
        evento,
        estado,
        layout,
        repositorio,
        segundos_decorridos,
        lupas_coletadas,
    ):
        """Retorna True/False ao encerrar a tela e None para continuar."""
        if evento.type == pygame.QUIT:
            return False

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return False
            if evento.key == pygame.K_RETURN:
                self._registrar_resultado(
                    estado,
                    repositorio,
                    segundos_decorridos,
                    lupas_coletadas,
                )
            elif evento.key == pygame.K_BACKSPACE and not estado.salvo:
                estado.nome = estado.nome[:-1]
            elif (
                not estado.salvo
                and evento.unicode.isprintable()
                and len(estado.nome) < self.LIMITE_NOME
            ):
                estado.nome += evento.unicode

        clicou = evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1
        if clicou and layout.botao_novamente.collidepoint(evento.pos):
            self._registrar_resultado(
                estado,
                repositorio,
                segundos_decorridos,
                lupas_coletadas,
            )
            return True
        if clicou and layout.botao_sair.collidepoint(evento.pos):
            self._registrar_resultado(
                estado,
                repositorio,
                segundos_decorridos,
                lupas_coletadas,
            )
            return False
        return None

    def _desenhar_resumo(
        self,
        tela,
        largura,
        fontes,
        repositorio,
        estado,
        segundos_decorridos,
        lupas_coletadas,
    ):
        titulo = fontes.titulo.render(
            "VOCÊ COMPLETOU O JOGO!",
            True,
            (80, 220, 120),
        )
        tela.blit(titulo, titulo.get_rect(center=(largura // 2, 55)))

        resumo = fontes.resumo.render(
            (
                f"Lupas: {lupas_coletadas}   |   "
                f"Tempo: {self._formatar_tempo(segundos_decorridos)}   |   "
                f"Pontos: {repositorio.calcular_pontos(lupas_coletadas, segundos_decorridos)}"
            ),
            True,
            (255, 255, 255),
        )
        tela.blit(resumo, resumo.get_rect(center=(largura // 2, 120)))

        instrucao = fontes.pequena.render(
            estado.mensagem,
            True,
            (205, 215, 225),
        )
        tela.blit(instrucao, instrucao.get_rect(center=(largura // 2, 150)))

    def _desenhar_campo_nome(self, tela, fontes, layout, estado):
        campo_nome = layout.campo_nome
        pygame.draw.rect(tela, (45, 75, 100), campo_nome, border_radius=10)
        pygame.draw.rect(
            tela,
            (120, 180, 220),
            campo_nome,
            2,
            border_radius=10,
        )
        texto_nome = fontes.resumo.render(
            estado.nome if estado.nome else "Seu nome",
            True,
            (255, 255, 255) if estado.nome else (170, 185, 200),
        )
        tela.blit(
            texto_nome,
            texto_nome.get_rect(
                midleft=(campo_nome.left + 15, campo_nome.centery),
            ),
        )

    def _desenhar_ranking(self, tela, largura, fontes, ranking):
        titulo = fontes.resumo.render("TOP 10", True, (255, 215, 55))
        tela.blit(titulo, titulo.get_rect(center=(largura // 2, 265)))

        inicio_y = 295
        for posicao, item in enumerate(ranking[: Ranking.LIMITE], start=1):
            linha = fontes.pequena.render(
                (
                    f"{posicao:>2}. {item['nome']:<16}  "
                    f"{item['pontos']} pts  |  {item['lupas']} lupas  |  "
                    f"{self._formatar_tempo(item['tempo'])}"
                ),
                True,
                (240, 245, 250),
            )
            tela.blit(
                linha,
                linha.get_rect(
                    center=(largura // 2, inicio_y + (posicao - 1) * 22),
                ),
            )

    def _desenhar_botoes(self, tela, fontes, layout, pos_mouse):
        for botao, texto in (
            (layout.botao_novamente, "JOGAR NOVAMENTE"),
            (layout.botao_sair, "SAIR"),
        ):
            cor = (
                (90, 155, 205)
                if botao.collidepoint(pos_mouse)
                else (55, 110, 160)
            )
            pygame.draw.rect(tela, cor, botao, border_radius=12)
            rotulo = fontes.pequena.render(texto, True, (255, 255, 255))
            tela.blit(rotulo, rotulo.get_rect(center=botao.center))

    def _desenhar(
        self,
        tela,
        largura,
        fontes,
        layout,
        repositorio,
        estado,
        segundos_decorridos,
        lupas_coletadas,
        pos_mouse,
    ):
        tela.fill((18, 35, 45))
        self._desenhar_resumo(
            tela,
            largura,
            fontes,
            repositorio,
            estado,
            segundos_decorridos,
            lupas_coletadas,
        )
        self._desenhar_campo_nome(tela, fontes, layout, estado)
        self._desenhar_ranking(tela, largura, fontes, estado.ranking)
        self._desenhar_botoes(tela, fontes, layout, pos_mouse)

    def mostrar(self, tela, segundos_decorridos, lupas_coletadas):
        """Retorna True para iniciar outra partida e False para sair."""
        largura, altura = tela.get_size()
        fontes = self._criar_fontes()
        layout = self._criar_layout(largura, altura)
        repositorio = Ranking()
        estado = _EstadoTelaFinal(ranking=repositorio.carregar())
        clock = pygame.time.Clock()

        while True:
            for evento in pygame.event.get():
                resultado = self._tratar_evento(
                    evento,
                    estado,
                    layout,
                    repositorio,
                    segundos_decorridos,
                    lupas_coletadas,
                )
                if resultado is not None:
                    return resultado

            self._desenhar(
                tela,
                largura,
                fontes,
                layout,
                repositorio,
                estado,
                segundos_decorridos,
                lupas_coletadas,
                pygame.mouse.get_pos(),
            )
            pygame.display.flip()
            clock.tick(FPS)
