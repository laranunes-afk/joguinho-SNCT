import pygame


def desenhar_lista_controles(tela, largura, altura):
    """Exibe os controles em uma lista na lateral direita do menu."""
    largura_painel = min(340, max(280, largura // 4))
    painel = pygame.Rect(
        largura - largura_painel - 30,
        max(35, (altura - 410) // 2),
        largura_painel,
        410
    )

    pygame.draw.rect(tela, (17, 25, 43), painel, border_radius=18)
    pygame.draw.rect(tela, (95, 155, 205), painel, 3, border_radius=18)

    fonte_titulo = pygame.font.Font(None, 42)
    fonte_tecla = pygame.font.Font(None, 30)
    fonte_descricao = pygame.font.Font(None, 28)

    titulo = fonte_titulo.render("CONTROLES", True, (255, 215, 70))
    tela.blit(titulo, titulo.get_rect(center=(painel.centerx, painel.top + 42)))

    controles = [
        ("W /", "cima", "Pular"),
        ("A /", "esquerda", "Andar para esquerda"),
        ("D /", "direita", "Andar para direita"),
        ("TAB", None, "Reiniciar jogo"),
        ("ESC", None, "Sair do jogo"),
    ]

    setas_pixel = {
        "cima": ["00100", "01110", "11111", "00100", "00100"],
        "esquerda": ["00100", "01100", "11111", "01100", "00100"],
        "direita": ["00100", "00110", "11111", "00110", "00100"],
    }

    y = painel.top + 88
    for tecla, direcao, descricao in controles:
        caixa_tecla = pygame.Rect(painel.left + 20, y, 92, 46)
        pygame.draw.rect(tela, (48, 75, 112), caixa_tecla, border_radius=8)
        pygame.draw.rect(tela, (150, 205, 240), caixa_tecla, 2, border_radius=8)

        texto_tecla = fonte_tecla.render(tecla, True, (255, 255, 255))
        if direcao is None:
            tela.blit(texto_tecla, texto_tecla.get_rect(center=caixa_tecla.center))
        else:
            escala = 4
            largura_seta = 5 * escala
            espaco = 6
            largura_total = texto_tecla.get_width() + espaco + largura_seta
            inicio_x = caixa_tecla.centerx - largura_total // 2
            tela.blit(
                texto_tecla,
                texto_tecla.get_rect(midleft=(inicio_x, caixa_tecla.centery))
            )
            seta_x = inicio_x + texto_tecla.get_width() + espaco
            seta_y = caixa_tecla.centery - (5 * escala) // 2
            for linha, pixels in enumerate(setas_pixel[direcao]):
                for coluna, pixel in enumerate(pixels):
                    if pixel == "1":
                        pygame.draw.rect(
                            tela,
                            (255, 255, 255),
                            (
                                seta_x + coluna * escala,
                                seta_y + linha * escala,
                                escala,
                                escala
                            )
                        )

        texto_descricao = fonte_descricao.render(
            descricao,
            True,
            (225, 235, 245)
        )
        tela.blit(
            texto_descricao,
            texto_descricao.get_rect(
                midleft=(caixa_tecla.right + 14, caixa_tecla.centery)
            )
        )
        y += 61

def tela_inicial():
    """Exibe o menu inicial e retorna True quando JOGAR for escolhido."""
    pygame.init()
    tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    largura, altura = tela.get_size()
    pygame.display.set_caption("A Caçadora da Tumba da Cleópatra")
    clock = pygame.time.Clock()

    # Aparência do menu.
    cor_fundo = (25, 35, 55)
    cor_titulo = (255, 255, 255)
    cor_botao = (70, 130, 180)
    cor_botao_hover = (100, 160, 210)
    cor_texto_botao = (255, 255, 255)
    fonte_titulo = pygame.font.Font(None, 72)
    fonte_botao = pygame.font.Font(None, 55)

    texto_titulo = fonte_titulo.render(
        "A Caçadora da Tumba da Cleópatra",
        True,
        cor_titulo
    )
    rect_titulo = texto_titulo.get_rect(center=(largura // 2, altura // 3))

    botao_jogar = pygame.Rect(0, 0, 300, 90)
    botao_jogar.center = (largura // 2, altura // 2)

    # Mantém o menu aberto até o jogador iniciar ou sair.
    while True:
        pos_mouse = pygame.mouse.get_pos()
        mouse_sobre_botao = botao_jogar.collidepoint(pos_mouse)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return False
            clicou_em_jogar = (
                evento.type == pygame.MOUSEBUTTONDOWN
                and evento.button == 1
                and botao_jogar.collidepoint(evento.pos)
            )
            if clicou_em_jogar:
                return True

        tela.fill(cor_fundo)
        tela.blit(texto_titulo, rect_titulo)

        cor_atual = cor_botao_hover if mouse_sobre_botao else cor_botao
        pygame.draw.rect(tela, cor_atual, botao_jogar, border_radius=20)

        texto_jogar = fonte_botao.render("JOGAR", True, cor_texto_botao)
        tela.blit(texto_jogar, texto_jogar.get_rect(center=botao_jogar.center))

        desenhar_lista_controles(tela, largura, altura)
        pygame.display.flip()
        clock.tick(60)
