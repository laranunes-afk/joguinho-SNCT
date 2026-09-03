import pygame

from recursos import carregar_imagem_recortada


ALTURA_IMAGEM_PADRAO = 90
TAMANHO_MODELO_PADRAO = (100, 160)
RAIO_INDICADOR = 25


class PessoaFinal:
    """Apresentador que bloqueia o caminho até sua pergunta ser respondida."""

    ALTURA_IMAGEM = ALTURA_IMAGEM_PADRAO

    def __init__(
        self,
        x,
        y_chao,
        cor,
        pergunta,
        nome_imagem=None,
        altura_imagem=None,
    ):
        self.cor = cor
        self.pergunta = pergunta
        self.respondida = False
        self.altura_imagem = altura_imagem or self.ALTURA_IMAGEM
        self.imagem = self._carregar_imagem(nome_imagem)
        tamanho = self.imagem.get_size() if self.imagem else TAMANHO_MODELO_PADRAO
        self.rect = pygame.Rect(x, 0, *tamanho)
        self.rect.bottom = y_chao
        self.indicador = self._criar_indicador()

    def _carregar_imagem(self, nome_imagem):
        """Recorta margens transparentes e preserva a proporção da arte."""
        if nome_imagem is None:
            return None

        recortada = carregar_imagem_recortada(nome_imagem)
        largura = max(
            1,
            round(
                recortada.get_width()
                * self.altura_imagem
                / recortada.get_height()
            ),
        )
        return pygame.transform.smoothscale(
            recortada,
            (largura, self.altura_imagem),
        )

    def _criar_indicador(self):
        tamanho = RAIO_INDICADOR * 2
        indicador = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
        centro = (RAIO_INDICADOR, RAIO_INDICADOR)
        pygame.draw.circle(indicador, (255, 255, 255), centro, RAIO_INDICADOR)
        fonte = pygame.font.Font(None, 42)
        texto = fonte.render("?", True, (30, 38, 58))
        indicador.blit(
            texto,
            texto.get_rect(center=(centro[0], centro[1] + 2)),
        )
        return indicador

    def bloquear_passagem(self, personagem, rect_anterior):
        """Cria uma barreira vertical até a resposta ser concluída."""
        if self.respondida:
            return

        x_barreira = self.rect.centerx
        atravessou_pela_esquerda = (
            rect_anterior.right <= x_barreira < personagem.rect.right
        )
        atravessou_pela_direita = (
            rect_anterior.left >= x_barreira > personagem.rect.left
        )
        if atravessou_pela_esquerda:
            personagem.rect.right = x_barreira
        elif atravessou_pela_direita:
            personagem.rect.left = x_barreira

    def desenhar(self, tela, camera_x):
        x_na_tela = self.rect.x - int(camera_x)
        centro_x = int(self.rect.centerx - camera_x)
        y = self.rect.top

        if self.imagem:
            tela.blit(self.imagem, (x_na_tela, y))
        else:
            self._desenhar_modelo(tela, centro_x, y)

        if not self.respondida:
            rect_indicador = self.indicador.get_rect(
                center=(centro_x, y - RAIO_INDICADOR),
            )
            tela.blit(self.indicador, rect_indicador)

    def _desenhar_modelo(self, tela, x, y):
        """Mantém um apresentador provisório quando nenhuma arte é fornecida."""
        pygame.draw.circle(tela, (235, 190, 150), (x, y + 34), 32)
        pygame.draw.rect(
            tela,
            self.cor,
            (x - 38, y + 68, 76, 72),
            border_radius=14,
        )
        pygame.draw.line(
            tela,
            (30, 38, 58),
            (x - 22, y + 140),
            (x - 28, y + 160),
            10,
        )
        pygame.draw.line(
            tela,
            (30, 38, 58),
            (x + 22, y + 140),
            (x + 28, y + 160),
            10,
        )
