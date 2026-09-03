import random

import pygame

from cenario import esta_visivel, manter_objetos_proximos
from recursos import carregar_imagem_recortada


LARGURA_PEDRA = (60, 80)
ALTURA_PEDRA = (45, 60)
LARGURA_BURACO = (110, 150)
ALTURA_AREA_BURACO = 2000
ALTURA_IMAGEM_BURACO = 42
POSICAO_INICIAL = (450, 700)
ESPACO_ENTRE_OBSTACULOS = (350, 700)
CHANCE_DE_BURACO = 0.35
TELAS_PARA_GERAR = 2
MARGEM_VISIBILIDADE = 100


class Pedra:
    """Pedra posicionada no chão do cenário."""

    _imagens = {}

    def __init__(self, x, y_chao):
        """Cria uma pedra de tamanho aleatório apoiada no chão."""
        tamanho = (
            random.randint(*LARGURA_PEDRA),
            random.randint(*ALTURA_PEDRA),
        )
        largura, altura = tamanho
        self.rect = pygame.Rect(x, y_chao - altura, largura, altura)
        self.imagem = self._obter_imagem(tamanho)

    def _obter_imagem(self, tamanho):
        """Reaproveita pedras que tenham exatamente o mesmo tamanho."""
        if tamanho not in self._imagens:
            self._imagens[tamanho] = carregar_imagem_recortada(
                "Pedra-melhorada.png",
                tamanho,
            )
        return self._imagens[tamanho]

    def desenhar(self, tela, camera_x):
        """Desenha a pedra considerando o deslocamento da câmera."""
        pedra_na_tela = self.rect.copy()
        pedra_na_tela.x -= int(camera_x)
        tela.blit(self.imagem, pedra_na_tela)


class Buraco:
    """Abertura no chão que faz o personagem cair."""

    _imagens = {}

    def __init__(self, x, y_chao):
        """Cria um buraco com largura aleatória a partir do nível do chão."""
        largura = random.randint(*LARGURA_BURACO)
        self.rect = pygame.Rect(x, y_chao, largura, ALTURA_AREA_BURACO)
        self.imagem = self._obter_imagem(largura)

    def _obter_imagem(self, largura):
        """Reaproveita a arte de buracos com a mesma largura."""
        if largura not in self._imagens:
            self._imagens[largura] = carregar_imagem_recortada(
                "Buraco.png",
                (largura, ALTURA_IMAGEM_BURACO),
            )
        return self._imagens[largura]

    def desenhar(self, tela, camera_x):
        """Desenha a abertura do buraco na posição visível."""
        rect_imagem = self.imagem.get_rect(
            midtop=(
                self.rect.centerx - int(camera_x),
                self.rect.y,
            )
        )
        tela.blit(self.imagem, rect_imagem)


class Obstaculos:
    """Cria e controla pedras e buracos espalhados pelo cenário."""

    def __init__(self, largura_tela, y_chao, areas_livres=None):
        """Prepara um primeiro buraco e os demais obstáculos aleatórios."""
        self.largura_tela = largura_tela
        self.y_chao = y_chao
        self.pedras = []
        self.buracos = []
        self.areas_livres = areas_livres or []
        self.proximo_eh_buraco = True

        # Mantém a região inicial livre para a personagem.
        self.proxima_posicao = random.randint(*POSICAO_INICIAL)
        self.atualizar(0)

    def _criar_proximo(self):
        """Cria a próxima peça sem decidir ainda se ela será adicionada."""
        criar_buraco = (
            self.proximo_eh_buraco
            or random.random() < CHANCE_DE_BURACO
        )
        self.proximo_eh_buraco = False
        classe_obstaculo = Buraco if criar_buraco else Pedra
        return classe_obstaculo(self.proxima_posicao, self.y_chao)

    def _area_ocupada(self, obstaculo):
        """Representa no chão a área usada para proteger checkpoints."""
        if not isinstance(obstaculo, Buraco):
            return obstaculo.rect

        # A hitbox do buraco começa abaixo do chão, por isso uma faixa
        # vertical separada é usada somente durante a geração.
        return pygame.Rect(
            obstaculo.rect.x,
            0,
            obstaculo.rect.width,
            self.y_chao,
        )

    def _esta_em_area_protegida(self, obstaculo):
        area_ocupada = self._area_ocupada(obstaculo)
        return any(
            area_ocupada.colliderect(area)
            for area in self.areas_livres
        )

    def _adicionar(self, obstaculo):
        colecao = self.buracos if isinstance(obstaculo, Buraco) else self.pedras
        colecao.append(obstaculo)

    def _gerar_ate(self, limite_geracao):
        """Gera peças até preencher a margem adiante da câmera."""
        while self.proxima_posicao < limite_geracao:
            obstaculo = self._criar_proximo()
            if not self._esta_em_area_protegida(obstaculo):
                self._adicionar(obstaculo)
            self.proxima_posicao += random.randint(*ESPACO_ENTRE_OBSTACULOS)

    def _descartar_distantes(self, camera_x):
        self.pedras = manter_objetos_proximos(
            self.pedras,
            camera_x,
            self.largura_tela,
        )
        self.buracos = manter_objetos_proximos(
            self.buracos,
            camera_x,
            self.largura_tela,
        )

    def atualizar(self, camera_x):
        """Mantém obstáculos próximos e gera novas peças à frente."""
        self._descartar_distantes(camera_x)
        limite_geracao = camera_x + self.largura_tela * TELAS_PARA_GERAR
        self._gerar_ate(limite_geracao)

    def colidiu_com(self, personagem):
        """Informa se a personagem tocou alguma pedra."""
        return any(
            personagem.rect.colliderect(pedra.rect)
            for pedra in self.pedras
        )

    def personagem_esta_sobre_buraco(self, personagem):
        """Verifica se o centro dos pés está dentro de algum buraco."""
        # O centro evita perder o pulo apenas por encostar numa borda.
        centro_dos_pes = personagem.rect.centerx
        return any(
            buraco.rect.left < centro_dos_pes < buraco.rect.right
            for buraco in self.buracos
        )

    def desenhar(self, tela, camera_x):
        """Desenha somente os obstáculos próximos à área visível."""
        for obstaculo in (*self.pedras, *self.buracos):
            if esta_visivel(
                obstaculo.rect,
                camera_x,
                self.largura_tela,
                MARGEM_VISIBILIDADE,
            ):
                obstaculo.desenhar(tela, camera_x)
