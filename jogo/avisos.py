import pygame

from recursos import renderizar_texto_contornado


class AvisosTemporarios:
    """Gerencia mensagens flutuantes sem acoplar essa logica a partida."""

    def __init__(self):
        self.itens = []

    def adicionar(self, personagem, texto, cor, duracao=1100):
        self.itens.append(
            {
                "texto": texto,
                "cor": cor,
                "x": personagem.rect.centerx,
                "y": personagem.rect.top - 12,
                "inicio": pygame.time.get_ticks(),
                "duracao": duracao,
            }
        )

    def transferir_para(self, personagem):
        """Ancora o aviso mais recente em uma nova personagem."""
        if not self.itens:
            return
        aviso = self.itens[-1]
        aviso["x"] = personagem.rect.centerx
        aviso["y"] = personagem.rect.top - 12
        aviso["inicio"] = pygame.time.get_ticks()

    def desenhar(self, tela, camera_x):
        agora = pygame.time.get_ticks()
        fonte = pygame.font.Font(None, 18)
        ativos = []
        for aviso in self.itens:
            decorrido = agora - aviso["inicio"]
            if decorrido >= aviso["duracao"]:
                continue
            progresso = decorrido / aviso["duracao"]
            base = renderizar_texto_contornado(
                fonte,
                aviso["texto"],
                aviso["cor"],
            )
            texto = pygame.transform.scale(
                base, (base.get_width() * 2, base.get_height() * 2)
            )
            texto.set_alpha(int(255 * (1 - progresso)))
            rect = texto.get_rect(
                midbottom=(
                    int(aviso["x"] - camera_x),
                    int(aviso["y"] - progresso * 38),
                )
            )
            tela.blit(texto, rect)
            ativos.append(aviso)
        self.itens = ativos
