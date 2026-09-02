# Joguinho SNCT

## Como executar

Na raiz do projeto, instale o Pygame e execute:

```powershell
python -m pip install pygame
python jogo/main.py
```

No Windows, caso o comando `python` não esteja disponível, tente usar `py` no
lugar dele. O jogo carrega as imagens da pasta `Imagens/` e a trilha sonora da
pasta `musica/` automaticamente.

## Organização do código

O projeto segue uma organização em peças pequenas, no estilo LEGO:

- `main.py`: coordena o laço principal;
- `estado_partida.py`: guarda pontuação, fase e transições;
- `fabrica_fase.py`: monta os elementos de cada fase;
- `personagem.py`, `inimigos.py`, `obstaculos.py` e `moedas.py`: regras das
  entidades;
- `tela_multipla_escolha.py`: componente reutilizável das perguntas;
- `recursos.py`: carregamento e cache de imagens;
- `menu.py`, `hud.py`, `avisos.py` e `tela_final.py`: componentes de interface.

Pastas `__pycache__` e arquivos `.pyc` são gerados automaticamente pelo
Python e não devem ser versionados.
