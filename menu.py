import pygame

def tela_inicial():

    pygame.init()

    # ========================================================
    # TELA CHEIA
    # ========================================================

    tela = pygame.display.set_mode(
        (0, 0),
        pygame.FULLSCREEN
    )

    largura, altura = tela.get_size()

    pygame.display.set_caption(
        "Menu Inicial"
    )

    clock = pygame.time.Clock()


    # ========================================================
    # CORES
    # ========================================================

    cor_fundo = (25, 35, 55)

    cor_titulo = (255, 255, 255)

    cor_botao = (70, 130, 180)

    cor_botao_hover = (100, 160, 210)

    cor_texto_botao = (255, 255, 255)


    # ========================================================
    # FONTES
    # ========================================================

    fonte_titulo = pygame.font.Font(
        None,
        90
    )

    fonte_botao = pygame.font.Font(
        None,
        55
    )


    # ========================================================
    # TÍTULO
    # ========================================================

    texto_titulo = fonte_titulo.render(
        "Meu Jogo",
        True,
        cor_titulo
    )

    rect_titulo = texto_titulo.get_rect(
        center=(
            largura // 2,
            altura // 3
        )
    )


    # ========================================================
    # BOTÃO JOGAR
    # ========================================================

    largura_botao = 300

    altura_botao = 90

    botao_jogar = pygame.Rect(
        0,
        0,
        largura_botao,
        altura_botao
    )

    botao_jogar.center = (
        largura // 2,
        altura // 2
    )


    # ========================================================
    # LOOP DO MENU
    # ========================================================

    rodando = True

    while rodando:

        pos_mouse = pygame.mouse.get_pos()

        mouse_sobre_botao = botao_jogar.collidepoint(
            pos_mouse
        )


        # ====================================================
        # EVENTOS
        # ====================================================

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                return False

            if (
                evento.type == pygame.KEYDOWN
                and evento.key == pygame.K_ESCAPE
            ):
                return False

            if evento.type == pygame.MOUSEBUTTONDOWN:

                if (
                    evento.button == 1
                    and botao_jogar.collidepoint(
                        evento.pos
                    )
                ):

                    # Informa que o jogador escolheu jogar.
                    return True


        # ====================================================
        # DESENHAR FUNDO
        # ====================================================

        tela.fill(
            cor_fundo
        )


        # ====================================================
        # DESENHAR TÍTULO
        # ====================================================

        tela.blit(
            texto_titulo,
            rect_titulo
        )


        # ====================================================
        # DESENHAR BOTÃO
        # ====================================================

        if mouse_sobre_botao:

            pygame.draw.rect(
                tela,
                cor_botao_hover,
                botao_jogar,
                border_radius=20
            )

        else:

            pygame.draw.rect(
                tela,
                cor_botao,
                botao_jogar,
                border_radius=20
            )


        texto_jogar = fonte_botao.render(
            "JOGAR",
            True,
            cor_texto_botao
        )

        rect_texto_jogar = texto_jogar.get_rect(
            center=botao_jogar.center
        )

        tela.blit(
            texto_jogar,
            rect_texto_jogar
        )


        # ====================================================
        # ATUALIZAR TELA
        # ====================================================

        pygame.display.flip()

        clock.tick(
            60
        )


    return False
