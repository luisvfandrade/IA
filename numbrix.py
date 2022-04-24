# numbrix.py: Template para implementação do projeto de Inteligência Artificial 2021/2022.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 17:
# 94179 Luis Freire D'Andrade
# 95531 Ana Rita Duarte

import sys
import copy
from turtle import end_fill

from sympy import true
from search import Problem, Node, astar_search, breadth_first_tree_search, depth_first_tree_search, greedy_search, recursive_best_first_search


class NumbrixState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = NumbrixState.state_id
        NumbrixState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    def get_board(self) -> list:
        return self.board

    def __eq__(self, obj):
        return isinstance(obj, NumbrixState) and self.board == obj.get_board()

    def __hash__(self):
        return hash(str(self.board.repr))


class Board:
    """ Representação interna de um tabuleiro de Numbrix. """
    def __init__(self, n : int):
        self.size = n
        self.repr = [([0] * n) for _ in range(n)]
        self.numbers = []
        self.positions = {}
    
    def get_number(self, row: int, col: int) -> int:
        """ Devolve o valor na respetiva posição do tabuleiro. """
        try:
            return self.repr[row][col]
        except IndexError as exception:
            sys.exit(exception)

    def adjacent_vertical_numbers(self, row: int, col: int) -> (int, int):
        """ Devolve os valores imediatamente abaixo e acima, 
        respectivamente. """
        try:
            if row == 0:
                return (self.repr[row + 1][col], None)
            elif row == self.size - 1:
                return (None, self.repr[row - 1][col])
            else:
                return (self.repr[row + 1][col], self.repr[row - 1][col])
        except IndexError as exception:
            sys.exit(exception)
    
    def adjacent_horizontal_numbers(self, row: int, col: int) -> (int, int):
        """ Devolve os valores imediatamente à esquerda e à direita, 
        respectivamente. """
        try:
            if col == 0:
                return (None, self.repr[row][col + 1])
            elif col == self.size - 1:
                return (self.repr[row][col - 1], None)
            else:
                return (self.repr[row][col - 1], self.repr[row][col + 1])
        except IndexError as exception:
            sys.exit(exception)
    
    @staticmethod    
    def parse_instance(filename: str):
        """ Lê o ficheiro cujo caminho é passado como argumento e retorna
        uma instância da classe Board. """
        try:
            file = open(filename, "r")
            lines = file.read().splitlines()
            file.close()
        except IOError as exception:
            sys.exit(exception)

        if len(lines[0].split()) != 1:
            sys.exit("File format not supported.")
        board = Board(int(lines[0]))

        if len(lines) != board.size + 1:
            sys.exit("File format not supported.")

        row = 0
        for i in range(1, len(lines)):
            col = 0
            nums = lines[i].split("\t")
            if len(nums) > board.size:
                sys.exit("File format not supported.")
            for num in nums:
                n = int(num)
                if n != 0:
                    board.repr[row][col] = n
                    board.numbers.append(n)
                    board.positions[n] = (row, col)
                col += 1
            row += 1

        if len(board.numbers) != len(set(board.numbers)):
            sys.exit("Board not valid, contains duplicate numbers.")

        return board

    def get_size(self) -> int:
        return self.size

    def get_all_numbers(self) -> list:
        return self.numbers

    def get_all_positions(self) -> dict:
        return self.positions
    
    def get_position_actions(self, row: int, col: int) -> int:
        return self.positionActions[(row, col)]

    def set_number(self, row: int, col: int, number: int):
        try:
            self.repr[row][col] = number
        except IndexError as exception:
            sys.exit(exception)
        self.numbers.append(number)
        self.positions[number] = (row, col)

    def set_position_actions(self, positionActions: dict):
        self.positionActions = positionActions

    def to_string(self) -> str:
        string = ""
        for i in range(self.size):
            for j in range(self.size):
                string += str(self.repr[i][j])
                if j != self.size - 1:
                    string += '\t'
            string += '\n'

        return string

    def __eq__(self, obj):
        if not isinstance(obj, Board) or self.size != obj.get_size() or set(self.numbers) != set(obj.get_all_numbers()):
            return False

        for number in self.positions:
            objPositions = obj.get_all_positions()
            if self.positions[number] != objPositions[number]:
                return False

        return True


