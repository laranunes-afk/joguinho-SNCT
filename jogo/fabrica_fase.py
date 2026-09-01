from cenario import Cenario
from checkpoint import Checkpoint
from configuracoes_tela import RECUO_CAMERA_RETORNO
from inimigos import Inimigos
from moedas import Moedas
from obstaculos import Obstaculos
from personagem import Personagem


def criar_fase(numero_fase, largura, altura):
    """Monta e conecta todas as pecas de uma fase comum."""
    cenario = Cenario(largura, altura, numero_fase)
    personagem = Personagem(30, cenario.y_chao - 80)
    primeiro_checkpoint = largura + 250
    distancia = max(1100, largura)
    checkpoints = [
        Checkpoint(primeiro_checkpoint + indice * distancia, cenario.y_chao)
        for indice in range(2)
    ]
    areas_livres = [checkpoint.area_livre for checkpoint in checkpoints]
    obstaculos = Obstaculos(largura, cenario.y_chao, areas_livres)
    inimigos = Inimigos(largura, cenario.y_chao, areas_livres, numero_fase)
    moedas = Moedas(largura, cenario.y_chao, areas_livres)
    moedas.atualizar(0, obstaculos.pedras, obstaculos.buracos)
    return cenario, personagem, checkpoints, obstaculos, inimigos, moedas


def reposicionar(personagem, cenario, ponto_retorno_x):
    """Restaura a personagem no ultimo ponto seguro."""
    personagem.rect.left = ponto_retorno_x + personagem.margem_hitbox_x
    personagem.rect.bottom = cenario.y_chao
    personagem.velocidade_y = 0
    personagem.no_chao = True
    personagem.caindo_no_buraco = False
    cenario.camera_x = max(
        cenario.inicio_mundo,
        ponto_retorno_x - RECUO_CAMERA_RETORNO,
    )
