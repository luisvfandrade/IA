# Grupo 17:
# 94179 Luis Freire D'Andrade
# 95531 Ana Rita Duarte

from pickletools import int4
import sys
import copy
from search import Problem, Node, astar_search, breadth_first_tree_search, depth_first_tree_search, greedy_search, recursive_best_first_search
from utils import manhattan_distance


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


class Board:
    """ Representação interna de um tabuleiro de Numbrix. """
    def __init__(self, n : int):
        self.size = n
        self.repr = [([0] * n) for _ in range(n)]
        self.numbers = []
        self.positions = {}
        self.positionActionsChosen = False
        self.numberActionsChosen = False
    
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

    def position_actions_chosen(self) -> int:
        return self.positionActionsChosen

    def number_actions_chosen(self) -> int:
        return self.numberActionsChosen
    
    def get_position_actions(self, row: int, col: int) -> int:
        return len(self.positionActions[(row, col)])

    def get_number_actions(self, number: int) -> int:
        return len(self.numberActions[number])

    def get_holes(self) -> int:
        holes = 0
        for row in range(self.size):
            for col in range(self.size):
                if self.repr[row][col] == 0 and self.adjacent_vertical_numbers(row, col)[1] != 0 and self.adjacent_horizontal_numbers(row, col)[0] != 0:
                    holes += 1
        
        return holes

    def set_number(self, row: int, col: int, number: int):
        try:
            self.repr[row][col] = number
        except IndexError as exception:
            sys.exit(exception)
        self.numbers.append(number)
        self.positions[number] = (row, col)

    def set_position_actions(self, positionActions: dict):
        self.numberActionsChosen = True
        self.positionActions = positionActions

    def set_number_actions(self, numberActions: dict):
        self.positionActionsChosen = True
        self.numberActions = numberActions

    def to_string(self) -> str:
        string = ""
        for i in range(self.size):
            for j in range(self.size):
                string += str(self.repr[i][j])
                if j != self.size - 1:
                    string += '\t'
            if i != self.size - 1:
                string += '\n'

        return string


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

        if len(board.get_all_numbers()) == (boardSize ** 2):
            return []

        actions = {}
        positions = {}
        minPositionActions = (float('inf'), (0, 0))
        for row in range(boardSize):
            for col in range(boardSize):
                if board.get_number(row, col) != 0:
                    continue
                
                positions.setdefault((row, col), [])
                for possibleNumber in range(1, boardSize ** 2 + 1):
                    if possibleNumber in boardPositions:
                        continue
                    
                    possible = True
                    for number in boardPositions:
                        absoluteValue = abs(possibleNumber - number)
                        manhattanDistance = manhattan_distance((row, col), boardPositions[number])
                        if manhattanDistance > absoluteValue or manhattanDistance % 2 != absoluteValue % 2:
                            possible = False
                            break

                    actions.setdefault(possibleNumber, [])
                    if possible:
                        actions[possibleNumber].append((row, col, possibleNumber))
                        positions[(row, col)].append((row, col, possibleNumber))

                positionActions = len(positions[(row, col)])
                if positionActions == 0:
                    return []
                elif positionActions < minPositionActions[0]:
                    minPositionActions = (positionActions, (row, col))

        minNumActions = (float('inf'), 0)
        for possibleNumber in actions:
            numActions = len(actions[possibleNumber])
            if numActions == 0:
                return []
            elif numActions < minNumActions[0]:
                minNumActions = (numActions, possibleNumber) 

        if minPositionActions[0] < minNumActions[0]:
            board.set_number_actions(actions)
            return positions[minPositionActions[1]]
        else:
            board.set_position_actions(positions)
            return actions[minNumActions[1]]

    def result(self, state: NumbrixState, action):
        """ Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de 
        self.actions(state). """
        board = state.get_board()
        boardPositions = board.get_all_positions()
        resultBoard = Board(board.get_size())
        for number in boardPositions:
            position = boardPositions[number]
            resultBoard.set_number(position[0], position[1], number)

        resultBoard.set_number(action[0], action[1], action[2])

        return NumbrixState(resultBoard)

    def goal_test(self, state: NumbrixState):
        """ Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro 
        estão preenchidas com uma sequência de números adjacentes. """
        board = state.get_board()
        boardSize = board.get_size()

        return len(board.get_all_numbers()) == boardSize ** 2

    def h(self, node: Node):
        """ Função heuristica utilizada para a procura A*. """
        # (boardSize ** 2) - len(boardNumbers) - optimism (manhattanDistance?)
        board = node.state.get_board()
        boardSize = board.get_size()

        base = (boardSize ** 2) - len(board.get_all_numbers()) + board.get_holes()
        if node.path_cost != 0:
            parentBoard = node.parent.state.get_board()
            action = node.action
            if board.number_actions_chosen():
                base += parentBoard.get_position_actions(action[0], action[1])
            elif board.position_actions_chosen():
                base += parentBoard.get_number_actions(action[2])

        return base


if __name__ == "__main__":
    # Ler o ficheiro de input de sys.argv[1],
    board = Board.parse_instance(sys.argv[1])
    problem = Numbrix(board)

    # Usar uma técnastara resolver a instância,
    solutionNode = greedy_search(problem)

    # Retirar a solução a partir do nó resultante,
    solutionState = solutionNode.state

    # Imprimir para o standard output no formato indicado.
    print(solutionState.get_board().to_string())
