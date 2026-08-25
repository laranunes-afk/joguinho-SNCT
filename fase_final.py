import pygame

from personagem import Personagem


class PessoaFinal:
    """Pessoa que apresenta um dos desafios da fase final."""

    def __init__(self, x, y_chao, cor, pergunta):
        self.rect = pygame.Rect(x, y_chao - 82, 52, 82)
        self.cor = cor
        self.pergunta = pergunta
        self.respondida = False

    def desenhar(self, tela, camera_x):
        x = int(self.rect.centerx - camera_x)
        y = self.rect.top

        pygame.draw.circle(tela, (235, 190, 150), (x, y + 17), 16)
        pygame.draw.rect(
            tela,
            self.cor,
            (x - 19, y + 34, 38, 38),
            border_radius=7
        )
        pygame.draw.line(tela, (30, 38, 58), (x - 11, y + 72), (x - 14, y + 82), 5)
        pygame.draw.line(tela, (30, 38, 58), (x + 11, y + 72), (x + 14, y + 82), 5)

        if not self.respondida:
            pygame.draw.circle(tela, (255, 255, 255), (x, y - 15), 15)
            fonte = pygame.font.Font(None, 28)
            interrogacao = fonte.render("?", True, (30, 38, 58))
            tela.blit(interrogacao, interrogacao.get_rect(center=(x, y - 14)))


