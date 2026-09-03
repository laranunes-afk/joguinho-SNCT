from dataclasses import dataclass, field

import pygame

from recursos import renderizar_texto_contornado


@dataclass
class AvisoTemporario:
    """Dados necessários para animar uma mensagem sobre o cenário."""

    texto: str
    cor: tuple[int, int, int]
    x: int
    y: int
    inicio: int
    duracao: int
    superficie: pygame.Surface = field(repr=False)


class AvisosTemporarios:
    """Gerencia mensagens flutuantes sem acoplar essa logica a partida."""

    TAMANHO_FONTE = 18
    ESCALA_TEXTO = 2
    DISTANCIA_SUBIDA = 38

    def __init__(self):
        self.itens: list[AvisoTemporario] = []
        self.fonte = pygame.font.Font(None, self.TAMANHO_FONTE)

    def adicionar(self, personagem, texto, cor, duracao=1100):
        """Cria um aviso ancorado na posição atual da personagem."""
        base = renderizar_texto_contornado(self.fonte, texto, cor)
        superficie = pygame.transform.scale(
            base,
            (
                base.get_width() * self.ESCALA_TEXTO,
                base.get_height() * self.ESCALA_TEXTO,
            ),
        )
        self.itens.append(
            AvisoTemporario(
                texto=texto,
                cor=cor,
                x=personagem.rect.centerx,
                y=personagem.rect.top - 12,
                inicio=pygame.time.get_ticks(),
                duracao=duracao,
                superficie=superficie,
            )
        )

    def transferir_para(self, personagem):
        """Ancora o aviso mais recente em uma nova personagem."""
        if not self.itens:
            return
        aviso = self.itens[-1]
        aviso.x = personagem.rect.centerx
        aviso.y = personagem.rect.top - 12
        aviso.inicio = pygame.time.get_ticks()

    def desenhar(self, tela, camera_x):
        """Anima, desenha e descarta os avisos que já expiraram."""
        agora = pygame.time.get_ticks()
        ativos = []
        for aviso in self.itens:
            decorrido = agora - aviso.inicio
            if decorrido >= aviso.duracao:
                continue

            progresso = decorrido / aviso.duracao
            texto = aviso.superficie.copy()
            texto.set_alpha(int(255 * (1 - progresso)))
            rect = texto.get_rect(
                midbottom=(
                    int(aviso.x - camera_x),
                    int(aviso.y - progresso * self.DISTANCIA_SUBIDA),
                )
            )
            tela.blit(texto, rect)
            ativos.append(aviso)
        self.itens = ativos
