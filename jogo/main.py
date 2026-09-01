import pygame

from avisos import AvisosTemporarios
from configuracoes_musica import iniciar_musica, parar_musica
from configuracoes_tela import (
    FPS,
    RECUO_CAMERA_RETORNO,
    atualizar_camera_personagem,
    criar_tela,
    limitar_personagem_na_tela,
)
from fase_final import FaseFinal
from fabrica_fase import criar_fase as montar_fase
from fabrica_fase import reposicionar as reposicionar_na_fase
from hud import desenhar_hud
from menu import desenhar_lista_controles, tela_inicial
from perguntas import Perguntas
from tela_final import TelaFinal


def jogo():
    """Executa uma partida completa, incluindo as três fases e o desafio final."""
    pygame.init()

    tela, largura, altura = criar_tela()

    clock = pygame.time.Clock()
    fonte_cronometro = pygame.font.Font(None, 48)
    fonte_fase = pygame.font.Font(None, 42)
    fonte_moedas = pygame.font.Font(None, 36)
    tempo_inicio = None
    segundos_decorridos = 0
    moedas_coletadas = 0
    avisos = AvisosTemporarios()
    mostrar_controles = True

    perguntas = Perguntas()
    numero_fase = 1

    cenario, personagem, checkpoints, obstaculos, inimigos, moedas = montar_fase(
        numero_fase,
        largura,
        altura
    )
    ponto_retorno_x = RECUO_CAMERA_RETORNO

    rodando = True

    while rodando:
        reiniciar_por_tab = False

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            if (
                evento.type == pygame.KEYDOWN
                and evento.key == pygame.K_ESCAPE
            ):
                rodando = False

            if (
                evento.type == pygame.KEYDOWN
                and evento.key == pygame.K_TAB
            ):
                reiniciar_por_tab = True

        if not rodando:
            break

        if reiniciar_por_tab:
            numero_fase = 1
            perguntas = Perguntas()
            (
                cenario,
                personagem,
                checkpoints,
                obstaculos,
                inimigos,
                moedas
            ) = montar_fase(numero_fase, largura, altura)
            ponto_retorno_x = RECUO_CAMERA_RETORNO
            moedas_coletadas = 0
            tempo_inicio = None
            segundos_decorridos = 0
            mostrar_controles = True
            continue

        x_anterior = personagem.rect.x
        rect_anterior = personagem.rect.copy()
        personagem.atualizar(
            cenario.y_chao,
            obstaculos.personagem_esta_sobre_buraco
        )

        if personagem.rect.x != x_anterior:
            mostrar_controles = False

        limitar_personagem_na_tela(personagem, cenario.camera_x, largura)

        obstaculos.atualizar(cenario.camera_x)
        inimigos.atualizar(
            cenario.camera_x,
            obstaculos.pedras,
            obstaculos.buracos
        )
        moedas.atualizar(
            cenario.camera_x,
            obstaculos.pedras,
            obstaculos.buracos
        )
        lupas_apanhadas = moedas.coletar(personagem)
        moedas_coletadas += lupas_apanhadas
        for _ in range(lupas_apanhadas):
            avisos.adicionar(
                personagem,
                "+1 LUPA",
                (255, 205, 45)
            )
        deve_retornar = False
        lupas_perdidas = 0
        mudou_fase = False

        for checkpoint in checkpoints:
            if checkpoint.foi_alcancado(personagem):
                resposta_correta = perguntas.fazer(
                    tela,
                    numero_fase
                )

                if resposta_correta == "reiniciar":
                    numero_fase = 1
                    perguntas = Perguntas()
                    (
                        cenario,
                        personagem,
                        checkpoints,
                        obstaculos,
                        inimigos,
                        moedas
                    ) = montar_fase(numero_fase, largura, altura)
                    ponto_retorno_x = RECUO_CAMERA_RETORNO
                    moedas_coletadas = 0
                    tempo_inicio = None
                    segundos_decorridos = 0
                    mostrar_controles = True
                    mudou_fase = True
                elif resposta_correta is None:
                    rodando = False
                elif resposta_correta:
                    checkpoint.ativar()
                    ponto_retorno_x = checkpoint.posicao_retorno
                    moedas_coletadas += 5
                    avisos.adicionar(
                        personagem,
                        "+5 LUPAS",
                        (255, 205, 45),
                        duracao=2400
                    )

                    if all(item.ativado for item in checkpoints):
                        if numero_fase == 3:
                            resultado_final, moedas_finais = FaseFinal(
                                largura,
                                altura
                            ).jogar(
                                tela,
                                moedas_coletadas,
                                tempo_inicio
                            )
                            moedas_coletadas = moedas_finais

                            if resultado_final == "venceu":
                                if tempo_inicio is not None:
                                    segundos_decorridos = (
                                        pygame.time.get_ticks() - tempo_inicio
                                    ) // 1000

                                jogar_novamente = TelaFinal().mostrar(
                                    tela,
                                    segundos_decorridos,
                                    moedas_coletadas
                                )
                                return jogar_novamente

                            if resultado_final == "sair":
                                rodando = False
                            else:
                                numero_fase = 1
                                perguntas = Perguntas()
                                (
                                    cenario,
                                    personagem,
                                    checkpoints,
                                    obstaculos,
                                    inimigos,
                                    moedas
                                ) = montar_fase(
                                    numero_fase,
                                    largura,
                                    altura
                                )
                                ponto_retorno_x = RECUO_CAMERA_RETORNO
                                moedas_coletadas = 0
                                if resultado_final == "reiniciar_total":
                                    tempo_inicio = None
                                    segundos_decorridos = 0
                                    mostrar_controles = True
                                mudou_fase = True
                        else:
                            numero_fase += 1
                            (
                                cenario,
                                personagem,
                                checkpoints,
                                obstaculos,
                                inimigos,
                                moedas
                            ) = montar_fase(
                                numero_fase,
                                largura,
                                altura
                            )
                            ponto_retorno_x = RECUO_CAMERA_RETORNO
                            # O bônus do checkpoint acompanha a personagem
                            # e começa novamente ao abrir a próxima fase.
                            avisos.transferir_para(personagem)
                            mudou_fase = True
                else:
                    deve_retornar = True
                    lupas_perdidas = min(4, moedas_coletadas)
                    moedas_coletadas -= lupas_perdidas

                break

        if not rodando:
            break

        if mudou_fase:
            continue

        if personagem.rect.top >= altura:
            # Ao cair, retorna ao início ou ao último checkpoint ativado.
            deve_retornar = True
            if not lupas_perdidas:
                lupas_perdidas = min(2, moedas_coletadas)
                moedas_coletadas -= lupas_perdidas
        elif obstaculos.colidiu_com(personagem):
            deve_retornar = True
            if not lupas_perdidas:
                lupas_perdidas = min(2, moedas_coletadas)
                moedas_coletadas -= lupas_perdidas

        resultado_inimigo = inimigos.verificar_colisao(
            personagem,
            rect_anterior
        )
        if resultado_inimigo == "derrotou":
            moedas_coletadas += 5
            avisos.adicionar(
                personagem,
                "+5 LUPAS",
                (255, 205, 45)
            )
        elif resultado_inimigo == "atingido":
            deve_retornar = True
            if not lupas_perdidas:
                lupas_perdidas = min(2, moedas_coletadas)
                moedas_coletadas -= lupas_perdidas

        if deve_retornar:
            reposicionar_na_fase(
                personagem,
                cenario,
                ponto_retorno_x
            )
            if lupas_perdidas:
                avisos.adicionar(
                    personagem,
                    f"-{lupas_perdidas} LUPAS",
                    (245, 65, 65)
                )
        elif tempo_inicio is None and personagem.rect.x != x_anterior:
            tempo_inicio = pygame.time.get_ticks()

        atualizar_camera_personagem(cenario, personagem)
        limitar_personagem_na_tela(personagem, cenario.camera_x, largura)

        cenario.desenhar(tela)
        moedas.desenhar(tela, cenario.camera_x)
        obstaculos.desenhar(tela, cenario.camera_x)
        inimigos.desenhar(tela, cenario.camera_x)

        for checkpoint in checkpoints:
            checkpoint.desenhar(
                tela,
                cenario.camera_x,
                largura
            )

        personagem.desenhar(tela, cenario.camera_x)
        avisos.desenhar(tela, cenario.camera_x)

        if mostrar_controles:
            desenhar_lista_controles(tela, largura, altura)

        segundos_decorridos = desenhar_hud(
            tela,
            largura,
            numero_fase,
            fonte_cronometro,
            fonte_fase,
            fonte_moedas,
            tempo_inicio,
            moedas_coletadas
        )

        pygame.display.flip()
        clock.tick(FPS)

    return False


def main():
    """Alterna entre o menu e novas partidas até o jogador sair."""

    pygame.init()

    while tela_inicial():
        iniciar_musica()

        # True significa que JOGAR NOVAMENTE foi escolhido na tela final.
        # Nesse caso, o laço volta ao menu antes de iniciar outra partida.
        jogar_novamente = jogo()
        parar_musica()

        if not jogar_novamente:
            break

    pygame.quit()


if __name__ == "__main__":
    main()
