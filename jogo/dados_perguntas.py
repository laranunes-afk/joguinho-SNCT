TIPOS_DE_PERGUNTA = {
    1: "CONHECIMENTOS GERAIS",
    2: "MATEMÁTICA",
    3: "CIÊNCIAS",
}

PERGUNTAS_POR_FASE = {
    1: [
        (
            "Qual é a capital do Brasil?",
            ["Brasília", "Salvador", "São Paulo", "Recife"],
            0,
        ),
        (
            "Em qual continente fica o Brasil?",
            ["Europa", "Ásia", "América do Sul", "África"],
            2,
        ),
        ("Quantos dias possui uma semana?", ["Cinco", "Seis", "Sete", "Oito"], 2),
        (
            "Qual idioma é falado oficialmente no Brasil?",
            ["Espanhol", "Português", "Inglês", "Francês"],
            1,
        ),
    ],
    2: [
        ("Quanto é 7 x 8?", ["48", "54", "56", "64"], 2),
        ("Quanto é 100 dividido por 4?", ["20", "25", "30", "40"], 1),
        ("Quanto é 35 + 27?", ["52", "60", "62", "72"], 2),
        ("Quantos lados possui um hexágono?", ["Cinco", "Seis", "Sete", "Oito"], 1),
    ],
    3: [
        (
            "Qual é o maior planeta do Sistema Solar?",
            ["Terra", "Marte", "Saturno", "Júpiter"],
            3,
        ),
        (
            "Qual destes animais é um mamífero?",
            ["Tubarão", "Golfinho", "Polvo", "Pinguim"],
            1,
        ),
        (
            "Qual gás é essencial para a respiração humana?",
            ["Oxigênio", "Hélio", "Hidrogênio", "Neônio"],
            0,
        ),
        (
            "A água congela normalmente a quantos graus Celsius?",
            ["0", "10", "50", "100"],
            0,
        ),
    ],
}


class DesafioFinal:
    """Une um apresentador à sua pergunta, evitando listas paralelas."""

    def __init__(self, cor, imagem, altura_imagem, pergunta):
        self.cor = cor
        self.imagem = imagem
        self.altura_imagem = altura_imagem
        self.pergunta = pergunta


DESAFIOS_FINAIS = (
    DesafioFinal(
        (65, 145, 210),
        "personagem-1-mesma-escala.png",
        118,
        ("Quanto e 12 multiplicado por 8?", ["86", "92", "96", "108"], 2),
    ),
    DesafioFinal(
        (220, 115, 70),
        "personagem-2-mesma-escala.png",
        118,
        (
            "Qual planeta e conhecido como Planeta Vermelho?",
            ["Venus", "Marte", "Jupiter", "Saturno"],
            1,
        ),
    ),
    DesafioFinal(
        (105, 180, 105),
        "ELIAS.png",
        118,
        (
            "Qual linguagem e usada para estruturar paginas da internet?",
            ["HTML", "Python", "SQL", "C++"],
            0,
        ),
    ),
)

# Mantém os nomes antigos disponíveis para qualquer importação externa.
PERGUNTAS_FINAIS = [desafio.pergunta for desafio in DESAFIOS_FINAIS]
APRESENTADORES = [
    (desafio.cor, desafio.imagem, desafio.altura_imagem)
    for desafio in DESAFIOS_FINAIS
]
