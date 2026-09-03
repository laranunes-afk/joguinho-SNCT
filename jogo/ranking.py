PASTA_JOGO = __file__.replace("\\", "/").rsplit("/", 1)[0]
ARQUIVO_RANKING = PASTA_JOGO + "/ranking.json"


class Ranking:
    """Le, valida, ordena e persiste o ranking local."""

    TEMPO_REFERENCIA = 10 * 60
    PONTOS_POR_LUPA = 100
    PONTOS_POR_SEGUNDO = 5
    LIMITE = 10
    TAMANHO_MAXIMO_NOME = 16

    def __init__(self, arquivo=ARQUIVO_RANKING):
        self.arquivo = str(arquivo)
        self.ultimo_resultado_entrou_no_top_10 = False

    @classmethod
    def calcular_pontos(cls, lupas, tempo):
        """Equilibra exploracao e velocidade em uma pontuacao unica."""
        bonus_tempo = max(0, cls.TEMPO_REFERENCIA - tempo)
        return lupas * cls.PONTOS_POR_LUPA + bonus_tempo * cls.PONTOS_POR_SEGUNDO

    @staticmethod
    def _chave(item):
        # Valores negativos permitem ordenar pontos e lupas do maior para o menor.
        return (
            -item["pontos"],
            -item["lupas"],
            item["tempo"],
            item["nome"].casefold(),
        )

    @classmethod
    def _normalizar_item(cls, item):
        """Valida uma entrada externa e devolve somente os campos aceitos."""
        if not isinstance(item, dict):
            return None

        nome = item.get("nome")
        tempo = item.get("tempo")
        lupas = item.get("lupas")
        contagens_validas = (
            isinstance(tempo, int)
            and not isinstance(tempo, bool)
            and tempo >= 0
            and isinstance(lupas, int)
            and not isinstance(lupas, bool)
            and lupas >= 0
        )
        if not isinstance(nome, str) or not contagens_validas:
            return None

        nome = nome.strip()[:cls.TAMANHO_MAXIMO_NOME] or "Anônimo"
        return {
            "nome": nome,
            "tempo": tempo,
            "lupas": lupas,
            "pontos": cls.calcular_pontos(lupas, tempo),
        }

    @staticmethod
    def _validar_contagem(valor, campo):
        if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
            raise ValueError(f"{campo} deve ser um inteiro não negativo")
        return valor

    def carregar(self):
        try:
            with open(self.arquivo, encoding="utf-8") as arquivo:
                linhas = arquivo.readlines()
        except (OSError, UnicodeError):
            return []

        itens = []
        item = None
        try:
            for linha in linhas:
                linha = linha.strip().rstrip(",")
                if linha == "{":
                    item = {}
                    continue
                if linha == "}":
                    if item is not None:
                        itens.append(item)
                    item = None
                    continue
                if item is None or ":" not in linha:
                    continue

                chave, valor = linha.split(":", 1)
                chave = chave.strip().strip('"')
                valor = valor.strip()
                if chave == "nome" and valor.startswith('"') and valor.endswith('"'):
                    item[chave] = valor[1:-1].replace('\\"', '"').replace(
                        "\\\\",
                        "\\",
                    )
                elif chave in {"tempo", "lupas", "pontos"}:
                    item[chave] = int(valor)
        except (TypeError, ValueError):
            return []

        validos = []
        for item in itens:
            normalizado = self._normalizar_item(item)
            if normalizado is not None:
                validos.append(normalizado)
        return sorted(validos, key=self._chave)[:self.LIMITE]

    def _gravar(self, itens):
        """Grava o ranking em JSON usando apenas recursos nativos da linguagem."""
        linhas = ["["]
        for indice, item in enumerate(itens):
            nome = item["nome"].replace("\\", "\\\\").replace('"', '\\"')
            linhas.extend(
                (
                    "  {",
                    f'    "nome": "{nome}",',
                    f'    "tempo": {item["tempo"]},',
                    f'    "lupas": {item["lupas"]},',
                    f'    "pontos": {item["pontos"]}',
                    "  }," if indice < len(itens) - 1 else "  }",
                )
            )
        linhas.append("]")
        with open(self.arquivo, "w", encoding="utf-8") as arquivo:
            arquivo.write("\n".join(linhas) + "\n")

    def salvar_resultado(self, itens, nome, tempo, lupas):
        if not isinstance(itens, (list, tuple)):
            raise ValueError("itens deve ser uma lista de resultados")
        if not isinstance(nome, str):
            raise ValueError("nome deve ser um texto")
        tempo = self._validar_contagem(tempo, "tempo")
        lupas = self._validar_contagem(lupas, "lupas")
        novo_resultado = {
            "nome": nome.strip()[:self.TAMANHO_MAXIMO_NOME] or "Anônimo",
            "tempo": tempo,
            "lupas": lupas,
            "pontos": self.calcular_pontos(lupas, tempo),
        }

        candidatos = []
        for item in itens:
            normalizado = self._normalizar_item(item)
            if normalizado is not None:
                candidatos.append(normalizado)
        candidatos.append(novo_resultado)
        candidatos.sort(key=self._chave)
        melhores = candidatos[:self.LIMITE]
        self.ultimo_resultado_entrou_no_top_10 = any(
            item is novo_resultado for item in melhores
        )
        self._gravar(melhores)
        return melhores
