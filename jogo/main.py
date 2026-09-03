import pygame

from configuracoes_musica import iniciar_musica, parar_musica
from configuracoes_tela import (
    FPS,
    TOTAL_FASES,
    atualizar_camera_personagem,
    criar_tela,
    limitar_personagem_na_tela,
)
from estado_partida import EstadoPartida
from fabrica_fase import reposicionar
from fase_final import FaseFinal
from hud import desenhar_hud
from menu import desenhar_lista_controles, tela_inicial
from tela_final import TelaFinal


COR_RECOMPENSA = (255, 205, 45)
COR_PERDA = (245, 65, 65)
RECOMPENSA_CHECKPOINT = 5
RECOMPENSA_INIMIGO = 5


class AcaoQuadro:
    """Decisões que fazem o laço principal mudar de caminho."""

    CONTINUAR = object()
    MUDOU_FASE = object()
    REINICIAR = object()
    SAIR = object()
    FINALIZAR = object()


class Jogo:
    """Coordena as peças da partida sem implementar cada uma delas."""

    def __init__(self, tela, clock=None):
        self.tela = tela
        self.largura, self.altura = tela.get_size()
        self.clock = clock or pygame.time.Clock()
        self.estado = EstadoPartida(self.largura, self.altura)
        self.jogar_novamente = False

        self.fonte_cronometro = pygame.font.Font(None, 48)
        self.fonte_fase = pygame.font.Font(None, 42)
        self.fonte_lupas = pygame.font.Font(None, 36)

    def _ler_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return AcaoQuadro.SAIR
            if evento.type != pygame.KEYDOWN:
                continue
            if evento.key == pygame.K_ESCAPE:
                return AcaoQuadro.SAIR
            if evento.key == pygame.K_TAB:
                return AcaoQuadro.REINICIAR
        return AcaoQuadro.CONTINUAR

    def _atualizar_entidades(self):
        estado = self.estado
        fase = estado.cenario
        personagem = estado.personagem

        x_anterior = personagem.rect.x
        rect_anterior = personagem.rect.copy()
        personagem.atualizar(
            fase.y_chao,
            estado.obstaculos.personagem_esta_sobre_buraco,
        )
        if estado.houve_movimento(x_anterior):
            estado.mostrar_controles = False

        limitar_personagem_na_tela(personagem, fase.camera_x, self.largura)
        estado.obstaculos.atualizar(fase.camera_x)
        estado.inimigos.atualizar(
            fase.camera_x,
            estado.obstaculos.pedras,
            estado.obstaculos.buracos,
        )
        estado.moedas.atualizar(
            fase.camera_x,
            estado.obstaculos.pedras,
            estado.obstaculos.buracos,
        )

        self._coletar_lupas()
        return x_anterior, rect_anterior

    def _coletar_lupas(self):
        quantidade = self.estado.moedas.coletar(self.estado.personagem)
        self.estado.lupas += quantidade
        for _ in range(quantidade):
            self.estado.avisos.adicionar(
                self.estado.personagem,
                "+1 LUPA",
                COR_RECOMPENSA,
            )

    def _processar_checkpoint(self):
        estado = self.estado
        for checkpoint in estado.checkpoints:
            if not checkpoint.foi_alcancado(estado.personagem):
                continue

            resposta = estado.perguntas.fazer(self.tela, estado.numero_fase)
            if resposta == "reiniciar":
                return AcaoQuadro.REINICIAR, False, 0
            if resposta is None:
                return AcaoQuadro.SAIR, False, 0
            if not resposta:
                return AcaoQuadro.CONTINUAR, True, estado.perder_lupas(4)

            checkpoint.ativar()
            estado.ponto_retorno_x = checkpoint.posicao_retorno
            estado.lupas += RECOMPENSA_CHECKPOINT
            estado.avisos.adicionar(
                estado.personagem,
                f"+{RECOMPENSA_CHECKPOINT} LUPAS",
                COR_RECOMPENSA,
                duracao=2400,
            )

            if not all(item.ativado for item in estado.checkpoints):
                return AcaoQuadro.CONTINUAR, False, 0
            if estado.numero_fase < TOTAL_FASES:
                estado.avancar_fase()
                return AcaoQuadro.MUDOU_FASE, False, 0
            return self._executar_fase_final(), False, 0

        return AcaoQuadro.CONTINUAR, False, 0

    def _executar_fase_final(self):
        estado = self.estado
        resultado, estado.lupas = FaseFinal(
            self.largura,
            self.altura,
        ).jogar(self.tela, estado.lupas, estado.tempo_inicio)

        if resultado == "venceu":
            self.jogar_novamente = TelaFinal().mostrar(
                self.tela,
                estado.segundos_decorridos(),
                estado.lupas,
            )
            return AcaoQuadro.FINALIZAR
        if resultado == "sair":
            return AcaoQuadro.SAIR
        if resultado in {"reiniciar", "reiniciar_total"}:
            estado.reiniciar(
                reiniciar_cronometro=resultado == "reiniciar_total"
            )
            return AcaoQuadro.MUDOU_FASE

        raise ValueError(f"Resultado desconhecido da fase final: {resultado!r}")

    def _processar_perigos(self, rect_anterior, deve_retornar, lupas_perdidas):
        estado = self.estado
        personagem = estado.personagem

        caiu = personagem.rect.top >= self.altura
        bateu_em_pedra = estado.obstaculos.colidiu_com(personagem)
        if caiu or bateu_em_pedra:
            deve_retornar = True
            if not lupas_perdidas:
                lupas_perdidas = estado.perder_lupas(2)

        resultado = estado.inimigos.verificar_colisao(
            personagem,
            rect_anterior,
        )
        if resultado == "derrotou":
            estado.lupas += RECOMPENSA_INIMIGO
            estado.avisos.adicionar(
                personagem,
                f"+{RECOMPENSA_INIMIGO} LUPAS",
                COR_RECOMPENSA,
            )
        elif resultado == "atingido":
            deve_retornar = True
            if not lupas_perdidas:
                lupas_perdidas = estado.perder_lupas(2)

        return deve_retornar, lupas_perdidas

    def _resolver_retorno(self, deve_retornar, lupas_perdidas):
        if not deve_retornar:
            return

        estado = self.estado
        reposicionar(
            estado.personagem,
            estado.cenario,
            estado.ponto_retorno_x,
        )
        if lupas_perdidas:
            estado.avisos.adicionar(
                estado.personagem,
                f"-{lupas_perdidas} LUPAS",
                COR_PERDA,
            )

    def _atualizar(self):
        estado = self.estado
        x_anterior, rect_anterior = self._atualizar_entidades()
        acao, deve_retornar, lupas_perdidas = self._processar_checkpoint()
        if acao is not AcaoQuadro.CONTINUAR:
            return acao

        deve_retornar, lupas_perdidas = self._processar_perigos(
            rect_anterior,
            deve_retornar,
            lupas_perdidas,
        )
        self._resolver_retorno(deve_retornar, lupas_perdidas)
        if not deve_retornar and estado.houve_movimento(x_anterior):
            estado.iniciar_cronometro()

        atualizar_camera_personagem(estado.cenario, estado.personagem)
        limitar_personagem_na_tela(
            estado.personagem,
            estado.cenario.camera_x,
            self.largura,
        )
        return AcaoQuadro.CONTINUAR

    def _desenhar(self):
        estado = self.estado
        camera_x = estado.cenario.camera_x
        estado.cenario.desenhar(self.tela)
        estado.moedas.desenhar(self.tela, camera_x)
        estado.obstaculos.desenhar(self.tela, camera_x)
        estado.inimigos.desenhar(self.tela, camera_x)
        for checkpoint in estado.checkpoints:
            checkpoint.desenhar(self.tela, camera_x, self.largura)
        estado.personagem.desenhar(self.tela, camera_x)
        estado.avisos.desenhar(self.tela, camera_x)

        if estado.mostrar_controles:
            desenhar_lista_controles(self.tela, self.largura, self.altura)

        desenhar_hud(
            self.tela,
            self.largura,
            estado.numero_fase,
            self.fonte_cronometro,
            self.fonte_fase,
            self.fonte_lupas,
            estado.tempo_inicio,
            estado.lupas,
        )
        pygame.display.flip()

    def executar(self):
        while True:
            acao = self._ler_eventos()
            if acao is AcaoQuadro.SAIR:
                return False
            if acao is AcaoQuadro.REINICIAR:
                self.estado.reiniciar()
                continue

            acao = self._atualizar()
            if acao is AcaoQuadro.REINICIAR:
                self.estado.reiniciar()
                continue
            if acao is AcaoQuadro.MUDOU_FASE:
                continue
            if acao is AcaoQuadro.SAIR:
                return False
            if acao is AcaoQuadro.FINALIZAR:
                return self.jogar_novamente

            self._desenhar()
            self.clock.tick(FPS)


def jogo(tela=None, clock=None):
    """Executa uma partida; aceita tela/relógio para facilitar testes."""
    if not pygame.get_init():
        pygame.init()
    if tela is None:
        tela, _, _ = criar_tela()
    return Jogo(tela, clock).executar()


def main():
    """Inicializa o Pygame uma vez e alterna menu e partida."""
    pygame.init()
    tela, _, _ = criar_tela()
    clock = pygame.time.Clock()

    while tela_inicial(tela, clock):
        iniciar_musica()
        jogar_novamente = jogo(tela, clock)
        parar_musica()
        if not jogar_novamente:
            break

    pygame.quit()


if __name__ == "__main__":
    main()
