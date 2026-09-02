import random

import pygame

from cenario import esta_visivel, manter_objetos_proximos
from recursos import carregar_imagem_recortada


LARGURA_INIMIGO = 46
ALTURA_INIMIGO = 58
ALCANCE_PATRULHA = 110
VELOCIDADE_PATRULHA = 2
MARGEM_BURACO = 8

DISTANCIAS_POR_FASE = {
    1: (450, 600),
    2: (350, 500),
    3: (280, 420),
}
TELAS_PARA_GERAR = 2
MARGEM_ROTA = 10
MARGEM_CHECKPOINT = (260, 0)
MARGEM_PEDRA = (120, 0)
MARGEM_VISIBILIDADE = 100
TOLERANCIA_PISADA = 12
INTENSIDADE_REBOTE = 0.55
ALTURA_IMAGEM_INIMIGO = 78
ARQUIVOS_INIMIGOS = (
    "Homem Vilão6.png",
    "mulher vilão.png",
)


class Inimigo:
    """Inimigo que patrulha uma pequena área do cenário."""

    _imagens = {}

    def __init__(self, x, y_chao, nome_imagem=ARQUIVOS_INIMIGOS[0]):
        """Cria um inimigo e define os limites de sua patrulha."""
        self.rect = pygame.Rect(
            x,
            y_chao - ALTURA_INIMIGO,
            LARGURA_INIMIGO,
            ALTURA_INIMIGO,
        )
        self.limite_esquerdo = x - ALCANCE_PATRULHA
        self.limite_direito = x + ALCANCE_PATRULHA
        self.velocidade = VELOCIDADE_PATRULHA
        self.derrotado = False
        self.imagem = self._obter_imagem(nome_imagem)

    @classmethod
    def _obter_imagem(cls, nome_imagem):
        """Carrega e dimensiona cada arte de inimigo uma única vez."""
        if nome_imagem not in cls._imagens:
            imagem = carregar_imagem_recortada(nome_imagem)
            largura = max(
                1,
                round(
                    imagem.get_width()
                    * ALTURA_IMAGEM_INIMIGO
                    / imagem.get_height()
                ),
            )
            cls._imagens[nome_imagem] = pygame.transform.scale(
                imagem,
                (largura, ALTURA_IMAGEM_INIMIGO),
            )
        return cls._imagens[nome_imagem]

    def _esta_perto_de_buraco(self, buracos):
        return any(
            self.rect.right + MARGEM_BURACO > buraco.rect.left
            and self.rect.left - MARGEM_BURACO < buraco.rect.right
            for buraco in buracos
        )

    def _colidiu_com_bloqueio(self, pedras, areas_livres, outros):
        return (
            any(self.rect.colliderect(pedra.rect) for pedra in pedras)
            or any(self.rect.colliderect(area) for area in areas_livres)
            or any(
                outro is not self
                and not outro.derrotado
                and self.rect.colliderect(outro.rect)
                for outro in outros
            )
        )

    def atualizar(self, pedras=(), buracos=(), areas_livres=(), outros=()):
        """Patrulha a área e muda de direção diante de bloqueios."""
        if self.derrotado:
            return

        x_anterior = self.rect.x
        self.rect.x += self.velocidade
        encontrou_bloqueio = (
            self._esta_perto_de_buraco(buracos)
            or self._colidiu_com_bloqueio(pedras, areas_livres, outros)
        )

        if encontrou_bloqueio:
            self.rect.x = x_anterior
            self.velocidade *= -1
            return

        if self.rect.left <= self.limite_esquerdo:
            self.rect.left = self.limite_esquerdo
            self.velocidade = abs(self.velocidade)
        elif self.rect.left >= self.limite_direito:
            self.rect.left = self.limite_direito
            self.velocidade = -abs(self.velocidade)

    def desenhar(self, tela, camera_x):
        """Desenha o inimigo enquanto ele não tiver sido derrotado."""
        if self.derrotado:
            return

        inimigo_na_tela = self.rect.copy()
        inimigo_na_tela.x -= int(camera_x)

        imagem = self.imagem
        if self.velocidade < 0:
            imagem = pygame.transform.flip(imagem, True, False)
        tela.blit(imagem, imagem.get_rect(midbottom=inimigo_na_tela.midbottom))


