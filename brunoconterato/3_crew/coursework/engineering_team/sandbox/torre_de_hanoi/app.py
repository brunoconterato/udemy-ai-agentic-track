import tkinter as tk
from tkinter import messagebox
# Import a solução que contém a classe HanoiTower do backend
from solution import HanoiTower

class HanoiApp:
    def __init__(self, master):
        """Inicializa a aplicação da Torre de Hanoi."""
        self.master = master
        master.title("Torre de Hanoi Demo")
        
        # Variáveis de controle
        self.num_discos = tk.IntVar(value=3) # Valor inicial
        self.result_text = tk.StringVar()

        # --- Interface de Usuário ---
        
        # Título
        tk.Label(master, text="Demonstrador da Torre de Hanoi", font=('Arial', 16, 'bold')).pack(pady=15)
        
        # Entrada para o número de discos
        self.entry_frame = tk.Frame(master)
        self.entry_frame.pack(pady=10)
        
        tk.Label(self.entry_frame, text="Número de Discos (n):").pack(side=tk.LEFT, padx=5)
        
        self.entry = tk.Entry(self.entry_frame, textvariable=self.num_discos, width=10)
        self.entry.pack(side=tk.LEFT, padx=5)
        self.entry.bind('<Return>', self.solve_hanoi) # Adiciona funcionalidade de Enter

        # Botão para resolver
        self.solve_button = tk.Button(master, text="Resolver", command=self.solve_hanoi, font=('Arial', 12))
        self.solve_button.pack(pady=10)

        # Área para exibir o resultado
        tk.Label(master, text="Sequência de Movimentos:").pack()
        
        result_label = tk.Label(master, textvariable=self.result_text, justify=tk.LEFT, padx=10, pady=10, bg='lightyellow')
        result_label.pack(fill=tk.BOTH, expand=True)

    def solve_hanoi(self):
        """Lógica para obter os dados do backend e exibir no frontend."""
        try:
            n = self.num_discos.get()
            if n < 0:
                messagebox.showerror("Erro", "O número de discos não pode ser negativo.")
                return

            # 1. Instanciar a classe do backend
            hanoi = HanoiTower(n)
            
            # 2. Chamar o método para resolver e obter os movimentos
            moves = hanoi.solve(n)
            
            # 3. Formatar a saída dos movimentos
            if not moves:
                display_text = "Nenhum movimento encontrado."
            else:
                display_text = "\n".join([f"Movimento {i+1}: ({origem} -> {destino})" for i, (origem, destino) in enumerate(moves)])

            # 4. Exibir o resultado na interface
            self.result_text.set(display_text)

        except Exception as e:
            messagebox.showerror("Erro de Execução", f"Ocorreu um erro ao resolver: {e}")
            self.result_text.set("Erro ao calcular os movimentos.")


if __name__ == "__main__":
    root = tk.Tk()
    app = HanoiApp(root)
    root.mainloop()