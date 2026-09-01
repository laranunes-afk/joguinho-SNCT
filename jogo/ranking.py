import json
from pathlib import Path


ARQUIVO_RANKING = Path(__file__).with_name("ranking.json")


class Ranking:
    """Le, valida, ordena e persiste o ranking local."""

    TEMPO_REFERENCIA = 10 * 60
    PONTOS_POR_LUPA = 100
    PONTOS_POR_SEGUNDO = 5

    @classmethod
    def calcular_pontos(cls, lupas, tempo):
        """Equilibra exploracao e velocidade em uma pontuacao unica."""
        bonus_tempo = max(0, cls.TEMPO_REFERENCIA - tempo)
        return lupas * cls.PONTOS_POR_LUPA + bonus_tempo * cls.PONTOS_POR_SEGUNDO

    @staticmethod
    def _chave(item):
        return (
            -item["pontos"],
            -item["lupas"],
            item["tempo"],
            item["nome"].casefold(),
        )

    def carregar(self):
        try:
            with ARQUIVO_RANKING.open(encoding="utf-8") as arquivo:
                itens = json.load(arquivo)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        validos = [
            {
                **item,
                "pontos": self.calcular_pontos(item["lupas"], item["tempo"]),
            }
            for item in itens
            if isinstance(item, dict)
            and isinstance(item.get("nome"), str)
            and isinstance(item.get("tempo"), int)
            and isinstance(item.get("lupas"), int)
        ]
        return sorted(validos, key=self._chave)

    def salvar_resultado(self, itens, nome, tempo, lupas):
        itens.append(
            {
                "nome": nome.strip() or "Anônimo",
                "tempo": tempo,
                "lupas": lupas,
                "pontos": self.calcular_pontos(lupas, tempo),
            }
        )
        itens.sort(key=self._chave)
        melhores = itens[:10]
        with ARQUIVO_RANKING.open("w", encoding="utf-8") as arquivo:
            json.dump(melhores, arquivo, ensure_ascii=False, indent=2)
        return melhores
