"""Configurações e reprodução da trilha e dos efeitos do jogo."""

import pygame


# Reduz a latência entre o comando do jogador e o início dos efeitos.
# Este módulo é importado antes de pygame.init(), então o mixer já começa
# usando um buffer curto.
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=256)


RAIZ_PROJETO = __file__.replace("\\", "/").rsplit("/", 2)[0]
PASTA_MUSICAS = RAIZ_PROJETO + "/musica"
NOME_MUSICA = "SNCT2026JOGO.mp3"
CAMINHO_MUSICA = PASTA_MUSICAS + "/" + NOME_MUSICA
VOLUME_MUSICA = 0.2
REPETICOES = -1  # -1 mantém a música tocando em loop.

ARQUIVOS_EFEITOS = {
    "pulo": "Pulo8bit.mp3",
    "passos": "Passos-areia.mp3",
    "perda": "New Project - Perda.mp3",
    "lupa": "New Project - LUPA.mp3",
    "checkpoint": "New Project - Checkpoint.mp3",
}
VOLUMES_EFEITOS = {
    "pulo": 1.00,
    "passos": 0.80,
    "perda": 0.25,
    "lupa": 0.70,
    "checkpoint": 0.30,
}

_efeitos = {}
_efeitos_indisponiveis = set()
_canal_passos = None
_quadro_anterior_passos = None

# A corrida possui 16 sprites. Estes são os dois quadros em que um pé toca o
# chão, um para cada metade do ciclo.
QUADROS_PISADA = frozenset((0, 8))


def _dados_pcm(efeito):
    """Obtém os bytes PCM quando o mixer está no formato de 16 bits."""
    frequencia, tamanho_amostra, canais = pygame.mixer.get_init()
    if abs(tamanho_amostra) != 16:
        return None
    return efeito.get_raw(), frequencia, canais


def _ler_amostra(dados, posicao):
    """Lê uma amostra PCM assinada sem bibliotecas adicionais."""
    return int.from_bytes(
        dados[posicao:posicao + 2],
        byteorder="little",
        signed=True,
    )


def _gravar_amostra(dados, posicao, valor):
    """Grava uma amostra PCM de 16 bits, respeitando seus limites."""
    valor = max(-32768, min(32767, round(valor)))
    dados[posicao:posicao + 2] = valor.to_bytes(
        2,
        byteorder="little",
        signed=True,
    )


def _recortar(efeito, inicio_segundos, fim_segundos):
    """Mantém somente o intervalo solicitado do arquivo de passos."""
    resultado = _dados_pcm(efeito)
    if resultado is None:
        return efeito

    dados, frequencia, canais = resultado
    bytes_por_quadro = canais * 2
    inicio = int(inicio_segundos * frequencia) * bytes_por_quadro
    fim = int(fim_segundos * frequencia) * bytes_por_quadro
    trecho = dados[inicio:min(fim, len(dados))]
    if not trecho:
        return efeito
    return pygame.mixer.Sound(buffer=trecho)


def _remover_silencio_inicial(efeito):
    """Inicia o pulo no primeiro trecho realmente audível."""
    resultado = _dados_pcm(efeito)
    if resultado is None:
        return efeito

    dados, frequencia, canais = resultado
    bytes_por_quadro = canais * 2
    primeiro_quadro = None
    for posicao in range(0, len(dados) - 1, bytes_por_quadro):
        for canal in range(canais):
            amostra = _ler_amostra(dados, posicao + canal * 2)
            if abs(amostra) >= 500:
                primeiro_quadro = posicao // bytes_por_quadro
                break
        if primeiro_quadro is not None:
            break

    if primeiro_quadro is None:
        return efeito

    margem = frequencia * 2 // 1000
    inicio = max(0, primeiro_quadro - margem) * bytes_por_quadro
    if inicio == 0:
        return efeito
    return pygame.mixer.Sound(buffer=dados[inicio:])


