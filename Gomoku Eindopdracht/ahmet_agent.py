import gomoku, random, math, time
from gomoku import Board, Move, GameState
from copy import deepcopy

class GameTreeNode:
    def __init__(self, state, parent=None, lastMove=None):
        self.state      = deepcopy(state)
        self.parent     = parent
        self.validMoves = gomoku.valid_moves(self.state)
        self.lastMove   = lastMove # pointer, for ease of use, corresponding to the previous game state
        self.children   = []       # A container with children, corresponding to possible moves/subsequent game states.
        self.N          = 0        # of visits to the node – this is used for exploration purposes
        self.Q          = 0        # the total number of accrued points, i.e., the number of wins plus 0.5 times the number of draws.

    def isTerminal(self): #returns whether the game is finished or not
        if gomoku.check_win(self.state[0], self.lastMove) or len(self.validMoves) == 0:
            return True
        return False

    def isFullyExpanded(self):
        return len(self.children) == len(self.validMoves) # If equal, The node is fully expanded because there is a childNode for each move.

    def UCT(self): #returns the uct result of the child
        return (self.Q / self.N) + (1 / math.sqrt(2)) * math.sqrt(2 * math.log(self.parent.N) / self.N)


class ahmetPlayer:
    """This class specifies a player that just does random moves.
    The use of this class is two-fold: 1) You can use it as a base random roll-out policy.
    2) it specifies the required methods that will be used by the competition to run
    your player
    """
    def __init__(self, black_: bool = True):
        """Constructor for the player."""
        self.black = black_

    def new_game(self, black_: bool):
        """At the start of each new game you will be notified by the competition.
        this method has a boolean parameter that informs your agent whether you
        will play black or white.
        """
        self.black = black_

    def whoWon(self, node, state): 
        """
        Return: Who won, 1 == You, -1 == Opponent, 0 == Draw.
        """
        if gomoku.check_win(state[0], node.lastMove):
            if state[1] % 2 != self.black:
                return 1
            if state[1] % 2 == self.black:
                return -1
        return 0

    def findSpotToExpand(self, node): # Algoritme (22) uit de reader.
        if node.isTerminal(): # returns the root-node if the game has finished
            return node

        valid_moves = gomoku.valid_moves(node.state)

        if not node.isFullyExpanded():
            random.shuffle(valid_moves)
            action = valid_moves.pop()

            while True:
                for child in node.children: #find unexplored actions
                    if child.lastMove == action:
                        action = valid_moves.pop()
                break

            _, _, state = gomoku.move(deepcopy(node.state), action)

            newChildNode = GameTreeNode(state, node, action)
            node.children.append(newChildNode)

            return newChildNode
        
        bestChildNode = None
        bestUCT = -math.inf

        for child in node.children:
            childScore = child.UCT()
            if childScore > bestUCT:
                bestChildNode = child
                bestUCT = childScore
                
        return self.findSpotToExpand(bestChildNode)

    def rollout(self, node): # Algoritme (23) uit de reader.
        state = deepcopy(node.state)
        valid_moves = deepcopy(gomoku.valid_moves(node.state))
        random.shuffle(valid_moves)

        while not node.isTerminal() and len(valid_moves) != 0:
            action = valid_moves.pop()
            _, _, state = gomoku.move(state, action)

        return self.whoWon(node, state)

    def BackupValue(self, val, node): # Algoritme (24) uit de reader.
        while node is not None:
            node.N += 1
            if node.state[1] % 2 == self.black:
                node.Q -= val
            else:
                node.Q += val

            node = node.parent

    def move(self, state: GameState, last_move: Move, max_time_to_move: int = 1000) -> Move: #Algoritme (21) uit de reader.
        """This is the most important method: the agent will get:
        1) the current state of the game
        2) the last move by the opponent
        3) the available moves you can play (this is a special service we provide ;-) )
        4) the maximum time until the agent is required to make a move in milliseconds [diverging from this will lead to disqualification].
        """
        n_root = GameTreeNode(deepcopy(state), lastMove=last_move)
        
        while max_time_to_move != 0:
            n_leaf = self.findSpotToExpand(n_root)
            val    = self.rollout(n_leaf)
            self.BackupValue(val, n_leaf)
            max_time_to_move -= 1

        bestMove = None
        bestVal = -math.inf

        for child in n_root.children:
            childVal = child.Q / child.N
            if childVal > bestVal and child.lastMove in gomoku.valid_moves(deepcopy(state)):
                bestVal = childVal
                bestMove = child.lastMove

        return bestMove

    def id(self) -> str:
        """Please return a string here that uniquely identifies your submission e.g., "name (student_id)" """
        return "Ahmet Serdar Çanak (1760039)"