import pygame

from cenario import Cenario
from checkpoint import Checkpoint
from configuracoes_tela import (
    FPS,
    RECUO_CAMERA_RETORNO,
    atualizar_camera_personagem,
    criar_tela,
    limitar_personagem_na_tela,
)
from fase_final import FaseFinal
from hud import desenhar_hud
from inimigos import Inimigos
from menu import desenhar_lista_controles, tela_inicial
from moedas import Moedas
from obstaculos import Obstaculos
from personagem import Personagem
from perguntas import Perguntas
from tela_final import TelaFinal


def adicionar_texto_temporario(
    textos,
    personagem,
    texto,
    cor,
    duracao=1100
):
    """Cria um aviso flutuante ancorado acima da personagem."""
    textos.append(
        {
            "texto": texto,
            "cor": cor,
            "x": personagem.rect.centerx,
            "y": personagem.rect.top - 12,
            "inicio": pygame.time.get_ticks(),
            "duracao": duracao,
        }
    )


def desenhar_textos_temporarios(tela, textos, camera_x):
    """Desenha avisos pixelados que sobem e desaparecem suavemente."""
    agora = pygame.time.get_ticks()
    fonte_base = pygame.font.Font(None, 18)
    ativos = []

    for aviso in textos:
        decorrido = agora - aviso["inicio"]
        duracao = aviso["duracao"]
        if decorrido >= duracao:
            continue

        progresso = decorrido / duracao
        superficie_base = fonte_base.render(
            aviso["texto"],
            False,
            aviso["cor"]
        )
        superficie = pygame.transform.scale(
            superficie_base,
            (superficie_base.get_width() * 2, superficie_base.get_height() * 2)
        )
        superficie.set_alpha(int(255 * (1 - progresso)))
        rect = superficie.get_rect(
            midbottom=(
                int(aviso["x"] - camera_x),
                int(aviso["y"] - progresso * 38)
            )
        )
        tela.blit(superficie, rect)
        ativos.append(aviso)

    textos[:] = ativos


def criar_fase(numero_fase, largura, altura):
    """Cria todos os objetos necessários para uma fase."""

    cenario = Cenario(
        largura,
        altura,
        numero_fase
    )

    personagem = Personagem(
        30,
        cenario.y_chao - 80
    )

    primeiro_checkpoint = largura + 250
    distancia_checkpoints = max(1100, largura)

    checkpoints = [
        Checkpoint(
            primeiro_checkpoint + indice * distancia_checkpoints,
            cenario.y_chao
        )
        for indice in range(2)
    ]

    areas_livres = [
        checkpoint.area_livre
        for checkpoint in checkpoints
    ]

    obstaculos = Obstaculos(
        largura,
        cenario.y_chao,
        areas_livres
    )
    inimigos = Inimigos(
        largura,
        cenario.y_chao,
        areas_livres,
        numero_fase
    )

    moedas = Moedas(
        largura,
        cenario.y_chao,
        areas_livres
    )
    moedas.atualizar(0, obstaculos.pedras, obstaculos.buracos)

    return cenario, personagem, checkpoints, obstaculos, inimigos, moedas


def reposicionar(personagem, cenario, ponto_retorno_x):
    """Leva a personagem ao último ponto seguro e restaura sua queda."""
    personagem.rect.left = ponto_retorno_x
    personagem.rect.bottom = cenario.y_chao
    personagem.velocidade_y = 0
    personagem.no_chao = True
    personagem.caindo_no_buraco = False

    cenario.camera_x = max(
        cenario.inicio_mundo,
        ponto_retorno_x - RECUO_CAMERA_RETORNO
    )


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
    textos_temporarios = []
    mostrar_controles = True

    perguntas = Perguntas()
    numero_fase = 1

    cenario, personagem, checkpoints, obstaculos, inimigos, moedas = criar_fase(
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
            ) = criar_fase(numero_fase, largura, altura)
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
            adicionar_texto_temporario(
                textos_temporarios,
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
                    ) = criar_fase(numero_fase, largura, altura)
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
                    adicionar_texto_temporario(
                        textos_temporarios,
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
                                ) = criar_fase(
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
                            ) = criar_fase(
                                numero_fase,
                                largura,
                                altura
                            )
                            ponto_retorno_x = RECUO_CAMERA_RETORNO
                            # O bônus do checkpoint acompanha a personagem
                            # e começa novamente ao abrir a próxima fase.
                            if textos_temporarios:
                                bonus = textos_temporarios[-1]
                                bonus["x"] = personagem.rect.centerx
                                bonus["y"] = personagem.rect.top - 12
                                bonus["inicio"] = pygame.time.get_ticks()
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
            adicionar_texto_temporario(
                textos_temporarios,
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
            reposicionar(
                personagem,
                cenario,
                ponto_retorno_x
            )
            if lupas_perdidas:
                adicionar_texto_temporario(
                    textos_temporarios,
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
        desenhar_textos_temporarios(
            tela,
            textos_temporarios,
            cenario.camera_x
        )

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
        # True significa que JOGAR NOVAMENTE foi escolhido na tela final.
        # Nesse caso, o laço volta ao menu antes de iniciar outra partida.
        if not jogo():
            break

    pygame.quit()


if __name__ == "__main__":
    main()
