import random

import pygame

from recursos import carregar_imagem


class Pedra:
    """Pedra posicionada no chão do cenário."""

    def __init__(self, x, y_chao):
        largura = random.randint(60, 80)
        altura = random.randint(45, 60)

        self.rect = pygame.Rect(
            x,
            y_chao - altura,
            largura,
            altura
        )
        imagem_original = carregar_imagem(
            "Pedra-melhorada.png",
            fundo_transparente=True
        )
        limites = pygame.mask.from_surface(
            imagem_original
        ).get_bounding_rects()
        area_pedra = limites[0].unionall(limites)
        imagem_recortada = imagem_original.subsurface(area_pedra).copy()
        self.imagem = pygame.transform.scale(
            imagem_recortada,
            (largura, altura)
        )

    def desenhar(self, tela, camera_x):
        pedra_na_tela = self.rect.copy()
        pedra_na_tela.x -= int(camera_x)

        tela.blit(self.imagem, pedra_na_tela)


class Buraco:
    """Abertura no chão que faz o personagem cair."""

    def __init__(self, x, y_chao):
        largura = random.randint(110, 150)
        self.rect = pygame.Rect(x, y_chao, largura, 2000)
        imagem_original = carregar_imagem(
            "Buraco.png",
            fundo_transparente=True
        )
        limites = pygame.mask.from_surface(
            imagem_original
        ).get_bounding_rects()
        area_buraco = limites[0].unionall(limites)
        imagem_recortada = imagem_original.subsurface(area_buraco).copy()
        self.imagem = pygame.transform.scale(
            imagem_recortada,
            (largura, 42)
        )

    def desenhar(self, tela, camera_x):
        rect_imagem = self.imagem.get_rect(
            midtop=(
                self.rect.centerx - int(camera_x),
                self.rect.y
            )
        )
        tela.blit(self.imagem, rect_imagem)


class Obstaculos:
    """Cria e controla pedras e buracos espalhados pelo cenário infinito."""

    def __init__(self, largura_tela, y_chao, areas_livres=None):
        self.largura_tela = largura_tela
        self.y_chao = y_chao
        self.pedras = []
        self.buracos = []
        self.areas_livres = areas_livres or []
        self.proximo_eh_buraco = True

        # Mantém a região inicial livre para o personagem.
        self.proxima_posicao = random.randint(450, 700)
        self.atualizar(0)

    def atualizar(self, camera_x):
        limite_geracao = camera_x + self.largura_tela * 2

        while self.proxima_posicao < limite_geracao:
            # Buracos são largos o bastante para exigir um pulo, mas ainda
            # podem ser atravessados com o alcance normal do personagem.
            obstaculo = (
                Buraco(self.proxima_posicao, self.y_chao)
                if self.proximo_eh_buraco or random.random() < 0.35
                else Pedra(self.proxima_posicao, self.y_chao)
            )
            self.proximo_eh_buraco = False

            if isinstance(obstaculo, Buraco):
                # O rect do buraco começa abaixo do chão; para proteger os
                # checkpoints, sua área segura precisa considerar a superfície.
                area_do_buraco = pygame.Rect(
                    obstaculo.rect.x,
                    0,
                    obstaculo.rect.width,
                    self.y_chao
                )
                obstaculo_em_area_livre = any(
                    area_do_buraco.colliderect(area)
                    for area in self.areas_livres
                )
            else:
                obstaculo_em_area_livre = any(
                    obstaculo.rect.colliderect(area)
                    for area in self.areas_livres
                )

            if not obstaculo_em_area_livre:
                if isinstance(obstaculo, Buraco):
                    self.buracos.append(obstaculo)
                else:
                    self.pedras.append(obstaculo)

            # O espaço permite que o jogador pule cada pedra.
            self.proxima_posicao += random.randint(350, 700)

    def colidiu_com(self, personagem):
        return any(
            personagem.rect.colliderect(pedra.rect)
            for pedra in self.pedras
        )

    def personagem_esta_sobre_buraco(self, personagem):
        return any(
            personagem.rect.right > buraco.rect.left
            and personagem.rect.left < buraco.rect.right
            for buraco in self.buracos
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

        for buraco in self.buracos:
            if (
                buraco.rect.right > limite_esquerdo
                and buraco.rect.left < limite_direito
            ):
                buraco.desenhar(tela, camera_x)
