import unittest
from TorreDeHanoi import HanoiTower

class TestHanoiTower(unittest.TestCase):
    """Testes unitários para a classe HanoiTower."""

    def test_solve_2_discs(self):
        """Verifica se o método solve() gera a sequência correta para 2 discos."""
        hanoi = HanoiTower()
        # Para 2 discos, o número mínimo de movimentos é 3.
        expected_sequence = [
            ('A', 'C'),  # Mover disco 1 de A para C
            ('A', 'B'),  # Mover disco 2 de A para B
            ('C', 'B')   # Mover disco 1 de C para B
        ]
        self.assertEqual(hanoi.solve(2), expected_sequence)

    def test_solve_3_discs(self):
        """Verifica se o método solve() gera a sequência correta para 3 discos."""
        hanoi = HanoiTower()
        # Para 3 discos, o número mínimo de movimentos é 7.
        expected_sequence = [
            ('A', 'C'), ('A', 'B'), ('C', 'B'),
            ('A', 'C'), ('B', 'A'), ('B', 'C'), ('A', 'C')
        ]
        self.assertEqual(hanoi.solve(3), expected_sequence)

    def test_solve_1_disc(self):
        """Verifica o caso de borda para 1 disco."""
        hanoi = HanoiTower()
        expected_sequence = [('A', 'C')]
        self.assertEqual(hanoi.solve(1), expected_sequence)

    def test_solve_0_discs(self):
        """Verifica o caso de borda para 0 discos (deve retornar uma lista vazia)."""
        hanoi = HanoiTower()
        expected_sequence = []
        self.assertEqual(hanoi.solve(0), expected_sequence)

if __name__ == '__main__':
    unittest.main()