class Inimigos:
    """Gera, movimenta e detecta colisões com os inimigos da fase."""

    def __init__(
        self,
        largura_tela,
        y_chao,
        areas_livres=None,
        numero_fase=1,
    ):
        """Prepara a geração e o controle dos inimigos da fase."""
        self.largura_tela = largura_tela
        self.y_chao = y_chao
        self.areas_livres = areas_livres or []
        self.inimigos = []
        self.numero_fase = max(1, min(3, numero_fase))
        self._intervalo_geracao = DISTANCIAS_POR_FASE[self.numero_fase]
        self.proxima_posicao = random.randint(*self._intervalo_geracao)

    @staticmethod
    def _rota_sobre_buraco(inimigo, buracos):
        """Verifica se a área real da patrulha cruza um buraco."""
        largura_rota = (
            inimigo.limite_direito
            - inimigo.limite_esquerdo
            + inimigo.rect.width
        )
        rota = pygame.Rect(
            inimigo.limite_esquerdo,
            inimigo.rect.top,
            largura_rota,
            inimigo.rect.height,
        ).inflate(MARGEM_ROTA * 2, 0)
        return any(
            rota.right > buraco.rect.left
            and rota.left < buraco.rect.right
            for buraco in buracos
        )

    def _esta_em_posicao_segura(self, inimigo, pedras, buracos):
        perto_de_checkpoint = any(
            inimigo.rect.inflate(*MARGEM_CHECKPOINT).colliderect(area)
            for area in self.areas_livres
        )
        perto_de_pedra = any(
            inimigo.rect.inflate(*MARGEM_PEDRA).colliderect(pedra.rect)
            for pedra in pedras
        )
        return (
            not perto_de_checkpoint
            and not perto_de_pedra
            and not self._rota_sobre_buraco(inimigo, buracos)
        )

    def _gerar_ate(self, limite_geracao, pedras, buracos):
        """Gera inimigos em posições seguras até o limite indicado."""
        while self.proxima_posicao < limite_geracao:
            nome_imagem = ARQUIVOS_INIMIGOS[
                len(self.inimigos) % len(ARQUIVOS_INIMIGOS)
            ]
            inimigo = Inimigo(
                self.proxima_posicao,
                self.y_chao,
                nome_imagem,
            )
            if self._esta_em_posicao_segura(inimigo, pedras, buracos):
                self.inimigos.append(inimigo)
            self.proxima_posicao += random.randint(*self._intervalo_geracao)

    def _descartar_distantes_e_derrotados(self, camera_x):
        proximos = manter_objetos_proximos(
            self.inimigos,
            camera_x,
            self.largura_tela,
        )
        self.inimigos = [
            inimigo for inimigo in proximos if not inimigo.derrotado
        ]

    def _atualizar_patrulhas(self, pedras, buracos):
        """Atualiza usando apenas vizinhos laterais, evitando busca O(n²)."""
        ordenados = sorted(self.inimigos, key=lambda inimigo: inimigo.rect.left)
        for indice, inimigo in enumerate(ordenados):
            vizinhos = (
                ordenados[max(0, indice - 1):indice]
                + ordenados[indice + 1:indice + 2]
            )
            inimigo.atualizar(
                pedras,
                buracos,
                self.areas_livres,
                vizinhos,
            )

    def atualizar(self, camera_x, pedras=(), buracos=()):
        """Gera inimigos seguros e atualiza somente os ainda relevantes."""
        self._descartar_distantes_e_derrotados(camera_x)
        limite_geracao = camera_x + self.largura_tela * TELAS_PARA_GERAR
        self._gerar_ate(limite_geracao, pedras, buracos)
        self._atualizar_patrulhas(pedras, buracos)

    def verificar_colisao(self, personagem, rect_anterior):
        """Retorna 'derrotou', 'atingido' ou None conforme o contato."""
        for inimigo in self.inimigos:
            if inimigo.derrotado or not personagem.rect.colliderect(inimigo.rect):
                continue

            pulou_na_cabeca = (
                personagem.velocidade_y > 0
                and rect_anterior.bottom <= inimigo.rect.top + TOLERANCIA_PISADA
                and personagem.rect.bottom >= inimigo.rect.top
            )

            if pulou_na_cabeca:
                inimigo.derrotado = True
                personagem.rect.bottom = inimigo.rect.top
                personagem.rebater(INTENSIDADE_REBOTE)
                return "derrotou"

            return "atingido"

        return None

    def desenhar(self, tela, camera_x):
        """Desenha somente os inimigos próximos à tela."""
        for inimigo in self.inimigos:
            if esta_visivel(
                inimigo.rect,
                camera_x,
                self.largura_tela,
                MARGEM_VISIBILIDADE,
            ):
                inimigo.desenhar(tela, camera_x)