def _limpar_ruido_passos(efeito, corte_graves=190):
    """Reduz o rumor semelhante a vento sem afetar o ataque dos passos."""
    resultado = _dados_pcm(efeito)
    if resultado is None:
        return efeito

    dados_originais, frequencia, canais = resultado
    dados = bytearray(dados_originais)
    alpha = 1.0 / (
        1.0 + 2.0 * 3.141592653589793 * corte_graves / frequencia
    )
    entradas_anteriores = [0.0] * canais
    saidas_anteriores = [0.0] * canais
    limiar_ruido = 260

    for posicao in range(0, len(dados) - 1, 2):
        canal = (posicao // 2) % canais
        entrada = _ler_amostra(dados_originais, posicao)
        saida = alpha * (
            saidas_anteriores[canal]
            + entrada
            - entradas_anteriores[canal]
        )
        entradas_anteriores[canal] = entrada
        saidas_anteriores[canal] = saida

        intensidade = abs(saida)
        if intensidade < limiar_ruido:
            saida *= intensidade / limiar_ruido
        _gravar_amostra(dados, posicao, saida)

    return pygame.mixer.Sound(buffer=bytes(dados))


def _amplificar(efeito, ganho):
    """Aumenta o volume das amostras sem ultrapassar o limite PCM."""
    resultado = _dados_pcm(efeito)
    if resultado is None:
        return efeito

    dados_originais, _, _ = resultado
    dados = bytearray(dados_originais)
    for posicao in range(0, len(dados) - 1, 2):
        valor = _ler_amostra(dados_originais, posicao)
        _gravar_amostra(dados, posicao, valor * ganho)
    return pygame.mixer.Sound(buffer=bytes(dados))


def _preparar_mixer():
    """Inicializa o áudio somente quando alguma faixa for solicitada."""
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    # O canal zero fica exclusivo para o loop de passos.
    pygame.mixer.set_reserved(1)


def _carregar_efeito(nome):
    """Carrega e guarda um efeito para que cada evento não releia o disco."""
    if nome in _efeitos:
        return _efeitos[nome]
    if nome in _efeitos_indisponiveis:
        return None

    arquivo = ARQUIVOS_EFEITOS.get(nome)
    if arquivo is None:
        raise ValueError(f"Efeito de áudio desconhecido: {nome!r}")

    try:
        _preparar_mixer()
        efeito = pygame.mixer.Sound(PASTA_MUSICAS + "/" + arquivo)
        if nome == "pulo":
            efeito = _remover_silencio_inicial(efeito)
        elif nome == "passos":
            efeito = _recortar(efeito, 4.0, 8.0)
            efeito = _limpar_ruido_passos(efeito)
            efeito = _amplificar(efeito, 4.0)
        efeito.set_volume(VOLUMES_EFEITOS[nome])
    except (OSError, pygame.error) as erro:
        # Um efeito ausente ou sem codec não impede a partida de continuar.
        print(f"Não foi possível carregar o efeito {arquivo}: {erro}")
        _efeitos_indisponiveis.add(nome)
        return None

    _efeitos[nome] = efeito
    return efeito


def iniciar_musica():
    """Carrega a faixa local configurada e inicia sua reprodução."""
    try:
        _preparar_mixer()
        pygame.mixer.music.load(CAMINHO_MUSICA)
        pygame.mixer.music.set_volume(VOLUME_MUSICA)
        pygame.mixer.music.play(REPETICOES)
        # Decodifica os efeitos antes da partida para o primeiro pulo não
        # esperar a leitura do arquivo.
        for nome_efeito in ARQUIVOS_EFEITOS:
            _carregar_efeito(nome_efeito)
    except (OSError, pygame.error) as erro:
        # O jogo continua funcionando mesmo em computadores sem saída de áudio.
        print(f"Não foi possível iniciar a música: {erro}")
        return False

    return True


def reproduzir_efeito(nome):
    """Toca uma vez o efeito associado ao evento informado."""
    efeito = _carregar_efeito(nome)
    if efeito is None:
        return False
    efeito.play()
    return True


def atualizar_passos(ativo, quadro_atual=None):
    """Dispara cada pisada no sprite correspondente da corrida."""
    global _canal_passos, _quadro_anterior_passos

    efeito = _carregar_efeito("passos") if ativo else _efeitos.get("passos")
    if efeito is None:
        return

    if _canal_passos is None:
        _canal_passos = pygame.mixer.Channel(0)
    if not ativo:
        if _canal_passos.get_busy():
            _canal_passos.stop()
        _quadro_anterior_passos = None
        return

    mudou_de_quadro = quadro_atual != _quadro_anterior_passos
    if mudou_de_quadro and quadro_atual in QUADROS_PISADA:
        _canal_passos.play(efeito)
    _quadro_anterior_passos = quadro_atual


def parar_passos():
    """Interrompe os passos antes de telas e sequências sem controle."""
    global _quadro_anterior_passos
    if _canal_passos is not None:
        _canal_passos.stop()
    _quadro_anterior_passos = None


def parar_musica():
    """Interrompe a música caso o sistema de áudio esteja disponível."""
    if pygame.mixer.get_init():
        parar_passos()
        pygame.mixer.stop()
        pygame.mixer.music.stop()
