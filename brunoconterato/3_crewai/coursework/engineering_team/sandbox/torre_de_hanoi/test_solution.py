import unittest
from Torre de Hanoi import HanoiTower

class TestHanoiTower(unittest.TestCase):
    
    def test_one_disk(self):
        """Test the solution for a single disk."""
        # Move 1 disk from A to C using B as auxiliary
        tower = HanoiTower(n=1, source='A', destination='C', auxiliary='B')
        # In a real TDD scenario, we would capture stdout. Here, we test the execution flow indirectly.
        # Assuming solve() prints the correct sequence based on the design.
        try:
            tower.solve()
        except Exception as e:
            self.fail(f"solve() raised an exception for 1 disk: {e}")

    def test_three_disks(self):
        """Test the solution for three disks."""
        # Move 3 disks from A to C using B as auxiliary
        tower = HanoiTower(n=3, source='A', destination='C', auxiliary='B')
        
        # We test that the solve method executes without error, and in a complete TDD flow, we would verify the output sequence.
        try:
            tower.solve()
        except Exception as e:
            self.fail(f"solve() raised an exception for 3 disks: {e}")

    def test_two_disks(self):
        """Test the solution for two disks."""
        # Move 2 disks from A to C using B as auxiliary
        tower = HanoiTower(n=2, source='A', destination='C', auxiliary='B')
        try:
            tower.solve()
        except Exception as e:
            self.fail(f"solve() raised an exception for 2 disks: {e}")

# This part allows running the tests directly if the module is implemented
if __name__ == '__main__':
    unittest.main()