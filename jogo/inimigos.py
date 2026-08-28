import random

import pygame


class Inimigo:
    """Inimigo que patrulha uma pequena área do cenário."""

    def __init__(self, x, y_chao):
        """Cria um inimigo e define os limites de sua patrulha."""
        self.rect = pygame.Rect(x, y_chao - 58, 46, 58)
        self.limite_esquerdo = x - 110
        self.limite_direito = x + 110
        self.velocidade = 2
        self.derrotado = False

    def atualizar(self, pedras=(), buracos=(), areas_livres=(), outros=()):
        """Patrulha a área e muda de direção diante de bloqueios."""
        if self.derrotado:
            return

        x_anterior = self.rect.x
        self.rect.x += self.velocidade

        perto_de_buraco = any(
            self.rect.right + 8 > buraco.rect.left
            and self.rect.left - 8 < buraco.rect.right
            for buraco in buracos
        )
        colidiu_com_objeto = (
            any(self.rect.colliderect(pedra.rect) for pedra in pedras)
            or any(self.rect.colliderect(area) for area in areas_livres)
            or perto_de_buraco
            or any(
                outro is not self
                and not outro.derrotado
                and self.rect.colliderect(outro.rect)
                for outro in outros
            )
        )

        if colidiu_com_objeto:
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

        # O inimigo ainda não possui imagem própria.
        pygame.draw.rect(
            tela,
            (120, 55, 135),
            (inimigo_na_tela.left + 5, inimigo_na_tela.top + 22, 36, 31),
            border_radius=8
        )
        pygame.draw.circle(
            tela,
            (170, 90, 180),
            (inimigo_na_tela.centerx, inimigo_na_tela.top + 16),
            17
        )
        pygame.draw.circle(
            tela,
            (255, 255, 255),
            (inimigo_na_tela.centerx - 6, inimigo_na_tela.top + 14),
            4
        )
        pygame.draw.circle(
            tela,
            (255, 255, 255),
            (inimigo_na_tela.centerx + 6, inimigo_na_tela.top + 14),
            4
        )
        pygame.draw.circle(
            tela,
            (35, 25, 45),
            (inimigo_na_tela.centerx - 6, inimigo_na_tela.top + 15),
            2
        )
        pygame.draw.circle(
            tela,
            (35, 25, 45),
            (inimigo_na_tela.centerx + 6, inimigo_na_tela.top + 15),
            2
        )
        pygame.draw.line(
            tela,
            (55, 35, 70),
            (inimigo_na_tela.left + 9, inimigo_na_tela.bottom),
            (inimigo_na_tela.left + 16, inimigo_na_tela.bottom - 8),
            4
        )
        pygame.draw.line(
            tela,
            (55, 35, 70),
            (inimigo_na_tela.right - 9, inimigo_na_tela.bottom),
            (inimigo_na_tela.right - 16, inimigo_na_tela.bottom - 8),
            4
        )


class Inimigos:
    """Gera, movimenta e detecta colisões com os inimigos da fase."""

    def __init__(
        self,
        largura_tela,
        y_chao,
        areas_livres=None,
        numero_fase=1
    ):
        """Prepara a geração e o controle dos inimigos da fase."""
        self.largura_tela = largura_tela
        self.y_chao = y_chao
        self.areas_livres = areas_livres or []
        self.inimigos = []
        self.numero_fase = max(1, min(3, numero_fase))
        self.distancias_por_fase = {
            1: (450, 600),
            2: (350, 500),
            3: (280, 420),
        }
        distancia_minima, distancia_maxima = self.distancias_por_fase[
            self.numero_fase
        ]
        self.proxima_posicao = random.randint(
            distancia_minima,
            distancia_maxima
        )

    @staticmethod
    def _rota_sobre_buraco(inimigo, buracos):
        """Verifica se a área de patrulha planejada cruza um buraco."""
        rota = inimigo.rect.inflate(240, 0)
        return any(
            rota.right > buraco.rect.left
            and rota.left < buraco.rect.right
            for buraco in buracos
        )

    def atualizar(self, camera_x, pedras=(), buracos=()):
        """Gera inimigos em posições seguras e atualiza suas patrulhas."""
        limite_geracao = camera_x + self.largura_tela * 2

        while self.proxima_posicao < limite_geracao:
            inimigo = Inimigo(self.proxima_posicao, self.y_chao)
            perto_de_checkpoint = any(
                inimigo.rect.inflate(260, 0).colliderect(area)
                for area in self.areas_livres
            )
            perto_de_pedra = any(
                inimigo.rect.inflate(120, 0).colliderect(pedra.rect)
                for pedra in pedras
            )

            if (
                not perto_de_checkpoint
                and not perto_de_pedra
                and not self._rota_sobre_buraco(inimigo, buracos)
            ):
                self.inimigos.append(inimigo)

            distancia_minima, distancia_maxima = self.distancias_por_fase[
                self.numero_fase
            ]
            self.proxima_posicao += random.randint(
                distancia_minima,
                distancia_maxima
            )

        for inimigo in self.inimigos:
            inimigo.atualizar(
                pedras,
                buracos,
                self.areas_livres,
                self.inimigos
            )

    def verificar_colisao(self, personagem, rect_anterior):
        """Retorna 'derrotou', 'atingido' ou None conforme o contato."""
        for inimigo in self.inimigos:
            if inimigo.derrotado or not personagem.rect.colliderect(inimigo.rect):
                continue

            pulou_na_cabeca = (
                personagem.velocidade_y > 0
                and rect_anterior.bottom <= inimigo.rect.top + 12
                and personagem.rect.bottom >= inimigo.rect.top
            )

            if pulou_na_cabeca:
                inimigo.derrotado = True
                personagem.rect.bottom = inimigo.rect.top
                personagem.velocidade_y = personagem.forca_pulo * 0.55
                personagem.no_chao = False
                return "derrotou"

            return "atingido"

        return None

    def desenhar(self, tela, camera_x):
        """Desenha somente os inimigos próximos à tela."""
        limite_esquerdo = camera_x - 100
        limite_direito = camera_x + self.largura_tela + 100

        for inimigo in self.inimigos:
            if (
                inimigo.rect.right > limite_esquerdo
                and inimigo.rect.left < limite_direito
            ):
                inimigo.desenhar(tela, camera_x)
