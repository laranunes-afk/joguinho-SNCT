import pygame

from cenario import Cenario
from checkpoint import Checkpoint
from menu import tela_inicial
from moedas import Moedas
from obstaculos import Obstaculos
from personagem import Personagem
from perguntas import Perguntas
from tela_final import TelaFinal


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

    moedas = Moedas(
        largura,
        cenario.y_chao,
        areas_livres
    )
    moedas.atualizar(0, obstaculos.pedras, obstaculos.buracos)

    return cenario, personagem, checkpoints, obstaculos, moedas


def reposicionar(personagem, cenario, ponto_retorno_x):
    personagem.rect.left = ponto_retorno_x
    personagem.rect.bottom = cenario.y_chao
    personagem.velocidade_y = 0
    personagem.no_chao = True

    cenario.camera_x = max(
        cenario.inicio_mundo,
        ponto_retorno_x - 30
    )


def desenhar_hud(
    tela,
    largura,
    numero_fase,
    fonte_cronometro,
    fonte_fase,
    fonte_moedas,
    tempo_inicio,
    moedas_coletadas
):
    if tempo_inicio is None:
        segundos_decorridos = 0
    else:
        segundos_decorridos = (
            pygame.time.get_ticks() - tempo_inicio
        ) // 1000

    minutos = segundos_decorridos // 60
    segundos = segundos_decorridos % 60

    texto_fase = fonte_fase.render(
        f"FASE {numero_fase}/3",
        True,
        (255, 255, 255)
    )
    fundo_fase = texto_fase.get_rect(topleft=(30, 25)).inflate(24, 14)
    pygame.draw.rect(tela, (25, 35, 55), fundo_fase, border_radius=10)
    tela.blit(texto_fase, texto_fase.get_rect(topleft=(30, 25)))

    texto_cronometro = fonte_cronometro.render(
        f"{minutos:02d}:{segundos:02d}",
        True,
        (255, 255, 255)
    )
    rect_cronometro = texto_cronometro.get_rect(
        topright=(largura - 30, 25)
    )
    fundo_cronometro = rect_cronometro.inflate(24, 14)
    pygame.draw.rect(
        tela,
        (25, 35, 55),
        fundo_cronometro,
        border_radius=10
    )
    tela.blit(texto_cronometro, rect_cronometro)

    texto_moedas = fonte_moedas.render(
        f"LUPAS: {moedas_coletadas}",
        True,
        (255, 215, 55)
    )
    rect_moedas = texto_moedas.get_rect(
        topright=(largura - 30, 88)
    )
    fundo_moedas = rect_moedas.inflate(24, 14)
    pygame.draw.rect(
        tela,
        (25, 35, 55),
        fundo_moedas,
        border_radius=10
    )
    tela.blit(texto_moedas, rect_moedas)

    return segundos_decorridos


def jogo():
    pygame.init()

    tela = pygame.display.set_mode(
        (0, 0),
        pygame.FULLSCREEN
    )
    largura, altura = tela.get_size()
    pygame.display.set_caption("Jogo de Perguntas - 3 Fases")

    fps = 60
    clock = pygame.time.Clock()
    fonte_cronometro = pygame.font.Font(None, 48)
    fonte_fase = pygame.font.Font(None, 42)
    fonte_moedas = pygame.font.Font(None, 36)
    tempo_inicio = None
    segundos_decorridos = 0
    moedas_coletadas = 0

    perguntas = Perguntas()
    numero_fase = 1

    cenario, personagem, checkpoints, obstaculos, moedas = criar_fase(
        numero_fase,
        largura,
        altura
    )
    ponto_retorno_x = 30

    rodando = True

    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            if (
                evento.type == pygame.KEYDOWN
                and evento.key == pygame.K_ESCAPE
            ):
                rodando = False

        if not rodando:
            break

        x_anterior = personagem.rect.x
        personagem.atualizar(
            cenario.y_chao,
            obstaculos.personagem_esta_sobre_buraco
        )

        if personagem.rect.left < cenario.camera_x:
            personagem.rect.left = cenario.camera_x

        if personagem.rect.right > cenario.camera_x + largura:
            personagem.rect.right = cenario.camera_x + largura

        obstaculos.atualizar(cenario.camera_x)
        moedas.atualizar(
            cenario.camera_x,
            obstaculos.pedras,
            obstaculos.buracos
        )
        moedas_coletadas += moedas.coletar(personagem)
        deve_retornar = False
        mudou_fase = False

        for checkpoint in checkpoints:
            if checkpoint.foi_alcancado(personagem):
                resposta_correta = perguntas.fazer(
                    tela,
                    numero_fase
                )

                if resposta_correta is None:
                    rodando = False
                elif resposta_correta:
                    checkpoint.ativar()
                    ponto_retorno_x = checkpoint.posicao_retorno
                    moedas_coletadas += 5

                    if all(item.ativado for item in checkpoints):
                        if numero_fase == 3:
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
                        else:
                            numero_fase += 1
                            (
                                cenario,
                                personagem,
                                checkpoints,
                                obstaculos,
                                moedas
                            ) = criar_fase(
                                numero_fase,
                                largura,
                                altura
                            )
                            ponto_retorno_x = 30
                            mudou_fase = True
                else:
                    deve_retornar = True

                break

        if not rodando:
            break

        if mudou_fase:
            continue

        if personagem.rect.top >= altura:
            # Ao cair, retorna ao início ou ao último checkpoint ativado.
            deve_retornar = True
            moedas_coletadas = max(0, moedas_coletadas - 2)
        elif obstaculos.colidiu_com(personagem):
            deve_retornar = True
            moedas_coletadas = max(0, moedas_coletadas - 2)

        if deve_retornar:
            reposicionar(
                personagem,
                cenario,
                ponto_retorno_x
            )
        elif tempo_inicio is None and personagem.rect.x != x_anterior:
            tempo_inicio = pygame.time.get_ticks()

        cenario.seguir_personagem(personagem)

        if personagem.rect.left < cenario.camera_x:
            personagem.rect.left = cenario.camera_x

        if personagem.rect.right > cenario.camera_x + largura:
            personagem.rect.right = cenario.camera_x + largura

        cenario.desenhar(tela)
        moedas.desenhar(tela, cenario.camera_x)
        obstaculos.desenhar(tela, cenario.camera_x)

        for checkpoint in checkpoints:
            checkpoint.desenhar(
                tela,
                cenario.camera_x,
                largura
            )

        personagem.desenhar(tela, cenario.camera_x)

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
        clock.tick(fps)

    return False


def main():
    """Abre o menu e inicia o jogo quando JOGAR for clicado."""

    pygame.init()

    if tela_inicial():
        jogar_novamente = True

        while jogar_novamente:
            jogar_novamente = jogo()

    pygame.quit()


if __name__ == "__main__":
    main()