class Numbrix(Problem):
    def __init__(self, board: Board):
        """ O construtor especifica o estado inicial. """
        super().__init__(NumbrixState(board))

    def actions(self, state: NumbrixState):
        """ Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento. """
        board = state.get_board()
        boardSize = board.get_size()
        boardPositions = board.get_all_positions()

        actions = {}
        positions = {}
        for row in range(boardSize):
            for col in range(boardSize):
                if board.get_number(row, col) != 0:
                    continue
                
                positions[(row, col)] = 0
                minNumber = boardSize ** 2 + 1
                maxNumber = 0
                for number in boardPositions:
                    numberPosition = boardPositions[number]
                    manhattanDistance = abs(row - numberPosition[0]) + abs(col - numberPosition[1])

                    minPossibility = number - manhattanDistance
                    if minPossibility >= 0 and minPossibility < minNumber:
                        minNumber = minPossibility

                    maxPossibility = number + manhattanDistance
                    if maxPossibility <= (boardSize ** 2) + 1 and maxPossibility > maxNumber:
                        maxNumber = maxPossibility

                for possibleNumber in range(1, minPossibility + 1):
                    if possibleNumber not in boardPositions:
                        actions.setdefault(possibleNumber, [])
                        actions[possibleNumber].append((row, col, possibleNumber))
                        positions[(row, col)] += 1
                for possibleNumber in range(maxPossibility, (boardSize ** 2) + 1):
                    if possibleNumber not in boardPositions:
                        actions.setdefault(possibleNumber, [])
                        actions[possibleNumber].append((row, col, possibleNumber))
                        positions[(row, col)] += 1

        board.set_position_actions(positions)
        if not actions:
            return []
        else:
            minActions = (float('inf'), 0)
            for possibleNumber in actions:
                numActions = len(actions[possibleNumber])
                if numActions < minActions[0]:
                    minActions = (numActions, possibleNumber)

            return actions[minActions[1]]

    def result(self, state: NumbrixState, action):
        """ Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de 
        self.actions(state). """
        resultState = copy.deepcopy(state)
        
        boardActions = self.actions(resultState)
        if action not in boardActions:
            sys.exit("Action not valid, not contained in possible actions.")

        resultState.get_board().set_number(action[0], action[1], action[2])
        return resultState

    def goal_test(self, state: NumbrixState):
        """ Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro 
        estão preenchidas com uma sequência de números adjacentes. """
        board = state.get_board()
        boardSize = board.get_size()

        boardNumbers = board.get_all_numbers()
        if len(set(boardNumbers)) < (boardSize ** 2):
            return False
        
        for i in range(boardSize):
            for j in range(boardSize):
                number = board.get_number(i, j)
                verticalNumbers = board.adjacent_vertical_numbers(i, j)
                horizontalNumbers = board.adjacent_horizontal_numbers(i, j)
                if number + 1 <= (boardSize ** 2) and number + 1 not in \
                    verticalNumbers and number + 1 not in horizontalNumbers:
                    return False
                if number - 1 > 0 and number - 1 not in verticalNumbers \
                    and number - 1 not in horizontalNumbers:
                    return False
        
        return True

    def h(self, node: Node):
        """ Função heuristica utilizada para a procura A*. """
        # (boardSize ** 2) - len(boardNumbers) - optimism (manhattanDistance?)
        board = node.state.get_board()
        boardSize = board.get_size()

        base = (boardSize ** 2) - len(board.get_all_numbers())
        if node.path_cost != 0:
            parentBoard = node.parent.state.get_board()
            action = node.action
            base -= ((boardSize ** 2 - len(parentBoard.get_all_numbers())) - parentBoard.get_position_actions(action[0], action[1]))
     
        return base


if __name__ == "__main__":
    # Ler o ficheiro de input de sys.argv[1],
    if len(sys.argv) != 2:
        sys.exit("Incorrect Program Usage.\nCorrect Usage: $ python3 numbrix.py <instance_file>")
    board = Board.parse_instance(sys.argv[1])
    problem = Numbrix(board)

    '''
    # Example

    s0 = NumbrixState(board)
    print("Initial:\n", s0.get_board().to_string(), sep = "")

    s1 = problem.result(s0, problem.actions(s0)[1])
    s2 = problem.result(s1, problem.actions(s1)[0])
    s3 = problem.result(s2, problem.actions(s2)[1])
    s4 = problem.result(s3, problem.actions(s3)[0])
    s5 = problem.result(s4, problem.actions(s4)[0])

    print("Is goal?", problem.goal_test(s5))
    print("Solution:\n", s5.get_board().to_string(), sep="")
    '''

    # Usar uma técnastara resolver a instância,
    solutionNode = astar_search(problem)

    # Retirar a solução a partir do nó resultante,
    solutionState = solutionNode.state

    # Imprimir para o standard output no formato indicado.
    print(solutionState.get_board().to_string())
