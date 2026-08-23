import pygame


class Checkpoint:
    """Marca um novo ponto de retorno para o personagem."""

    def __init__(self, x, y_chao):
        self.x = x
        self.y_chao = y_chao
        self.ativado = False

        # A área alta garante a ativação mesmo se o jogador estiver pulando.
        self.rect = pygame.Rect(
            x,
            0,
            50,
            y_chao
        )

        self.area_livre = pygame.Rect(
            x - 150,
            0,
            350,
            y_chao
        )

        self.posicao_retorno = x + 80

    def foi_alcancado(self, personagem):
        return (
            not self.ativado
            and self.rect.colliderect(personagem.rect)
        )

    def ativar(self):
        self.ativado = True

    def desenhar(self, tela, camera_x, largura_tela):
        x_na_tela = int(self.x - camera_x)

        if x_na_tela < -80 or x_na_tela > largura_tela + 80:
            return

        topo_mastro = self.y_chao - 150

        pygame.draw.rect(
            tela,
            (210, 210, 215),
            (x_na_tela, topo_mastro, 8, 150)
        )

        cor_bandeira = (
            (50, 200, 90)
            if self.ativado
            else (245, 190, 45)
        )

        pygame.draw.polygon(
            tela,
            cor_bandeira,
            [
                (x_na_tela + 8, topo_mastro),
                (x_na_tela + 70, topo_mastro + 25),
                (x_na_tela + 8, topo_mastro + 50),
            ]
        )

        pygame.draw.ellipse(
            tela,
            (80, 80, 85),
            (x_na_tela - 12, self.y_chao - 12, 32, 12)
        )
