import ast
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

RAIZ = Path(__file__).resolve().parents[1]
PASTA_JOGO = RAIZ / "jogo"
sys.path.insert(0, str(PASTA_JOGO))

import pygame  # noqa: E402

from dados_perguntas import DESAFIOS_FINAIS, PERGUNTAS_POR_FASE  # noqa: E402
from fabrica_fase import criar_fase, reposicionar  # noqa: E402
from personagem import Personagem  # noqa: E402


class TesteEstrutura(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((640, 480))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_todos_os_modulos_possuem_sintaxe_valida(self):
        for caminho in PASTA_JOGO.glob("*.py"):
            with self.subTest(arquivo=caminho.name):
                ast.parse(caminho.read_text(encoding="utf-8"), filename=caminho)

    def test_perguntas_possuem_resposta_valida(self):
        perguntas = [
            pergunta
            for lista in PERGUNTAS_POR_FASE.values()
            for pergunta in lista
        ]
        perguntas.extend(desafio.pergunta for desafio in DESAFIOS_FINAIS)

        for enunciado, respostas, correta in perguntas:
            with self.subTest(pergunta=enunciado):
                self.assertTrue(enunciado)
                self.assertGreaterEqual(len(respostas), 2)
                self.assertIn(correta, range(len(respostas)))

    def test_animacao_tem_pose_parada_e_oito_quadros_alinhados(self):
        personagem = Personagem(30, 100)
        self.assertEqual(len(personagem.quadros_direita), 8)
        self.assertTrue(personagem.quadro_parado_direita)
        for quadro in personagem.quadros_direita:
            self.assertEqual(
                quadro.get_bounding_rect(min_alpha=1).bottom,
                personagem.altura_visual,
            )

    def test_pulo_exige_um_novo_toque_na_tecla(self):
        personagem = Personagem(30, 100)
        pressionadas = {pygame.K_w}

        class Teclas:
            def __getitem__(self, tecla):
                return tecla in pressionadas

        with patch("pygame.key.get_pressed", return_value=Teclas()):
            personagem.no_chao = True
            personagem.pular()
            self.assertEqual(personagem.velocidade_y, personagem.forca_pulo)

            personagem.no_chao = True
            personagem.velocidade_y = 0
            personagem.pular()
            self.assertEqual(personagem.velocidade_y, 0)

            pressionadas.clear()
            personagem.pular()
            pressionadas.add(pygame.K_w)
            personagem.pular()
            self.assertEqual(personagem.velocidade_y, personagem.forca_pulo)

    def test_fabrica_monta_e_reposiciona_as_tres_fases(self):
        for numero_fase in range(1, 4):
            with self.subTest(fase=numero_fase):
                pecas = criar_fase(numero_fase, 640, 480)
                self.assertEqual(len(pecas), 6)
                cenario, personagem, checkpoints, *_ = pecas
                self.assertEqual(len(checkpoints), 2)

                reposicionar(personagem, cenario, 120)
                self.assertEqual(personagem.rect.bottom, cenario.y_chao)
                self.assertTrue(personagem.no_chao)


if __name__ == "__main__":
    unittest.main()
