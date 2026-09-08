import pygame

from configuracoes_musica import reproduzir_efeito
from recursos import carregar_imagem


# Arquivo principal, já transparente, com a personagem parada nas pontas e
# os quadros de corrida entre elas.
ARQUIVO_SPRITES = "personagem.png"
# Arquivo separado com os quadros usados durante o pulo.
ARQUIVO_SPRITES_PULO = "PERSONAGEM PULANDO.png"
# Quantidade total de quadros de corrida nas duas linhas da spritesheet, sem a pose parada.
TOTAL_QUADROS_CORRIDA = 16
# A pose parada aparece no início e se repete no fim da nova spritesheet.
TOTAL_POSES = TOTAL_QUADROS_CORRIDA + 2
# Quantidade de quadros da animação de pulo.
TOTAL_QUADROS_PULO = 7
# Tempo mínimo, em milissegundos, entre dois quadros da corrida.
INTERVALO_ANIMACAO_MS = 100
# Componentes menores que este tamanho são ignorados ao localizar sprites.
TAMANHO_MINIMO_COMPONENTE = 100
# Tolerância usada para identificar pixels quase brancos do fundo.
LIMIAR_FUNDO_CLARO = 36
# Ignora resíduos quase transparentes ao medir cada sprite.
LIMIAR_ALPHA_SPRITE = 128
# Folga usada para recuperar braços, cabelo e pés que ultrapassam a divisão
# visual entre duas células da spritesheet.
MARGEM_RECORTE_SPRITE = 32
# Quanto da personagem ainda fica visível ao começar a entrar em um buraco.
MARGEM_VISIVEL_NO_BURACO = 14
# Espaço lateral extra usado para evitar que a pose mude de posição visualmente.
MARGEM_ESTABILIZACAO_HORIZONTAL = 4
# Parte superior do corpo usada como referência para estabilizar cada pose.
PROPORCAO_CORPO_SUPERIOR = 0.65


