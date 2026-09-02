"""Configurações e reprodução da música do jogo."""

from pathlib import Path

import pygame


RAIZ_PROJETO = Path(__file__).resolve().parent.parent
PASTA_MUSICAS = RAIZ_PROJETO / "musica"
NOME_MUSICA = "SNCT2026JOGO.mp3"
CAMINHO_MUSICA = PASTA_MUSICAS / NOME_MUSICA
VOLUME_MUSICA = 0.30
REPETICOES = -1  # -1 mantém a música tocando em loop.


def iniciar_musica():
    """Carrega a faixa local configurada e inicia sua reprodução."""
    if not CAMINHO_MUSICA.is_file():
        print(f"Música não encontrada: {CAMINHO_MUSICA}")
        return False

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(str(CAMINHO_MUSICA))
        pygame.mixer.music.set_volume(VOLUME_MUSICA)
        pygame.mixer.music.play(REPETICOES)
    except pygame.error as erro:
        # O jogo continua funcionando mesmo em computadores sem saída de áudio.
        print(f"Não foi possível iniciar a música: {erro}")
        return False

    return True


def parar_musica():
    """Interrompe a música caso o sistema de áudio esteja disponível."""
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
