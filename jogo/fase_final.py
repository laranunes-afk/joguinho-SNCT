import pygame

from interface_fase_final import InterfaceFaseFinal
from pergunta_final import PerguntaFinal
from personagem import Personagem
from pessoa_final import PessoaFinal
from tesouro_final import TesouroFinal


PERGUNTAS_FINAIS = [
    ("Quanto e 12 multiplicado por 8?", ["86", "92", "96", "108"], 2),
    (
        "Qual planeta e conhecido como Planeta Vermelho?",
        ["Venus", "Marte", "Jupiter", "Saturno"],
        1,
    ),
    (
        "Qual linguagem e usada para estruturar paginas da internet?",
        ["HTML", "Python", "SQL", "C++"],
        0,
    ),
]

APRESENTADORES = [
    ((65, 145, 210), "personagem-1-mesma-escala.png", 90),
    ((220, 115, 70), "personagem-2-mesma-escala.png", 90),
    ((105, 180, 105), "ELIAS.png", 100),
]


class FaseFinal:
    """Coordena as pecas independentes do desafio final."""

    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura
        # Mantem a mesma altura e proporcao de chao das fases comuns.
        self.y_chao = altura - int(altura * 0.35)
        self.camera_x = 0
        self.personagem = Personagem(40, self.y_chao - 80)
        self.inicio_bonus_checkpoint = pygame.time.get_ticks()
        self.interface = InterfaceFaseFinal(largura, altura, self.y_chao)
        self.tesouro = TesouroFinal()

        inicio = max(620, int(largura * 0.65))
        distancia = max(620, int(largura * 0.6))
        self.pessoas = [
            PessoaFinal(
                inicio + indice * distancia,
                self.y_chao,
                cor,
                PERGUNTAS_FINAIS[indice],
                imagem,
                altura_imagem,
            )
            for indice, (cor, imagem, altura_imagem) in enumerate(APRESENTADORES)
        ]
        self.pergunta = PerguntaFinal(largura, altura, len(self.pessoas))
        self.fim_mundo = self.pessoas[-1].rect.right + largura // 2

    def _atualizar_personagem(self, lupas):
        """Atualiza movimento normal ou a caminhada do tesouro."""
        agora = pygame.time.get_ticks()
        if self.tesouro.em_andamento:
            recompensa = self.tesouro.atualizar(self.personagem, self.y_chao, agora)
            return lupas + recompensa

        self.personagem.atualizar(self.y_chao)
        self.tesouro.tentar_iniciar(self.personagem, agora)
        self.tesouro.limitar_saida_usada(self.personagem)
        return lupas

    def _verificar_perguntas(self, tela, lupas):
        """Processa o encontro com um apresentador."""
        for numero, pessoa in enumerate(self.pessoas, start=1):
            if pessoa.respondida or not self.personagem.rect.colliderect(pessoa.rect):
                continue

            resposta = self.pergunta.fazer(tela, pessoa.pergunta, numero)
            if resposta is None:
                return "sair", lupas
            if resposta == "reiniciar":
                return "reiniciar_total", lupas
            if not resposta:
                return "reiniciar", lupas

            pessoa.respondida = True
            self.personagem.rect.left = pessoa.rect.right + 20
            return None, lupas + 10

        return None, lupas

    def _atualizar_camera(self):
        margem = self.largura * 0.42
        alvo = self.personagem.rect.centerx - margem
        limite = max(0, self.fim_mundo - self.largura)
        self.camera_x = max(0, min(alvo, limite))

    def _desenhar(self, tela, lupas, tempo_inicio):
        self.interface.desenhar_cenario(tela, self.camera_x)
        for pessoa in self.pessoas:
            pessoa.desenhar(tela, self.camera_x)
        self.personagem.desenhar(tela, self.camera_x)
        self.interface.desenhar_bonus_checkpoint(
            tela, self.personagem, self.camera_x, self.inicio_bonus_checkpoint
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
        """Executa a fase e retorna seu resultado e o total de lupas."""
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

            rect_anterior = self.personagem.rect.copy()
            lupas = self._atualizar_personagem(lupas)
            self.personagem.rect.right = min(self.fim_mundo, self.personagem.rect.right)

            if not self.tesouro.em_andamento:
                for pessoa in self.pessoas:
                    pessoa.bloquear_passagem(self.personagem, rect_anterior)
                resultado, lupas = self._verificar_perguntas(tela, lupas)
                if resultado is not None:
                    return resultado, lupas

            if all(pessoa.respondida for pessoa in self.pessoas):
                return "venceu", lupas

            self._atualizar_camera()
            self._desenhar(tela, lupas, tempo_inicio)
            pygame.display.flip()
            clock.tick(60)
