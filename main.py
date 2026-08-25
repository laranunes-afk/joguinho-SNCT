import pygame

from cenario import Cenario
from checkpoint import Checkpoint
from fase_final import FaseFinal
from inimigos import Inimigos
from menu import tela_inicial
from moedas import Moedas
from obstaculos import Obstaculos
from personagem import Personagem
from perguntas import Perguntas
from tela_final import TelaFinal


FONTE_PIXEL = {
    "A": "01110/10001/10001/11111/10001/10001/10001",
    "B": "11110/10001/10001/11110/10001/10001/11110",
    "C": "01111/10000/10000/10000/10000/10000/01111",
    "D": "11110/10001/10001/10001/10001/10001/11110",
    "E": "11111/10000/10000/11110/10000/10000/11111",
    "G": "01111/10000/10000/10111/10001/10001/01111",
    "I": "11111/00100/00100/00100/00100/00100/11111",
    "J": "00111/00010/00010/00010/00010/10010/01100",
    "L": "10000/10000/10000/10000/10000/10000/11111",
    "M": "10001/11011/10101/10101/10001/10001/10001",
    "N": "10001/11001/10101/10011/10001/10001/10001",
    "O": "01110/10001/10001/10001/10001/10001/01110",
    "P": "11110/10001/10001/11110/10000/10000/10000",
    "R": "11110/10001/10001/11110/10100/10010/10001",
    "S": "01111/10000/10000/01110/00001/00001/11110",
    "T": "11111/00100/00100/00100/00100/00100/00100",
    "U": "10001/10001/10001/10001/10001/10001/01110",
    "W": "10001/10001/10001/10001/10101/11011/10001",
    "/": "00001/00010/00100/01000/10000/00000/00000"
}


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
        areas_livres
    )

    moedas = Moedas(
        largura,
        cenario.y_chao,
        areas_livres
    )
    moedas.atualizar(0, obstaculos.pedras, obstaculos.buracos)

    return cenario, personagem, checkpoints, obstaculos, inimigos, moedas


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