class FaseFinal:
    """Cenario final com tres pessoas e tres perguntas dificeis."""

    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura
        self.y_chao = altura - 100
        self.camera_x = 0
        self.personagem = Personagem(40, self.y_chao - 80)

        inicio = max(620, int(largura * 0.65))
        distancia = max(620, int(largura * 0.6))
        perguntas = [
            (
                "Quanto e 12 multiplicado por 8?",
                ["86", "92", "96", "108"],
                2
            ),
            (
                "Qual planeta e conhecido como Planeta Vermelho?",
                ["Venus", "Marte", "Jupiter", "Saturno"],
                1
            ),
            (
                "Qual linguagem e usada para estruturar paginas da internet?",
                ["HTML", "Python", "SQL", "C++"],
                0
            ),
        ]
        cores = [(65, 145, 210), (220, 115, 70), (105, 180, 105)]
        self.pessoas = [
            PessoaFinal(
                inicio + indice * distancia,
                self.y_chao,
                cores[indice],
                perguntas[indice]
            )
            for indice in range(3)
        ]
        self.fim_mundo = self.pessoas[-1].rect.right + largura // 2

    def _desenhar_cenario(self, tela):
        tela.fill((24, 30, 55))

        for indice in range(30):
            x_mundo = indice * 173 + 70
            x = int(x_mundo - self.camera_x * 0.25) % (self.largura + 100)
            y = 45 + (indice * 67) % max(100, self.altura // 2)
            pygame.draw.rect(tela, (220, 230, 255), (x, y, 3, 3))

        pygame.draw.rect(
            tela,
            (42, 55, 78),
            (0, self.y_chao, self.largura, self.altura - self.y_chao)
        )
        pygame.draw.rect(tela, (225, 235, 245), (0, self.y_chao, self.largura, 5))

    def _desenhar_hud(self, tela, lupas, tempo_inicio):
        fonte_titulo = pygame.font.Font(None, 42)
        fonte_texto = pygame.font.Font(None, 28)
        respondidas = sum(pessoa.respondida for pessoa in self.pessoas)

        titulo = fonte_titulo.render("DESAFIO FINAL", True, (255, 225, 90))
        tela.blit(titulo, (30, 24))

        progresso = fonte_texto.render(
            f"PERGUNTAS: {respondidas}/3",
            True,
            (255, 255, 255)
        )
        tela.blit(progresso, (30, 66))

        texto_lupas = fonte_texto.render(
            f"LUPAS: {lupas}",
            True,
            (255, 215, 55)
        )
        tela.blit(texto_lupas, (30, 94))

        segundos_totais = (
            (pygame.time.get_ticks() - tempo_inicio) // 1000
            if tempo_inicio is not None
            else 0
        )
        cronometro = fonte_titulo.render(
            f"{segundos_totais // 60:02d}:{segundos_totais % 60:02d}",
            True,
            (255, 255, 255)
        )
        tela.blit(
            cronometro,
            cronometro.get_rect(topright=(self.largura - 30, 24))
        )

        instrucao = fonte_texto.render(
            "SIGA EM FRENTE E FALE COM AS TRES PESSOAS",
            True,
            (225, 230, 245)
        )
        tela.blit(
            instrucao,
            instrucao.get_rect(midtop=(self.largura // 2, 28))
        )

    def _fazer_pergunta(self, tela, pessoa, numero):
        pergunta, respostas, correta = pessoa.pergunta
        fonte_titulo = pygame.font.Font(None, 52)
        fonte_pergunta = pygame.font.Font(None, 38)
        fonte_resposta = pygame.font.Font(None, 32)
        fonte_aviso = pygame.font.Font(None, 27)
        clock = pygame.time.Clock()

        largura_botao = min(820, self.largura - 100)
        botoes = []
        inicio_y = max(205, self.altura // 3)

        for indice in range(4):
            rect = pygame.Rect(
                (self.largura - largura_botao) // 2,
                inicio_y + indice * 76,
                largura_botao,
                58
            )
            botoes.append(rect)

        teclas = {
            pygame.K_a: 0,
            pygame.K_b: 1,
            pygame.K_c: 2,
            pygame.K_d: 3,
        }

        while True:
            pos_mouse = pygame.mouse.get_pos()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return None

                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        return None
                    if evento.key == pygame.K_TAB:
                        return "reiniciar"
                    if evento.key in teclas:
                        return teclas[evento.key] == correta

                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    for indice, botao in enumerate(botoes):
                        if botao.collidepoint(evento.pos):
                            return indice == correta

            tela.fill((18, 24, 45))
            titulo = fonte_titulo.render(
                f"PERGUNTA DIFICIL {numero}/3",
                True,
                (255, 215, 70)
            )
            tela.blit(titulo, titulo.get_rect(center=(self.largura // 2, 62)))

            texto_pergunta = fonte_pergunta.render(pergunta, True, (255, 255, 255))
            tela.blit(
                texto_pergunta,
                texto_pergunta.get_rect(center=(self.largura // 2, 135))
            )

            for indice, botao in enumerate(botoes):
                cor = (80, 135, 180) if botao.collidepoint(pos_mouse) else (48, 75, 112)
                pygame.draw.rect(tela, cor, botao, border_radius=9)
                resposta = fonte_resposta.render(
                    f"{'ABCD'[indice]}) {respostas[indice]}",
                    True,
                    (255, 255, 255)
                )
                tela.blit(resposta, resposta.get_rect(center=botao.center))

            aviso = fonte_aviso.render(
                "SE ERRAR, VOCE VOLTA AO INICIO DA FASE 1",
                True,
                (245, 120, 110)
            )
            tela.blit(
                aviso,
                aviso.get_rect(center=(self.largura // 2, self.altura - 58))
            )
            reinicio = fonte_aviso.render(
                "TAB REINICIA TODA A JOGATINA",
                True,
                (225, 230, 245)
            )
            tela.blit(
                reinicio,
                reinicio.get_rect(center=(self.largura // 2, self.altura - 28))
            )
            pygame.display.flip()
            clock.tick(60)

    def jogar(self, tela, lupas_iniciais=0, tempo_inicio=None):
        """Retorna o resultado da fase e a quantidade atual de lupas."""
        clock = pygame.time.Clock()
        lupas = lupas_iniciais

        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return "sair", lupas
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    return "sair", lupas
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_TAB:
                    return "reiniciar_total", lupas

            self.personagem.atualizar(self.y_chao)
            self.personagem.rect.left = max(0, self.personagem.rect.left)
            self.personagem.rect.right = min(self.fim_mundo, self.personagem.rect.right)

            for numero, pessoa in enumerate(self.pessoas, start=1):
                if pessoa.respondida or not self.personagem.rect.colliderect(pessoa.rect):
                    continue

                resposta_correta = self._fazer_pergunta(tela, pessoa, numero)
                if resposta_correta is None:
                    return "sair", lupas
                if resposta_correta == "reiniciar":
                    return "reiniciar_total", lupas
                if not resposta_correta:
                    return "reiniciar", lupas

                pessoa.respondida = True
                lupas += 10
                self.personagem.rect.left = pessoa.rect.right + 20
                break

            if all(pessoa.respondida for pessoa in self.pessoas):
                return "venceu", lupas

            margem = self.largura * 0.42
            alvo_camera = self.personagem.rect.centerx - margem
            limite_camera = max(0, self.fim_mundo - self.largura)
            self.camera_x = max(0, min(alvo_camera, limite_camera))

            self._desenhar_cenario(tela)
            for pessoa in self.pessoas:
                pessoa.desenhar(tela, self.camera_x)
            self.personagem.desenhar(tela, self.camera_x)
            self._desenhar_hud(tela, lupas, tempo_inicio)

            pygame.display.flip()
            clock.tick(60)
