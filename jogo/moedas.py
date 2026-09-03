import random

import pygame

from cenario import esta_visivel, manter_objetos_proximos
from recursos import carregar_imagem_recortada


TAMANHO_LUPA = 28
DISTANCIA_LUPA_DO_CHAO = 5
POSICAO_INICIAL = (220, 360)
ESPACO_ENTRE_LUPAS = (230, 430)
TELAS_PARA_GERAR = 2
MARGEM_BURACO = (20, 20)
MARGEM_PEDRA = (70, 30)
MARGEM_VISIBILIDADE = 50


class Moeda:
    """Lupa coletável mantida com o nome antigo por compatibilidade."""

    _imagem = None

    def __init__(self, x, y_chao):
        """Cria uma lupa com imagem e hitbox na mesma posição."""
        self.rect = pygame.Rect(
            x,
            y_chao - TAMANHO_LUPA - DISTANCIA_LUPA_DO_CHAO,
            TAMANHO_LUPA,
            TAMANHO_LUPA,
        )
        if Moeda._imagem is None:
            Moeda._imagem = carregar_imagem_recortada(
                "Lupa.png",
                (TAMANHO_LUPA, TAMANHO_LUPA),
            )
        self.imagem = Moeda._imagem

    def desenhar(self, tela, camera_x):
        """Desenha a lupa exatamente sobre sua hitbox."""
        moeda_na_tela = self.rect.copy()
        moeda_na_tela.x -= int(camera_x)
        tela.blit(self.imagem, moeda_na_tela)


class Moedas:
    """Gera, desenha e detecta a coleta das lupas."""

    def __init__(self, largura_tela, y_chao, areas_livres=None):
        """Prepara a coleção e a geração progressiva de lupas."""
        self.largura_tela = largura_tela
        self.y_chao = y_chao
        self.areas_livres = areas_livres or []
        self.moedas = []
        self.proxima_posicao = random.randint(*POSICAO_INICIAL)

    def _esta_sobre_buraco(self, moeda, buracos):
        """Informa se a lupa alcança a abertura de algum buraco."""
        area_moeda = moeda.rect.inflate(*MARGEM_BURACO)
        return any(
            area_moeda.right > buraco.rect.left
            and area_moeda.left < buraco.rect.right
            for buraco in buracos
        )

    def _esta_em_posicao_segura(self, moeda, pedras, buracos):
        perto_de_checkpoint = any(
            moeda.rect.colliderect(area)
            for area in self.areas_livres
        )
        perto_de_pedra = any(
            moeda.rect.inflate(*MARGEM_PEDRA).colliderect(pedra.rect)
            for pedra in pedras
        )
        return (
            not perto_de_checkpoint
            and not perto_de_pedra
            and not self._esta_sobre_buraco(moeda, buracos)
        )

    def _gerar_ate(self, limite_geracao, pedras, buracos):
        """Gera lupas até preencher a margem adiante da câmera."""
        while self.proxima_posicao < limite_geracao:
            moeda = Moeda(self.proxima_posicao, self.y_chao)
            if self._esta_em_posicao_segura(moeda, pedras, buracos):
                self.moedas.append(moeda)
            self.proxima_posicao += random.randint(*ESPACO_ENTRE_LUPAS)

    def _remover_lupas_invalidas(self, buracos):
        # Um buraco novo pode surgir perto da última lupa já gerada.
        self.moedas = [
            moeda
            for moeda in self.moedas
            if not self._esta_sobre_buraco(moeda, buracos)
        ]

    def atualizar(self, camera_x, pedras, buracos=()):
        """Mantém lupas próximas e gera novas peças em locais seguros."""
        self.moedas = manter_objetos_proximos(
            self.moedas,
            camera_x,
            self.largura_tela,
        )
        self._remover_lupas_invalidas(buracos)
        limite_geracao = camera_x + self.largura_tela * TELAS_PARA_GERAR
        self._gerar_ate(limite_geracao, pedras, buracos)

    def coletar(self, personagem):
        """Remove lupas tocadas e retorna quantas foram coletadas."""
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
        """Desenha apenas as lupas próximas à tela."""
        for moeda in self.moedas:
            if esta_visivel(
                moeda.rect,
                camera_x,
                self.largura_tela,
                MARGEM_VISIBILIDADE,
            ):
                moeda.desenhar(tela, camera_x)
