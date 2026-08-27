import pygame


def desenhar_hud(
    tela, largura, numero_fase, fonte_cronometro, fonte_fase,
    fonte_moedas, tempo_inicio, moedas_coletadas
):
    """Desenha as informações da partida e devolve o tempo decorrido."""
    segundos_decorridos = 0 if tempo_inicio is None else (
        pygame.time.get_ticks() - tempo_inicio
    ) // 1000
    minutos, segundos = divmod(segundos_decorridos, 60)

    texto_fase = fonte_fase.render(
        f"FASE {numero_fase}/3", True, (255, 255, 255)
    )
    rect_fase = texto_fase.get_rect(topleft=(30, 25))
    pygame.draw.rect(
        tela, (25, 35, 55), rect_fase.inflate(24, 14), border_radius=10
    )
    tela.blit(texto_fase, rect_fase)

    texto_cronometro = fonte_cronometro.render(
        f"{minutos:02d}:{segundos:02d}", True, (255, 255, 255)
    )
    rect_cronometro = texto_cronometro.get_rect(midtop=(largura // 2, 25))
    pygame.draw.rect(
        tela, (25, 35, 55), rect_cronometro.inflate(24, 14), border_radius=10
    )
    tela.blit(texto_cronometro, rect_cronometro)

    texto_moedas = fonte_moedas.render(
        f"LUPAS: {moedas_coletadas}", True, (255, 215, 55)
    )
    rect_moedas = texto_moedas.get_rect(midtop=(largura // 2, 88))
    pygame.draw.rect(
        tela, (25, 35, 55), rect_moedas.inflate(24, 14), border_radius=10
    )
    tela.blit(texto_moedas, rect_moedas)
    return segundos_decorridos
