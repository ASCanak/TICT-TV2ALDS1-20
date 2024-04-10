import random, math, copy
import gomoku
from gomoku import Board, Move, GameState

    
class GameTreeNode:
    def __init__(self, state, parent=None, last_move=None):
        self.state     = state
        self.parent    = parent
        self.last_move = last_move # pointer, for ease of use, corresponding to the previous game state
        self.children  = []        # A container with children, corresponding to possible moves/subsequent game states.
        self.N         = 0         # of visits to the node – this is used for exploration purposes
        self.Q         = 0         # the total number of accrued points, i.e., the number of wins plus 0.5 times the number of draws.

    def isTerminal(self): #returns whether the game is finished or not
        if gomoku.check_win(self.state[0], self.last_move) or len(gomoku.valid_moves(self.state)) == 0:
            return True
        return False

    def isFullyExpanded(self):
        return len(self.children) == len(gomoku.valid_moves(self.state)) # If equal, The node is fully expanded because there is a childNode for each move.

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

    def whoWon(self, node): 
        """
        Return: Who won, 1 == You, -1 == Opponent, 0 == Draw.
        """
        if gomoku.check_win(node.state[0], node.last_move):
            if node.state[1] % 2 != self.black:
                return 1
            if node.state[1] % 2 == self.black:
                return -1
        return 0

    def findSpotToExpand(self, node): # Algoritme (22) uit de reader.
        if node.isTerminal(): # returns the root-node if the game has finished
            return node

        valid_moves = copy.deepcopy(gomoku.valid_moves(node.state))

        if not node.isFullyExpanded():
            copy_state = copy.deepcopy(node.state)
            random.shuffle(valid_moves)
            action = valid_moves.pop()

            while True:
                for child in node.children: #find unexplored actions
                    if child.last_move == action:
                        action = valid_moves.pop()
                break

            valid, win, state = gomoku.move(copy_state, action)

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

    def rollout(self, node, state): # Algoritme (23) uit de reader.
        valid_moves = copy.deepcopy(gomoku.valid_moves(node.state))
        random.shuffle(valid_moves)

        while not node.isTerminal() and len(valid_moves) != 0:
            action = valid_moves.pop()
            valid, win, state = gomoku.move(state, action)

        return self.whoWon(node) #Returns who won

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
        n_root = GameTreeNode(copy.deepcopy(state), last_move=last_move)

        while max_time_to_move != 0:
            n_leaf = self.findSpotToExpand(n_root)
            val    = self.rollout(n_leaf, copy.deepcopy(state))
            self.BackupValue(val, n_leaf)
            max_time_to_move -= 1

        bestMove = None
        bestVal = -math.inf

        for child in n_root.children:
            childVal = child.Q / child.N
            if childVal > bestVal and child.last_move in gomoku.valid_moves(copy.deepcopy(state)):
                bestVal = childVal
                bestMove = child.last_move

        return bestMove

    def id(self) -> str:
        """Please return a string here that uniquely identifies your submission e.g., "name (student_id)" """
        return "Ahmet Serdar Çanak (1760039)"