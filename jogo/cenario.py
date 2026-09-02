from recursos import carregar_imagem, carregar_imagem_recortada


PROPORCAO_ALTURA_CHAO = 0.35
QUANTIDADE_TRECHOS_DESENHADOS = 3
TELAS_PRESERVADAS_ATRAS = 3
DISTANCIA_MINIMA_PRESERVADA = 1600

ARQUIVOS_DE_FUNDO = {
    1: "pixilart-drawing (1).png",
    2: "cenário-2.png",
    3: "cenário-3.png",
}


def esta_visivel(rect, camera_x, largura_tela, margem=0):
    """Informa se um retângulo alcança a região visível da câmera."""
    limite_esquerdo = camera_x - margem
    limite_direito = camera_x + largura_tela + margem
    return rect.right > limite_esquerdo and rect.left < limite_direito


def manter_objetos_proximos(
    objetos,
    camera_x,
    largura_tela,
    telas_atras=TELAS_PRESERVADAS_ATRAS,
):
    """Descarta objetos muito antigos sem impedir um retorno curto na fase."""
    distancia_preservada = max(
        largura_tela * telas_atras,
        DISTANCIA_MINIMA_PRESERVADA,
    )
    limite_descarte = camera_x - distancia_preservada
    return [objeto for objeto in objetos if objeto.rect.right >= limite_descarte]


class Cenario:
    """Cenário infinito com aparência própria para cada fase."""

    def __init__(self, largura, altura, fase=1):
        """Prepara as superfícies e medidas do cenário da fase."""
        self.largura = largura
        self.altura = altura
        self.fase = fase
        self.inicio_mundo = 0
        self.camera_x = 0
        self.altura_chao = int(altura * PROPORCAO_ALTURA_CHAO)
        self.y_chao = altura - self.altura_chao

        # Mantém o comportamento anterior: fases desconhecidas usam o fundo 3.
        arquivo_fundo = ARQUIVOS_DE_FUNDO.get(fase, ARQUIVOS_DE_FUNDO[3])
        self.fundo = carregar_imagem(
            arquivo_fundo,
            (self.largura, self.altura),
        )
        self.chao = carregar_imagem_recortada(
            "Chão.png",
            (self.largura, self.altura_chao),
        )

    def _desenhar_repetido(self, tela, superficie, y):
        """Repete uma camada para preencher a tela durante o movimento."""
        primeiro_trecho = int(self.camera_x // self.largura)
        for indice in range(
            primeiro_trecho,
            primeiro_trecho + QUANTIDADE_TRECHOS_DESENHADOS,
        ):
            x = indice * self.largura - self.camera_x
            tela.blit(superficie, (x, y))

    def desenhar_fundo(self, tela):
        """Repete o fundo para cobrir a região visível da câmera."""
        self._desenhar_repetido(tela, self.fundo, 0)

    def desenhar_chao(self, tela):
        """Repete a superfície do chão ao longo do cenário."""
        self._desenhar_repetido(tela, self.chao, self.y_chao)

    def desenhar(self, tela):
        """Desenha o fundo e o chão da fase."""
        self.desenhar_fundo(tela)
        self.desenhar_chao(tela)
