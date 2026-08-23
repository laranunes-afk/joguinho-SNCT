import random

import pygame


class Pedra:
    """Pedra posicionada no chão do cenário."""

    def __init__(self, x, y_chao):
        largura = random.randint(45, 75)
        altura = random.randint(35, 60)

        self.rect = pygame.Rect(
            x,
            y_chao - altura,
            largura,
            altura
        )

    def desenhar(self, tela, camera_x):
        pedra_na_tela = self.rect.copy()
        pedra_na_tela.x -= int(camera_x)

        pontos = [
            (pedra_na_tela.left, pedra_na_tela.bottom),
            (pedra_na_tela.left + pedra_na_tela.width // 6,
             pedra_na_tela.top + pedra_na_tela.height // 3),
            (pedra_na_tela.centerx, pedra_na_tela.top),
            (pedra_na_tela.right - pedra_na_tela.width // 6,
             pedra_na_tela.top + pedra_na_tela.height // 4),
            (pedra_na_tela.right, pedra_na_tela.bottom),
        ]

        pygame.draw.polygon(
            tela,
            (95, 95, 100),
            pontos
        )

        pygame.draw.line(
            tela,
            (135, 135, 140),
            pontos[1],
            pontos[2],
            3
        )


class Obstaculos:
    """Cria e controla pedras espalhadas pelo cenário infinito."""

    def __init__(self, largura_tela, y_chao, areas_livres=None):
        self.largura_tela = largura_tela
        self.y_chao = y_chao
        self.pedras = []
        self.areas_livres = areas_livres or []

        # Mantém a região inicial livre para o personagem.
        self.proxima_posicao = random.randint(450, 700)
        self.atualizar(0)

    def atualizar(self, camera_x):
        limite_geracao = camera_x + self.largura_tela * 2

        while self.proxima_posicao < limite_geracao:
            pedra = Pedra(
                self.proxima_posicao,
                self.y_chao
            )

            pedra_em_area_livre = any(
                pedra.rect.colliderect(area)
                for area in self.areas_livres
            )

            if not pedra_em_area_livre:
                self.pedras.append(pedra)

            # O espaço permite que o jogador pule cada pedra.
            self.proxima_posicao += random.randint(350, 700)

    def colidiu_com(self, personagem):
        return any(
            personagem.rect.colliderect(pedra.rect)
            for pedra in self.pedras
        )

    def desenhar(self, tela, camera_x):
        limite_esquerdo = camera_x - 100
        limite_direito = camera_x + self.largura_tela + 100

        for pedra in self.pedras:
            pedra_visivel = (
                pedra.rect.right > limite_esquerdo
                and pedra.rect.left < limite_direito
            )

            if pedra_visivel:
                pedra.desenhar(
                    tela,
                    camera_x
                )
