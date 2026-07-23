class HanoiTower:
    """
    Resolve o problema da Torre de Hanoi.
    """
    def __init__(self, num_discos: int):
        # Define as hastes padrao
        self.origem = 'A'
        self.destino = 'C'
        self.auxiliar = 'B'
        self.num_discos = num_discos

    def solve(self, n: int) -> list[tuple[str, str]]:
        """
        Inicia a solução da Torre de Hanoi e retorna a sequência de movimentos.
        n é o número de discos.
        """
        if n == 0:
            return []

        result = []
        # Inicia a recursão com as hastes padrão
        self._hanoi_recursivo(n, self.origem, self.destino, self.auxiliar, result)
        return result

    def _hanoi_recursivo(self, n: int, origem: str, destino: str, auxiliar: str, moves: list[tuple[str, str]]):
        """
        Implementa a lógica recursiva da Torre de Hanoi.
        Adiciona os movimentos à lista 'moves'.
        """
        # Caso Base: Se não houver discos a mover
        if n == 0:
            return

        # Passo Recursivo 1: Mover n-1 discos da Origem para o Auxiliar, usando o Destino como temporário
        self._hanoi_recursivo(n - 1, origem, auxiliar, destino, moves)

        # Movimento Atual: Mover o maior disco (n) da Origem para o Destino
        moves.append((origem, destino))

        # Passo Recursivo 2: Mover n-1 discos do Auxiliar para o Destino, usando a Origem como temporário
        self._hanoi_recursivo(n - 1, auxiliar, destino, origem, moves)

# Adicionando um método solve ajustado para o formato esperado pelos testes, que usa as configurações internas.
# Como os testes esperam chamar solve(N) e a classe tem o estado fixo A, C, B, vamos ajustar a implementação do solve para refletir a lógica necessária.
# Revisando os testes: Os testes chamam hanoi.solve(N) e esperam uma lista de tuplas representando o movimento.

class HanoiTowerCorrected:
    """Versão corrigida para atender ao formato exato dos testes."""
    def __init__(self, num_discos: int):
        self.num_discos = num_discos
        # Hastes fixas conforme o design (A=Origem, C=Destino, B=Auxiliar)
        self.origem = 'A'
        self.destino = 'C'
        self.auxiliar = 'B'

    def solve(self, n: int) -> list[tuple[str, str]]:
        """
        Executa a lógica recursiva para gerar a sequência de movimentos.
        """
        if n == 0:
            return []

        moves = []
        # Inicia a recursão principal
        self._hanoi_recursivo(n, self.origem, self.destino, self.auxiliar, moves)
        return moves

    def _hanoi_recursivo(self, n: int, origem: str, destino: str, auxiliar: str, moves: list[tuple[str, str]]):
        """
        Método recursivo para gerar os movimentos.
        """
        if n == 0:
            return

        # Move n-1 discos da Origem para o Auxiliar usando o Destino como auxílio
        self._hanoi_recursivo(n - 1, origem, auxiliar, destino, moves)

        # Move o disco n da Origem para o Destino
        moves.append((origem, destino))

        # Move n-1 discos do Auxiliar para o Destino usando a Origem como auxílio
        self._hanoi_recursivo(n - 1, auxiliar, destino, origem, moves)

# Para que os testes funcionem com a classe nomeada 'HanoiTower', farei uma pequena adaptação para garantir compatibilidade de nomes.
# O teste espera um objeto com o método solve e ele deve operar sobre A, B, C como as hastes.
# Vamos refatorar para usar o nome da classe esperado pelo teste implicitamente.

class HanoiTower:
    def __init__(self, num_discos: int):
        self.num_discos = num_discos
        self.origem = 'A'
        self.destino = 'C'
        self.auxiliar = 'B'

    def solve(self, n: int) -> list[tuple[str, str]]:
        if n == 0:
            return []
        
        moves = []
        self._hanoi_recursivo(n, self.origem, self.destino, self.auxiliar, moves)
        return moves

    def _hanoi_recursivo(self, n: int, origem: str, destino: str, auxiliar: str, moves: list[tuple[str, str]]):
        if n == 0:
            return

        # Recursão 1: Mover n-1 da Origem para o Auxiliar (usando Destino como auxílio)
        self._hanoi_recursivo(n - 1, origem, auxiliar, destino, moves)

        # Movimento do disco n: Origem -> Destino
        moves.append((origem, destino))

        # Recursão 2: Mover n-1 do Auxiliar para o Destino (usando Origem como auxílio)
        self._hanoi_recursivo(n - 1, auxiliar, destino, origem, moves)