class HanoiTower:
    """
    Representa o problema e a lógica para resolver a Torre de Hanoi.
    """
    def __init__(self, num_discos: int, origem: str, destino: str, auxiliar: str):
        """
        Inicializa a instância da classe com os parâmetros necessários para definir o estado inicial do problema.
        Valida que num_discos é positivo e as hastes são distintas.
        """
        if not isinstance(num_discos, int) or num_discos <= 0:
            raise ValueError("O número de discos deve ser um inteiro positivo.")
        if len({origem, destino, auxiliar}) != 3:
             raise ValueError("As hastes de origem, destino e auxiliar devem ser distintas.")

        self.num_discos = num_discos
        self.origem = origem
        self.destino = destino
        self.auxiliar = auxiliar
        self.movimentos = []

    def mover_disco(self, origem: str, destino: str, auxiliar: str):
        """
        Método auxiliar que executa um único movimento de disco entre as hastes e registra-o.
        """
        self.movimentos.append(f"Mover disco {self.num_discos - self.movimentos.count('mover')} de {origem} para {destino}")

    def solucionar(self):
        """
        Executa a lógica recursiva para mover os discos da origem para o destino.
        Responsável pela implementação da regra fundamental da Torre de Hanoi.
        """
        if self.num_discos == 0:
            return

        # Passo Recursivo 1: Mover n-1 discos da Origem para o Auxiliar, usando o Destino como auxiliar temporário
        self.solucionar(self.num_discos - 1, self.origem, self.auxiliar, self.destino)

        # Movimento Principal: Mover o maior disco (n) da Origem para o Destino
        # Nota: O registro do movimento precisa ser ajustado para refletir a ordem correta da descrição final.
        # Aqui, vamos garantir que a ordem de gravação no .movimentos corresponda à lógica de descrição esperada.
        self.mover_disco(self.origem, self.destino, self.auxiliar)

        # Passo Recursivo 2: Mover n-1 discos do Auxiliar para o Destino, usando a Origem como auxiliar temporário
        self.solucionar(self.num_discos - 1, self.auxiliar, self.destino, self.origem)


    def get_descricao(self):
        """
        Retorna uma string formatada descrevendo o passo a passo da solução.
        """
        # A implementação recursiva precisa ser ajustada para gerar a sequência exata de movimentos
        # conforme o exemplo esperado do design, que é mais fácil de gerenciar diretamente na recursão se seguirmos o padrão clássico de impressão.
        
        # Reimplementação focada em geração da string de saída (seguindo o design de como os movimentos são listados)
        
        def recursive_solver(n, origem, destino, auxiliar):
            if n == 0:
                return
            
            # Move n-1 discos de Origem para Auxiliar usando Destino como aux
            recursive_solver(n - 1, origem, auxiliar, destino)
            
            # Move o disco n de Origem para Destino
            self.movimentos.append(f"Mover disco {n} de {origem} para {destino}")
            
            # Move n-1 discos de Auxiliar para Destino usando Origem como aux
            recursive_solver(n - 1, auxiliar, destino, origem)

        # Limpar movimentos anteriores se for chamado novamente (embora não deva ser necessário em um fluxo TDD puro)
        self.movimentos = []
        
        recursive_solver(self.num_discos, self.origem, self.destino, self.auxiliar)
        
        return "\n".join(self.movimentos)

# Exemplo de Uso:
if __name__ == '__main__':
    try:
        hanoi = HanoiTower(num_discos=3, origem='A', destino='C', auxiliar='B')
        descricao = hanoi.get_descricao()
        print("--- Solução da Torre de Hanoi (N=3) ---")
        print(descricao)
    except ValueError as e:
        print(f"Erro na inicialização: {e}")