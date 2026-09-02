import pygame

from configuracoes_tela import TOTAL_FASES


COR_FUNDO = (25, 35, 55)
COR_TEXTO = (255, 255, 255)
COR_LUPAS = (255, 215, 55)
def _calcular_segundos(tempo_inicio):
    if tempo_inicio is None:
        return 0
    return (pygame.time.get_ticks() - tempo_inicio) // 1000


def _desenhar_indicador(tela, fonte, texto, cor, **ancora):
    """Desenha um texto sobre o painel arredondado comum ao HUD."""
    superficie = fonte.render(texto, True, cor)
    rect = superficie.get_rect(**ancora)
    pygame.draw.rect(
        tela,
        COR_FUNDO,
        rect.inflate(24, 14),
        border_radius=10,
    )
    tela.blit(superficie, rect)


def desenhar_hud(
    tela, largura, numero_fase, fonte_cronometro, fonte_fase,
    fonte_moedas, tempo_inicio, moedas_coletadas
):
    """Desenha as informações da partida e devolve o tempo decorrido."""
    segundos_decorridos = _calcular_segundos(tempo_inicio)
    minutos, segundos = divmod(segundos_decorridos, 60)

    _desenhar_indicador(
        tela,
        fonte_fase,
        f"FASE {numero_fase}/{TOTAL_FASES}",
        COR_TEXTO,
        topleft=(30, 25),
    )
    _desenhar_indicador(
        tela,
        fonte_cronometro,
        f"{minutos:02d}:{segundos:02d}",
        COR_TEXTO,
        midtop=(largura // 2, 25),
    )
    _desenhar_indicador(
        tela,
        fonte_moedas,
        f"LUPAS: {moedas_coletadas}",
        COR_LUPAS,
        midtop=(largura // 2, 88),
    )
    return segundos_decorridos
