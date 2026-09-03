from dataclasses import dataclass, field

import pygame

from avisos import AvisosTemporarios
from configuracoes_tela import RECUO_CAMERA_RETORNO
from fabrica_fase import criar_fase
from perguntas import Perguntas


@dataclass
class EstadoPartida:
    """Agrupa o estado mutável e as transições de uma partida."""

    largura: int
    altura: int
    numero_fase: int = 1
    lupas: int = 0
    tempo_inicio: int | None = None
    mostrar_controles: bool = True
    perguntas: Perguntas = field(default_factory=Perguntas)
    avisos: AvisosTemporarios = field(default_factory=AvisosTemporarios)

    def __post_init__(self):
        self._carregar_fase(self.numero_fase)

    def _carregar_fase(self, numero_fase):
        self.numero_fase = numero_fase
        (
            self.cenario,
            self.personagem,
            self.checkpoints,
            self.obstaculos,
            self.inimigos,
            self.moedas,
        ) = criar_fase(numero_fase, self.largura, self.altura)
        self.ponto_retorno_x = RECUO_CAMERA_RETORNO

    def reiniciar(self, reiniciar_cronometro=True):
        """Volta à fase 1 e limpa os recursos da tentativa anterior."""
        self.perguntas = Perguntas()
        self.avisos = AvisosTemporarios()
        self.lupas = 0
        self._carregar_fase(1)
        if reiniciar_cronometro:
            self.tempo_inicio = None
            self.mostrar_controles = True

    def avancar_fase(self):
        """Monta a próxima fase e leva consigo o aviso de recompensa."""
        self._carregar_fase(self.numero_fase + 1)
        self.avisos.transferir_para(self.personagem)

    def perder_lupas(self, limite):
        quantidade = min(limite, self.lupas)
        self.lupas -= quantidade
        return quantidade

    def houve_movimento(self, x_anterior):
        return self.personagem.rect.x != x_anterior

    def iniciar_cronometro(self):
        if self.tempo_inicio is None:
            self.tempo_inicio = pygame.time.get_ticks()

    @property
    def segundos_decorridos(self):
        if self.tempo_inicio is None:
            return 0
        return (pygame.time.get_ticks() - self.tempo_inicio) // 1000
