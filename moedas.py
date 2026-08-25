import random

import pygame

from recursos import carregar_imagem


class Moeda:
    """Moeda coletável posicionada próxima ao chão."""

    def __init__(self, x, y_chao):
        self.rect = pygame.Rect(
            x,
            y_chao - 48,
            28,
            28
        )
        imagem_original = carregar_imagem(
            "Lupa.png",
            fundo_transparente=True
        )
        limites = pygame.mask.from_surface(
            imagem_original
        ).get_bounding_rects()
        area_lupa = limites[0].unionall(limites)
        imagem_recortada = imagem_original.subsurface(area_lupa).copy()
        self.imagem = pygame.transform.scale(imagem_recortada, (28, 28))

    def desenhar(self, tela, camera_x):
        moeda_na_tela = self.rect.copy()
        moeda_na_tela.x -= int(camera_x)

        tela.blit(
            self.imagem,
            self.imagem.get_rect(
                midbottom=(moeda_na_tela.centerx, moeda_na_tela.bottom + 15)
            )
        )


class Moedas:
    """Gera, desenha e detecta a coleta das moedas."""

    def __init__(self, largura_tela, y_chao, areas_livres=None):
        self.largura_tela = largura_tela
        self.y_chao = y_chao
        self.areas_livres = areas_livres or []
        self.moedas = []
        self.proxima_posicao = random.randint(220, 360)

    def atualizar(self, camera_x, pedras, buracos=()):
        limite_geracao = camera_x + self.largura_tela * 2

        while self.proxima_posicao < limite_geracao:
            moeda = Moeda(
                self.proxima_posicao,
                self.y_chao
            )

            perto_de_checkpoint = any(
                moeda.rect.colliderect(area)
                for area in self.areas_livres
            )
            perto_de_pedra = any(
                moeda.rect.inflate(70, 30).colliderect(pedra.rect)
                for pedra in pedras
            )
            sobre_buraco = any(
                moeda.rect.inflate(20, 20).colliderect(buraco.rect)
                for buraco in buracos
            )

            if not perto_de_checkpoint and not perto_de_pedra and not sobre_buraco:
                self.moedas.append(moeda)

            self.proxima_posicao += random.randint(230, 430)

    def coletar(self, personagem):
        moedas_restantes = []
        quantidade_coletada = 0

        for moeda in self.moedas:
            if personagem.rect.colliderect(moeda.rect):
                quantidade_coletada += 1
            else:
                moedas_restantes.append(moeda)

        self.moedas = moedas_restantes
        return quantidade_coletada

    def desenhar(self, tela, camera_x):
        limite_esquerdo = camera_x - 50
        limite_direito = camera_x + self.largura_tela + 50

        for moeda in self.moedas:
            if (
                moeda.rect.right > limite_esquerdo
                and moeda.rect.left < limite_direito
            ):
                moeda.desenhar(
                    tela,
                    camera_x
                )
