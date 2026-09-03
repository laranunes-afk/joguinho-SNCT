import pygame

from configuracoes_tela import FPS
from dados_perguntas import (
    APRESENTADORES,
    DESAFIOS_FINAIS,
    PERGUNTAS_FINAIS,
)
from interface_fase_final import InterfaceFaseFinal
from pergunta_final import PerguntaFinal
from personagem import Personagem
from pessoa_final import PessoaFinal
from tesouro_final import TesouroFinal


PROPORCAO_CHAO = 0.35
X_INICIAL_PERSONAGEM = 40
INICIO_MINIMO_APRESENTADORES = 620
DISTANCIA_MINIMA_APRESENTADORES = 620
MARGEM_CAMERA = 0.42
RECOMPENSA_POR_RESPOSTA = 10
RECUO_APOS_RESPOSTA = 20

# Estes dois nomes continuam importáveis por compatibilidade. A fase usa a
# estrutura unificada DESAFIOS_FINAIS para não depender de listas paralelas.
__all__ = ["APRESENTADORES", "FaseFinal", "PERGUNTAS_FINAIS"]


class FaseFinal:
    """Coordena movimento, apresentadores, perguntas e tesouro final."""

    def __init__(self, largura, altura):
        self.largura = largura
        self.y_chao = altura - int(altura * PROPORCAO_CHAO)
        self.camera_x = 0
        self.personagem = Personagem(X_INICIAL_PERSONAGEM, 0)
        self.personagem.posicionar_no_chao(X_INICIAL_PERSONAGEM, self.y_chao)
        self.inicio_bonus_checkpoint = pygame.time.get_ticks()
        self.interface = InterfaceFaseFinal(largura, altura, self.y_chao)
        self.tesouro = TesouroFinal()
        self.pessoas = self._criar_pessoas()
        self.pergunta = PerguntaFinal(largura, altura, len(self.pessoas))
        self.fim_mundo = self.pessoas[-1].rect.right + largura // 2

    def _criar_pessoas(self):
        if not DESAFIOS_FINAIS:
            raise ValueError("A fase final precisa ter ao menos um desafio")

        inicio = max(INICIO_MINIMO_APRESENTADORES, int(self.largura * 0.65))
        distancia = max(
            DISTANCIA_MINIMA_APRESENTADORES,
            int(self.largura * 0.6),
        )
        return [
            PessoaFinal(
                inicio + indice * distancia,
                self.y_chao,
                desafio.cor,
                desafio.pergunta,
                desafio.imagem,
                desafio.altura_imagem,
            )
            for indice, desafio in enumerate(DESAFIOS_FINAIS)
        ]

    def _processar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "sair"
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return "sair"
                if evento.key == pygame.K_TAB:
                    return "reiniciar_total"
        return None

    def _atualizar_personagem(self, lupas):
        """Atualiza o controle normal ou a caminhada secreta do tesouro."""
        agora = pygame.time.get_ticks()
        if self.tesouro.em_andamento():
            recompensa = self.tesouro.atualizar(
                self.personagem,
                self.y_chao,
                agora,
            )
            return lupas + recompensa

        self.personagem.atualizar(self.y_chao)
        self.tesouro.tentar_iniciar(self.personagem, agora)
        self.tesouro.limitar_saida_usada(self.personagem)
        return lupas

    def _verificar_perguntas(self, tela, lupas):
        """Processa somente o primeiro apresentador encontrado no quadro."""
        for numero, pessoa in enumerate(self.pessoas, start=1):
            encontrou = self.personagem.rect.colliderect(pessoa.rect)
            if pessoa.respondida or not encontrou:
                continue

            resposta = self.pergunta.fazer(tela, pessoa.pergunta, numero)
            if resposta is None:
                return "sair", lupas
            if resposta == "reiniciar":
                return "reiniciar_total", lupas
            if not resposta:
                return "reiniciar", lupas

            pessoa.respondida = True
            self.personagem.rect.left = pessoa.rect.right + RECUO_APOS_RESPOSTA
            return None, lupas + RECOMPENSA_POR_RESPOSTA

        return None, lupas

    def _bloquear_apresentadores(self, rect_anterior):
        for pessoa in self.pessoas:
            pessoa.bloquear_passagem(self.personagem, rect_anterior)

    def _todas_perguntas_respondidas(self):
        return all(pessoa.respondida for pessoa in self.pessoas)

    def _atualizar_camera(self):
        margem = self.largura * MARGEM_CAMERA
        alvo = self.personagem.rect.centerx - margem
        limite = max(0, self.fim_mundo - self.largura)
        self.camera_x = max(0, min(alvo, limite))

    def _desenhar(self, tela, lupas, tempo_inicio):
        self.interface.desenhar_cenario(tela, self.camera_x)
        for pessoa in self.pessoas:
            pessoa.desenhar(tela, self.camera_x)
        self.personagem.desenhar(tela, self.camera_x)
        self.interface.desenhar_bonus_checkpoint(
            tela,
            self.personagem,
            self.camera_x,
            self.inicio_bonus_checkpoint,
        )
        self.interface.desenhar_hud(
            tela,
            lupas,
            tempo_inicio,
            len(self.pessoas),
            sum(pessoa.respondida for pessoa in self.pessoas),
        )
        self.tesouro.desenhar_aviso(tela, self.largura)

    def jogar(self, tela, lupas_iniciais=0, tempo_inicio=None):
        """Executa a fase e preserva os resultados esperados por ``main.py``."""
        clock = pygame.time.Clock()
        lupas = lupas_iniciais

        while True:
            resultado_evento = self._processar_eventos()
            if resultado_evento is not None:
                return resultado_evento, lupas

            rect_anterior = self.personagem.rect.copy()
            lupas = self._atualizar_personagem(lupas)
            self.personagem.rect.right = min(
                self.fim_mundo,
                self.personagem.rect.right,
            )

            if not self.tesouro.em_andamento():
                self._bloquear_apresentadores(rect_anterior)
                resultado, lupas = self._verificar_perguntas(tela, lupas)
                if resultado is not None:
                    return resultado, lupas

            if self._todas_perguntas_respondidas():
                return "venceu", lupas

            self._atualizar_camera()
            self._desenhar(tela, lupas, tempo_inicio)
            pygame.display.flip()
            clock.tick(FPS)
