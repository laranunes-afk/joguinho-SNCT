TIPOS_DE_PERGUNTA = {
    1: "CONHECIMENTOS GERAIS",
    2: "MATEMÁTICA",
    3: "CIÊNCIAS",
}

PERGUNTAS_POR_FASE = {
    1: [
        ("Qual é a capital do Brasil?", ["Brasília", "Salvador", "São Paulo", "Recife"], 0),
        ("Em qual continente fica o Brasil?", ["Europa", "Ásia", "América do Sul", "África"], 2),
        ("Quantos dias possui uma semana?", ["Cinco", "Seis", "Sete", "Oito"], 2),
        ("Qual idioma é falado oficialmente no Brasil?", ["Espanhol", "Português", "Inglês", "Francês"], 1),
    ],
    2: [
        ("Quanto é 7 x 8?", ["48", "54", "56", "64"], 2),
        ("Quanto é 100 dividido por 4?", ["20", "25", "30", "40"], 1),
        ("Quanto é 35 + 27?", ["52", "60", "62", "72"], 2),
        ("Quantos lados possui um hexágono?", ["Cinco", "Seis", "Sete", "Oito"], 1),
    ],
    3: [
        ("Qual é o maior planeta do Sistema Solar?", ["Terra", "Marte", "Saturno", "Júpiter"], 3),
        ("Qual destes animais é um mamífero?", ["Tubarão", "Golfinho", "Polvo", "Pinguim"], 1),
        ("Qual gás é essencial para a respiração humana?", ["Oxigênio", "Hélio", "Hidrogênio", "Neônio"], 0),
        ("A água congela normalmente a quantos graus Celsius?", ["0", "10", "50", "100"], 0),
    ],
}
