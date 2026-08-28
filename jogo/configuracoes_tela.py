import pygame


TAMANHO_TELA = (0, 0)
TELA_CHEIA = True
FPS = 60
TITULO_JOGO = "A Caçadora da Tumba da Cleópatra"
MARGEM_CAMERA_PERSONAGEM = 0.35
RECUO_CAMERA_RETORNO = 30


def criar_tela():
    """Cria a janela e devolve a tela com suas dimensões reais."""
    flags = pygame.FULLSCREEN if TELA_CHEIA else 0
    tela = pygame.display.set_mode(TAMANHO_TELA, flags)
    pygame.display.set_caption(TITULO_JOGO)
    return tela, *tela.get_size()


def atualizar_camera_personagem(cenario, personagem):
    """Atualiza a câmera horizontal para acompanhar a personagem."""
    margem = cenario.largura * MARGEM_CAMERA_PERSONAGEM
    if personagem.rect.right - cenario.camera_x > cenario.largura - margem:
        nova_camera = personagem.rect.right - (cenario.largura - margem)
        cenario.camera_x = max(cenario.camera_x, nova_camera)
    elif personagem.rect.left - cenario.camera_x < margem:
        nova_camera = personagem.rect.left - margem
        cenario.camera_x = max(
            cenario.inicio_mundo,
            min(cenario.camera_x, nova_camera)
        )
    cenario.camera_x = max(cenario.inicio_mundo, cenario.camera_x)


def limitar_personagem_na_tela(personagem, camera_x, largura):
    """Mantém a personagem dentro das bordas visíveis da tela."""
    personagem.rect.left = max(personagem.rect.left, camera_x)
    personagem.rect.right = min(personagem.rect.right, camera_x + largura)
