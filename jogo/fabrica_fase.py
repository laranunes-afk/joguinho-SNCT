from cenario import Cenario
from checkpoint import Checkpoint
from configuracoes_tela import RECUO_CAMERA_RETORNO
from inimigos import Inimigos
from moedas import Moedas
from obstaculos import Obstaculos
from personagem import Personagem


X_INICIAL_PERSONAGEM = 30
ALTURA_PERSONAGEM = 80
QUANTIDADE_CHECKPOINTS = 2
DISTANCIA_MINIMA_CHECKPOINTS = 1100
RECUO_PRIMEIRO_CHECKPOINT = 250


def _criar_checkpoints(largura, y_chao):
    """Cria os pontos que delimitam o progresso da fase."""
    primeiro_x = largura + RECUO_PRIMEIRO_CHECKPOINT
    distancia = max(DISTANCIA_MINIMA_CHECKPOINTS, largura)
    return [
        Checkpoint(primeiro_x + indice * distancia, y_chao)
        for indice in range(QUANTIDADE_CHECKPOINTS)
    ]


def _criar_elementos_da_fase(largura, y_chao, areas_protegidas, numero_fase):
    """Conecta geradores que compartilham chão e zonas protegidas."""
    obstaculos = Obstaculos(largura, y_chao, areas_protegidas)
    inimigos = Inimigos(
        largura,
        y_chao,
        areas_protegidas,
        numero_fase,
    )
    moedas = Moedas(largura, y_chao, areas_protegidas)
    moedas.atualizar(0, obstaculos.pedras, obstaculos.buracos)
    return obstaculos, inimigos, moedas


def criar_fase(numero_fase, largura, altura):
    """Monta e conecta as seis peças públicas de uma fase comum."""
    cenario = Cenario(largura, altura, numero_fase)
    personagem = Personagem(
        X_INICIAL_PERSONAGEM,
        cenario.y_chao - ALTURA_PERSONAGEM,
    )
    checkpoints = _criar_checkpoints(largura, cenario.y_chao)
    areas_protegidas = [
        checkpoint.area_livre
        for checkpoint in checkpoints
    ]
    obstaculos, inimigos, moedas = _criar_elementos_da_fase(
        largura,
        cenario.y_chao,
        areas_protegidas,
        numero_fase,
    )

    # A ordem é parte do contrato usado pelo laço principal.
    return cenario, personagem, checkpoints, obstaculos, inimigos, moedas


def reposicionar(personagem, cenario, ponto_retorno_x):
    """Restaura a personagem e a câmera no último ponto seguro."""
    personagem.posicionar_no_chao(ponto_retorno_x, cenario.y_chao)
    cenario.camera_x = max(
        cenario.inicio_mundo,
        ponto_retorno_x - RECUO_CAMERA_RETORNO,
    )