def desenhar_tutorial_controles(tela, largura):
    """Mostra os controles no inicio da primeira fase."""

    x_inicial = max(20, (largura - 460) // 2)
    y_inicial = 92
    branco = (255, 255, 255)

    def criar_texto_pixel(texto, escala=2):
        largura_caractere = 6 * escala
        largura_texto = max(1, len(texto) * largura_caractere - escala)
        superficie = pygame.Surface(
            (largura_texto, 7 * escala),
            pygame.SRCALPHA
        )

        for indice, caractere in enumerate(texto):
            desenho = FONTE_PIXEL.get(caractere)
            if desenho is None:
                continue

            for linha, pixels in enumerate(desenho.split("/")):
                for coluna, pixel in enumerate(pixels):
                    if pixel == "1":
                        pygame.draw.rect(
                            superficie,
                            branco,
                            (
                                indice * largura_caractere + coluna * escala,
                                linha * escala,
                                escala,
                                escala
                            )
                        )

        return superficie

    def desenhar_tecla(texto, x, y):
        largura_tecla = 64 if len(texto) > 1 else 34
        rect = pygame.Rect(x, y, largura_tecla, 32)
        pygame.draw.rect(tela, branco, rect, width=3)
        tecla = criar_texto_pixel(texto, 3)
        tela.blit(tecla, tecla.get_rect(center=rect.center))
        return rect

    def desenhar_seta(inicio, fim):
        pygame.draw.line(tela, branco, inicio, fim, 3)
        pygame.draw.polygon(
            tela,
            branco,
            [
                fim,
                (fim[0] - 9, fim[1] - 5),
                (fim[0] - 9, fim[1] + 5)
            ]
        )

    tecla_w = desenhar_tecla("W", x_inicial + 40, y_inicial)
    tecla_a = desenhar_tecla("A", x_inicial, y_inicial + 38)
    tecla_d = desenhar_tecla("D", x_inicial + 80, y_inicial + 38)

    inicio_andar = (tecla_d.right + 8, tecla_d.centery)
    fim_andar = (x_inicial + 180, tecla_d.centery)
    desenhar_seta(inicio_andar, fim_andar)
    andar = criar_texto_pixel("ANDAR / SETAS")
    tela.blit(andar, (fim_andar[0] + 10, fim_andar[1] - 10))

    inicio_pular = (tecla_w.right + 8, tecla_w.centery)
    fim_pular = (x_inicial + 180, tecla_w.centery)
    desenhar_seta(inicio_pular, fim_pular)
    pular = criar_texto_pixel("PULAR / SETA PARA CIMA")
    tela.blit(pular, (fim_pular[0] + 10, fim_pular[1] - 10))

    tecla_esc = desenhar_tecla("ESC", x_inicial, y_inicial + 86)
    fim_sair = (x_inicial + 180, tecla_esc.centery)
    desenhar_seta((tecla_esc.right + 8, tecla_esc.centery), fim_sair)
    sair = criar_texto_pixel("SAIR DO JOGO")
    tela.blit(sair, (fim_sair[0] + 10, fim_sair[1] - 10))

    tecla_tab = desenhar_tecla("TAB", x_inicial, y_inicial + 134)
    fim_reiniciar = (x_inicial + 180, tecla_tab.centery)
    desenhar_seta((tecla_tab.right + 8, tecla_tab.centery), fim_reiniciar)
    reiniciar = criar_texto_pixel("REINICIAR JOGO")
    tela.blit(
        reiniciar,
        (fim_reiniciar[0] + 10, fim_reiniciar[1] - 10)
    )


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
    tutorial_visivel = True

    perguntas = Perguntas()
    numero_fase = 1

    cenario, personagem, checkpoints, obstaculos, inimigos, moedas = criar_fase(
        numero_fase,
        largura,
        altura
    )
    ponto_retorno_x = 30

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
            ponto_retorno_x = 30
            moedas_coletadas = 0
            tempo_inicio = None
            segundos_decorridos = 0
            tutorial_visivel = True
            continue

        x_anterior = personagem.rect.x
        rect_anterior = personagem.rect.copy()
        personagem.atualizar(
            cenario.y_chao,
            obstaculos.personagem_esta_sobre_buraco
        )

        if personagem.rect.left < cenario.camera_x:
            personagem.rect.left = cenario.camera_x

        if personagem.rect.right > cenario.camera_x + largura:
            personagem.rect.right = cenario.camera_x + largura

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
        moedas_coletadas += moedas.coletar(personagem)
        deve_retornar = False
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
                    ponto_retorno_x = 30
                    moedas_coletadas = 0
                    tempo_inicio = None
                    segundos_decorridos = 0
                    tutorial_visivel = True
                    mudou_fase = True
                elif resposta_correta is None:
                    rodando = False
                elif resposta_correta:
                    checkpoint.ativar()
                    ponto_retorno_x = checkpoint.posicao_retorno
                    moedas_coletadas += 5

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
                                ponto_retorno_x = 30
                                moedas_coletadas = 0
                                tutorial_visivel = True
                                if resultado_final == "reiniciar_total":
                                    tempo_inicio = None
                                    segundos_decorridos = 0
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

        resultado_inimigo = inimigos.verificar_colisao(
            personagem,
            rect_anterior
        )
        if resultado_inimigo == "derrotou":
            moedas_coletadas += 5
        elif resultado_inimigo == "atingido":
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

        if personagem.rect.x != x_anterior:
            tutorial_visivel = False

        cenario.seguir_personagem(personagem)

        if personagem.rect.left < cenario.camera_x:
            personagem.rect.left = cenario.camera_x

        if personagem.rect.right > cenario.camera_x + largura:
            personagem.rect.right = cenario.camera_x + largura

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

        if numero_fase == 1 and tutorial_visivel:
            desenhar_tutorial_controles(
                tela,
                largura
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