class Personagem:
    """Personagem jogável com movimento, física e animação."""

    # O cache evita processar a spritesheet de pulo repetidamente para o mesmo tamanho.
    _quadros_pulo_por_tamanho = {}

    def __init__(self, x, y, largura=50, altura=80):
        # Guarda o tamanho visual solicitado para desenhar a personagem.
        self.largura_visual = largura
        self.altura_visual = altura

        # A hitbox ignora chapéu, cabelo e braços, mas termina nos pés.
        # Isso deixa colisões mais fiéis ao corpo do que usar a imagem inteira.
        largura_hitbox = max(1, round(largura * 0.56))
        altura_hitbox = max(1, round(altura * 0.88))
        # Calcula quanto a hitbox precisa ser deslocada para ficar centralizada.
        self.margem_hitbox_x = (largura - largura_hitbox) // 2
        # Cria o retângulo usado nas colisões e posiciona sua base nos pés.
        self.rect = pygame.Rect(
            x + self.margem_hitbox_x,
            y + altura - altura_hitbox,
            largura_hitbox,
            altura_hitbox,
        )

        # Velocidade horizontal em pixels por quadro.
        self.velocidade = 5
        # Velocidade vertical atual; valores negativos representam subida.
        self.velocidade_y = 0
        # Impulso aplicado quando o pulo começa.
        self.forca_pulo = -14
        # Aceleração vertical aplicada a cada atualização.
        self.gravidade = 0.6
        # Indica se a personagem está apoiada no chão.
        self.no_chao = False
        # Armazena o estado anterior da tecla de pulo para detectar um novo toque.
        self._pulo_pressionado = False
        # Permite que o áudio reconheça exatamente o quadro em que o pulo começou.
        self.pulo_iniciado_no_quadro = False

        # Depois de entrar em um buraco, não pode pousar na outra borda
        # durante a mesma queda. O estado é limpo ao reposicionar.
        # Indica que a queda atual começou sobre um buraco.
        self.caindo_no_buraco = False
        # Controla quando a personagem deixa de ser desenhada durante a queda.
        self.oculto_no_buraco = False

        # Carrega e prepara as poses da personagem para o tamanho solicitado.
        poses = self._carregar_quadros(largura, altura)
        # A primeira pose é usada quando a personagem está parada olhando para a direita.
        self.quadro_parado_direita = poses[0]
        # Espelha horizontalmente a pose parada para olhar para a esquerda.
        self.quadro_parado_esquerda = pygame.transform.flip(
            poses[0], True, False
        )
        # As demais poses formam a animação de corrida para a direita.
        self.quadros_direita = poses[1:]
        # Cria a mesma animação espelhada para a esquerda.
        self.quadros_esquerda = [
            pygame.transform.flip(quadro, True, False)
            for quadro in self.quadros_direita
        ]
        # Carrega os quadros específicos usados enquanto a personagem está no ar.
        self.quadros_pulo_direita = self._carregar_quadros_pulo(
            largura,
            altura,
        )
        # Cria a versão virada para a esquerda de cada quadro de pulo.
        self.quadros_pulo_esquerda = tuple(
            pygame.transform.flip(quadro, True, False)
            for quadro in self.quadros_pulo_direita
        )
        # Índice do quadro atual da animação de corrida.
        self.indice_quadro = 0
        # Momento em que o último quadro de corrida foi selecionado.
        self.ultimo_quadro = pygame.time.get_ticks()
        # Indica se houve movimento horizontal no último ciclo.
        self.em_movimento = False
        # Guarda a direção visual atual da personagem.
        self.virado_para_esquerda = False

    def _localizar_quadros(self, sprites):
        """Localiza uma célula aproximada para cada pose da spritesheet."""
        largura_total, altura_total = sprites.get_size()
        mascara = pygame.mask.from_surface(
            sprites,
            threshold=LIMIAR_ALPHA_SPRITE,
        )
        largura_media = largura_total // TOTAL_POSES
        raio_busca = max(4, largura_media // 3)
        separadores = [0]

        for indice in range(1, TOTAL_POSES):
            esperado = indice * largura_total // TOTAL_POSES
            inicio_busca = max(separadores[-1] + 1, esperado - raio_busca)
            fim_busca = min(largura_total - 1, esperado + raio_busca)

            def avaliar_coluna(x):
                pixels = sum(
                    mascara.get_at((x, y))
                    for y in range(altura_total)
                )
                return pixels, abs(x - esperado)

            separador = min(
                range(inicio_busca, fim_busca + 1),
                key=avaliar_coluna,
            )
            separadores.append(separador)

        separadores.append(largura_total)
        limites = []

        for indice in range(TOTAL_POSES):
            inicio_x = separadores[indice]
            fim_x = separadores[indice + 1]
            celula = sprites.subsurface(
                (inicio_x, 0, fim_x - inicio_x, altura_total),
            )
            area_visivel = celula.get_bounding_rect(LIMIAR_ALPHA_SPRITE)
            if not area_visivel.width or not area_visivel.height:
                raise ValueError(
                    f"A célula {indice + 1} da personagem está vazia"
                )
            area_visivel.move_ip(inicio_x, 0)
            limites.append(area_visivel)

        return limites

    def _calcular_escala(self, limites, largura, altura):
        """Usa os mesmos parâmetros de tamanho para corrida e pulo."""
        largura_base = max(area.width for area in limites)
        altura_base = max(area.height for area in limites)
        return min(largura / largura_base, altura / altura_base)

    def _isolar_personagem(self, quadro):
        """Mantém a pose central e descarta pedaços das poses vizinhas."""
        mascara = pygame.mask.from_surface(
            quadro,
            threshold=LIMIAR_ALPHA_SPRITE,
        )
        componentes = mascara.connected_components()
        if not componentes:
            return quadro

        personagem = max(componentes, key=lambda item: item.count())
        mascara_personagem = personagem.to_surface(
            setcolor=(255, 255, 255, 255),
            unsetcolor=(255, 255, 255, 0),
        )
        isolado = quadro.copy()
        isolado.blit(
            mascara_personagem,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT,
        )
        area_visivel = isolado.get_bounding_rect(1)
        if area_visivel.width and area_visivel.height:
            return isolado.subsurface(area_visivel).copy()
        return isolado

    def _extrair_quadros_corrida(self, sprites):
        """Recupera cada pose inteira, mesmo quando ela invade a célula vizinha."""
        limites = self._localizar_quadros(sprites)
        area_sprites = sprites.get_rect()
        quadros = []

        for area in limites:
            area_com_folga = area.inflate(MARGEM_RECORTE_SPRITE * 2, 0)
            area_com_folga.clamp_ip(area_sprites)
            quadro = sprites.subsurface(area_com_folga).copy()
            quadros.append(self._isolar_personagem(quadro))

        return quadros

    def _carregar_quadros(self, largura, altura):
        # Carrega a imagem que contém a pose parada e os quadros de corrida.
        sprites = carregar_imagem(ARQUIVO_SPRITES)
        # Descobre automaticamente onde cada pose está localizada e recupera
        # as partes que avançam para a célula vizinha.
        quadros_base = self._extrair_quadros_corrida(sprites)
        # Falha cedo caso a spritesheet tenha sido alterada ou esteja incompleta.
        if len(quadros_base) != TOTAL_POSES:
            raise ValueError(
                f"Esperadas {TOTAL_POSES} poses da personagem; "
                f"encontrados {len(quadros_base)}"
            )

        # Usa o maior quadro como referência para manter todas as poses proporcionais.
        escala = self._calcular_escala(
            [quadro.get_rect() for quadro in quadros_base],
            largura,
            altura,
        )
        # Recorta, redimensiona e alinha cada pose em um canvas de tamanho comum.
        poses = [
            self._preparar_quadro(
                quadro,
                quadro.get_rect(),
                largura,
                altura,
                escala,
            )
            for quadro in quadros_base
        ]
        # A última pose é uma repetição da primeira e serve apenas para fechar
        # visualmente a sequência na imagem; a animação usa os 16 quadros entre
        # as duas poses paradas.
        return poses[:-1]

    def _remover_fundo_claro(self, sprites):
        """Remove apenas o fundo claro conectado às bordas da spritesheet."""
        # Garante que a imagem aceite transparência alfa.
        sprites = sprites.convert_alpha()
        # Seleciona pixels brancos ou quase brancos que podem ser fundo.
        candidatos = pygame.mask.from_threshold(
            sprites,
            (255, 255, 255, 255),
            (
                LIMIAR_FUNDO_CLARO,
                LIMIAR_FUNDO_CLARO,
                LIMIAR_FUNDO_CLARO,
                255,
            ),
        )
        # Máscara que receberá somente as regiões de fundo conectadas às bordas.
        fundo = pygame.Mask(sprites.get_size())
        largura, altura = sprites.get_size()

        # Analisa cada área branca separadamente para não remover detalhes internos.
        for componente in candidatos.connected_components():
            limites = componente.get_bounding_rects()
            if not limites:
                continue
            area = limites[0]
            # Uma região que toca uma borda é considerada parte do fundo externo.
            toca_borda = (
                area.left == 0
                or area.top == 0
                or area.right == largura
                or area.bottom == altura
            )
            if toca_borda:
                # Marca essa região para ser tornada transparente.
                fundo.draw(componente, (0, 0))

        # Converte a máscara em uma superfície alfa: fundo transparente, demais pixels opacos.
        mascara_alpha = fundo.to_surface(
            setcolor=(255, 255, 255, 0),
            unsetcolor=(255, 255, 255, 255),
        )
        # Copia a imagem original para preservar o arquivo carregado.
        transparente = sprites.copy()
        # Aplica a transparência somente onde a máscara marcou o fundo.
        transparente.blit(
            mascara_alpha,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT,
        )
        return transparente

    def _carregar_quadros_pulo(self, largura, altura):
        """Extrai e reutiliza os sete quadros da animação de pulo."""
        # O tamanho faz parte da chave porque imagens redimensionadas não são intercambiáveis.
        chave = (largura, altura)
        if chave in self._quadros_pulo_por_tamanho:
            # Retorna o resultado pronto quando outro personagem usa o mesmo tamanho.
            return self._quadros_pulo_por_tamanho[chave]

        # Carrega a spritesheet do pulo e remove o fundo claro externo.
        sprites = self._remover_fundo_claro(
            carregar_imagem(ARQUIVO_SPRITES_PULO),
        )
        # Localiza os pixels visíveis de cada quadro.
        mascara = pygame.mask.from_surface(sprites, threshold=1)
        # Ordena os quadros pela posição horizontal na spritesheet.
        limites = sorted(
            (
                componente.get_bounding_rects()[0]
                for componente in mascara.connected_components(
                    TAMANHO_MINIMO_COMPONENTE,
                )
            ),
            key=lambda area: area.x,
        )
        # Confirma que a spritesheet contém exatamente a animação esperada.
        if len(limites) != TOTAL_QUADROS_PULO:
            raise ValueError(
                f"Esperados {TOTAL_QUADROS_PULO} quadros de pulo; "
                f"encontrados {len(limites)}"
            )

        # Calcula uma escala comum para todos os quadros de pulo.
        escala = self._calcular_escala(
            limites,
            largura,
            altura,
        )
        # Prepara cada quadro no mesmo tamanho e alinhamento visual.
        quadros = tuple(
            self._preparar_quadro(
                sprites,
                area,
                largura,
                altura,
                escala,
            )
            for area in limites
        )
        # Guarda o resultado para reutilização por outros objetos do mesmo tamanho.
        self._quadros_pulo_por_tamanho[chave] = quadros
        return quadros

    def _preparar_quadro(
        self,
        sprites,
        area,
        largura,
        altura,
        escala,
    ):
        """Redimensiona e estabiliza uma pose em um canvas comum."""
        # Recorta somente a área ocupada pela pose atual.
        quadro = sprites.subsurface(area).copy()
        # Calcula o tamanho final sem permitir dimensões menores que um pixel.
        tamanho = (
            max(1, round(area.width * escala)),
            max(1, round(area.height * escala)),
        )
        # Redimensiona com suavização para melhorar a qualidade visual.
        quadro = pygame.transform.smoothscale(quadro, tamanho)

        # Adiciona margem lateral para permitir pequenos ajustes de alinhamento.
        largura_canvas = largura + MARGEM_ESTABILIZACAO_HORIZONTAL * 2
        alinhado = pygame.Surface(
            (largura_canvas, altura),
            pygame.SRCALPHA,
        )
        # Posiciona o quadro com a base alinhada à parte inferior do canvas.
        alinhado.blit(
            quadro,
            ((largura_canvas - tamanho[0]) // 2, altura - tamanho[1]),
        )

        # As pernas mudam bastante a largura de cada pose. Usar cabeça e
        # tronco como âncora evita que esse movimento desloque o corpo inteiro.
        # Define a altura da região superior que servirá como âncora.
        altura_corpo_superior = round(altura * PROPORCAO_CORPO_SUPERIOR)
        # Recorta a parte superior do canvas, ignorando as pernas.
        corpo_superior = alinhado.subsurface(
            (0, 0, largura_canvas, altura_corpo_superior),
        )
        # Encontra o centro horizontal dos pixels visíveis dessa região.
        centro_visual_x = pygame.mask.from_surface(
            corpo_superior,
        ).centroid()[0]
        # Calcula quanto o quadro deve ser deslocado para centralizar o tronco.
        deslocamento_x = largura_canvas // 2 - centro_visual_x
        if deslocamento_x:
            # Usa uma nova superfície para aplicar o deslocamento sem cortar a pose original.
            estabilizado = pygame.Surface(
                alinhado.get_size(),
                pygame.SRCALPHA,
            )
            estabilizado.blit(alinhado, (deslocamento_x, 0))
            alinhado = estabilizado

        return alinhado

    def _direcao_horizontal(self, teclas):
        # Verifica simultaneamente as teclas alternativas de esquerda e direita.
        esquerda = teclas[pygame.K_a] or teclas[pygame.K_LEFT]
        direita = teclas[pygame.K_d] or teclas[pygame.K_RIGHT]
        # Retorna -1 para esquerda, 1 para direita e 0 quando não há direção.
        return int(direita) - int(esquerda)

    def esta_caminhando(self):
        """Indica se a animação e o som de passos devem permanecer ativos."""
        return (
            self.em_movimento
            and self.no_chao
            and not self.caindo_no_buraco
        )

    def mover(self):
        """Lê as teclas horizontais e desloca a hitbox."""
        # Obtém o estado atual do teclado e calcula a direção horizontal.
        direcao = self._direcao_horizontal(pygame.key.get_pressed())
        # Move a hitbox de acordo com a direção e a velocidade configurada.
        self.rect.x += direcao * self.velocidade
        # Registra se a personagem está se deslocando neste quadro.
        self.em_movimento = direcao != 0
        if self.em_movimento:
            # Atualiza a orientação apenas quando existe movimento.
            self.virado_para_esquerda = direcao < 0
        else:
            # Ao soltar as teclas, retorna exatamente ao primeiro sprite da
            # folha: parado e voltado para a direita.
            self.indice_quadro = 0
            self.virado_para_esquerda = False
            self.ultimo_quadro = pygame.time.get_ticks()

    def pular(self):
        """Inicia o pulo somente quando a personagem está apoiada."""
        self.pulo_iniciado_no_quadro = False
        # Lê as duas teclas aceitas para iniciar o pulo.
        teclas = pygame.key.get_pressed()
        pediu_pulo = teclas[pygame.K_w] or teclas[pygame.K_UP]
        # Detecta a transição de tecla solta para tecla pressionada.
        novo_toque = pediu_pulo and not self._pulo_pressionado
        # Guarda o estado atual para a próxima chamada.
        self._pulo_pressionado = pediu_pulo
        if novo_toque and self.no_chao:
            # Aplica o impulso vertical e marca que a personagem deixou o chão.
            self.velocidade_y = self.forca_pulo
            self.no_chao = False
            self.pulo_iniciado_no_quadro = True

    def posicionar_no_chao(self, x_visual, y_chao):
        """Restaura posição e estado físico em um ponto seguro."""
        # Converte a posição visual recebida para a posição real da hitbox.
        self.rect.left = x_visual + self.margem_hitbox_x
        # Encosta os pés exatamente na altura do chão indicada.
        self.rect.bottom = y_chao
        # Cancela qualquer velocidade vertical pendente.
        self.velocidade_y = 0
        # Marca a personagem como apoiada novamente.
        self.no_chao = True
        # Limpa o estado especial de queda no buraco.
        self.caindo_no_buraco = False
        self.oculto_no_buraco = False
        # Uma reposição sempre começa com a pose parada, sem reaproveitar o
        # último quadro da caminhada anterior.
        self.em_movimento = False
        self.indice_quadro = 0
        self.virado_para_esquerda = False
        self.ultimo_quadro = pygame.time.get_ticks()

    def rebater(self, intensidade=0.55):
        """Impulsiona a personagem após cair sobre um inimigo."""
        # Usa parte da força normal do pulo para lançar a personagem para cima.
        self.velocidade_y = self.forca_pulo * intensidade
        # O rebote também faz a personagem deixar de estar no chão.
        self.no_chao = False

    def caminhar_automaticamente(self, direcao):
        """Move sem ler o teclado, usado em sequências controladas."""
        # Desloca a hitbox na direção fornecida por uma sequência automática.
        self.rect.x += direcao * self.velocidade
        # Mantém a animação de caminhada ativa durante o movimento automático.
        self.em_movimento = True
        # Atualiza a direção visual conforme o sinal recebido.
        self.virado_para_esquerda = direcao < 0
        # Avança a animação imediatamente após mover.
        self.atualizar_animacao()

    def aplicar_gravidade(self, y_chao, ignorar_chao=False):
        """Aplica a queda e resolve o contato com o piso da fase."""
        # Aumenta gradualmente a velocidade vertical para simular gravidade.
        self.velocidade_y += self.gravidade
        # Move a hitbox verticalmente usando a velocidade atual.
        y_anterior = self.rect.y
        self.rect.y += int(self.velocidade_y)
        if self.pulo_iniciado_no_quadro and self.rect.y < y_anterior:
            # Dispara no exato primeiro deslocamento para cima, sem esperar
            # que o restante da atualização do quadro seja concluído.
            reproduzir_efeito("pulo")

        if self.rect.bottom >= y_chao and not ignorar_chao:
            # Impede que a personagem atravesse o chão e zera a queda.
            self.rect.bottom = y_chao
            self.velocidade_y = 0
            self.no_chao = True

    def atualizar(self, y_chao, verificar_buraco=None):
        """Atualiza entrada, física e animação por um quadro."""
        # Processa o movimento controlado pelo jogador.
        self.mover()
        # Consulta opcionalmente o cenário para saber se a hitbox está sobre um buraco.
        sobre_buraco = bool(verificar_buraco and verificar_buraco(self))

        if sobre_buraco:
            # Um buraco impede o pouso normal no chão.
            self.no_chao = False
            if self.rect.bottom >= y_chao:
                # Marca o começo da queda para impedir pouso na borda oposta.
                self.caindo_no_buraco = True

        # Processa um novo comando de pulo depois de ler o movimento.
        self.pular()
        # Aplica gravidade, ignorando o chão enquanto estiver sobre ou dentro do buraco.
        self.aplicar_gravidade(
            y_chao,
            ignorar_chao=sobre_buraco or self.caindo_no_buraco,
        )
        # Calcula o topo visual atual com base na base da hitbox.
        topo_visual = self.rect.bottom - self.altura_visual
        # Esconde a personagem somente depois que ela passou da margem visível do buraco.
        self.oculto_no_buraco = (
            self.caindo_no_buraco
            and topo_visual >= y_chao + MARGEM_VISIVEL_NO_BURACO
        )
        self.atualizar_animacao()

    def atualizar_animacao(self):
        """Avança a caminhada em intervalos constantes."""
        if not self.em_movimento:
            # Ao parar, volta imediatamente à pose inicial e reinicia o relógio.
            self.indice_quadro = 0
            self.ultimo_quadro = pygame.time.get_ticks()
            return

        # Obtém o horário atual para medir o intervalo desde o último quadro.
        agora = pygame.time.get_ticks()
        tempo_decorrido = agora - self.ultimo_quadro
        # Calcula quantos quadros deveriam ter passado nesse intervalo.
        quadros_decorridos = tempo_decorrido // INTERVALO_ANIMACAO_MS
        if quadros_decorridos:
            # Avança em ciclos para que a animação continue repetindo.
            self.indice_quadro = (
                self.indice_quadro + quadros_decorridos
            ) % len(self.quadros_direita)
            # Mantém o restante do tempo acumulado para não acelerar a animação.
            self.ultimo_quadro += quadros_decorridos * INTERVALO_ANIMACAO_MS

    def desenhar(self, tela, camera_x=0):
        """Desenha a pose atual alinhada aos pés da hitbox."""
        if self.oculto_no_buraco:
            # Não desenha a personagem quando ela já caiu além da área visível.
            return

        if not self.no_chao:
            # Escolhe a animação de pulo de acordo com a direção visual.
            quadros = (
                self.quadros_pulo_esquerda
                if self.virado_para_esquerda
                else self.quadros_pulo_direita
            )
            # Converte a velocidade vertical em uma posição entre o primeiro e o último quadro.
            amplitude = abs(self.forca_pulo) * 2
            progresso = (self.velocidade_y - self.forca_pulo) / amplitude
            # Limita o progresso para evitar índices fora da animação.
            progresso = max(0.0, min(1.0, progresso))
            # Escolhe o quadro de pulo proporcional à subida ou descida.
            indice = round(progresso * (len(quadros) - 1))
            quadro = quadros[indice]
        elif not self.em_movimento:
            # Quando está parada, escolhe a pose parada na direção atual.
            quadro = (
                self.quadro_parado_esquerda
                if self.virado_para_esquerda
                else self.quadro_parado_direita
            )
        else:
            # Quando corre, escolhe a sequência correspondente à direção.
            quadros = (
                self.quadros_esquerda
                if self.virado_para_esquerda
                else self.quadros_direita
            )
            # Usa o índice atualizado pela rotina de animação.
            quadro = quadros[self.indice_quadro]
        # Converte a posição da hitbox em uma posição visual corrigida pela câmera.
        destino = quadro.get_rect(
            midbottom=(self.rect.centerx - int(camera_x), self.rect.bottom)
        )
        # Copia o quadro selecionado para a tela.
        tela.blit(quadro, destino)
