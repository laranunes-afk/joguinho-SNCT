"""Configurações e reprodução da música do jogo."""

from pathlib import Path

import pygame


# Link da pasta de músicas no Git (não aponta diretamente para o MP3).
LINK_MUSICA_GIT = (
    "https://github.com/laranunes-afk/joguinho-SNCT/tree/main/musica"
)

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
PASTA_MUSICAS = RAIZ_PROJETO / "musica"
NOME_MUSICA = "SNCT2026JOGO.mp3"
VOLUME_MUSICA = 0.35
REPETICOES = -1  # -1 mantém a música tocando em loop.


def iniciar_musica():
    """Carrega a faixa local configurada e inicia sua reprodução."""
    caminho_musica = PASTA_MUSICAS / NOME_MUSICA

    if not caminho_musica.is_file():
        print(f"Música não encontrada: {caminho_musica}")
        return False

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(caminho_musica)
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
