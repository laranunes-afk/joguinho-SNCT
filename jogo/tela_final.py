import pygame

from ranking import Ranking


class TelaFinal:
    """Exibe o resultado da partida e mantém o ranking local dos jogadores."""

    def mostrar(self, tela, segundos_decorridos, lupas_coletadas):
        """Retorna True para iniciar outra partida e False para sair."""
        largura, altura = tela.get_size()
        fonte_titulo = pygame.font.Font(None, 68)
        fonte_resumo = pygame.font.Font(None, 38)
        fonte_ranking = pygame.font.Font(None, 26)
        fonte_pequena = pygame.font.Font(None, 26)
        clock = pygame.time.Clock()

        repositorio = Ranking()
        ranking = repositorio.carregar()
        nome = ""
        salvo = False
        mensagem = "Digite seu nome e pressione Enter para salvar no ranking."

        campo_nome = pygame.Rect(largura // 2 - 220, 180, 440, 50)
        botao_novamente = pygame.Rect(largura // 2 - 240, altura - 85, 220, 55)
        botao_sair = pygame.Rect(largura // 2 + 20, altura - 85, 220, 55)

        def registrar_resultado():
            """Adiciona o resultado atual uma única vez ao ranking."""
            nonlocal ranking, salvo, mensagem

            if salvo:
                return

            ranking = repositorio.salvar_resultado(
                ranking,
                nome,
                segundos_decorridos,
                lupas_coletadas,
            )
            salvo = True
            mensagem = "Resultado salvo no Top 10!"

        while True:
            pos_mouse = pygame.mouse.get_pos()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return False

                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        return False
                    if evento.key == pygame.K_RETURN:
                        registrar_resultado()
                    elif evento.key == pygame.K_BACKSPACE and not salvo:
                        nome = nome[:-1]
                    elif not salvo and evento.unicode.isprintable() and len(nome) < 16:
                        nome += evento.unicode

                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    if botao_novamente.collidepoint(evento.pos):
                        registrar_resultado()
                        return True
                    if botao_sair.collidepoint(evento.pos):
                        registrar_resultado()
                        return False

            tela.fill((18, 35, 45))

            titulo = fonte_titulo.render("VOCÊ COMPLETOU O JOGO!", True, (80, 220, 120))
            tela.blit(titulo, titulo.get_rect(center=(largura // 2, 55)))

            minutos = segundos_decorridos // 60
            segundos = segundos_decorridos % 60
            resumo = fonte_resumo.render(
                (
                    f"Lupas: {lupas_coletadas}   |   "
                    f"Tempo: {minutos:02d}:{segundos:02d}   |   "
                    f"Pontos: {repositorio.calcular_pontos(lupas_coletadas, segundos_decorridos)}"
                ),
                True,
                (255, 255, 255)
            )
            tela.blit(resumo, resumo.get_rect(center=(largura // 2, 120)))

            instrucao = fonte_pequena.render(mensagem, True, (205, 215, 225))
            tela.blit(instrucao, instrucao.get_rect(center=(largura // 2, 150)))

            pygame.draw.rect(tela, (45, 75, 100), campo_nome, border_radius=10)
            pygame.draw.rect(tela, (120, 180, 220), campo_nome, 2, border_radius=10)
            texto_nome = fonte_resumo.render(
                nome if nome else "Seu nome",
                True,
                (255, 255, 255) if nome else (170, 185, 200)
            )
            tela.blit(texto_nome, texto_nome.get_rect(midleft=(campo_nome.left + 15, campo_nome.centery)))

            titulo_ranking = fonte_resumo.render("TOP 10", True, (255, 215, 55))
            tela.blit(titulo_ranking, titulo_ranking.get_rect(center=(largura // 2, 265)))

            inicio_y = 295
            for posicao, item in enumerate(ranking, start=1):
                minutos_item = item["tempo"] // 60
                segundos_item = item["tempo"] % 60
                linha = fonte_ranking.render(
                    (
                        f"{posicao:>2}. {item['nome']:<16}  "
                        f"{item['pontos']} pts  |  {item['lupas']} lupas  |  "
                        f"{minutos_item:02d}:{segundos_item:02d}"
                    ),
                    True,
                    (240, 245, 250)
                )
                tela.blit(linha, linha.get_rect(center=(largura // 2, inicio_y + (posicao - 1) * 22)))

            for botao, texto in (
                (botao_novamente, "JOGAR NOVAMENTE"),
                (botao_sair, "SAIR"),
            ):
                cor = (90, 155, 205) if botao.collidepoint(pos_mouse) else (55, 110, 160)
                pygame.draw.rect(tela, cor, botao, border_radius=12)
                rotulo = fonte_pequena.render(texto, True, (255, 255, 255))
                tela.blit(rotulo, rotulo.get_rect(center=botao.center))

            pygame.display.flip()
            clock.tick(60)
