import random, math, copy
import gomoku
from gomoku import Board, Move, GameState


class GameTreeNode: 
    def __init__(self, state, parent):
        self.state = state
        self.valid_moves = gomoku.valid_moves(self.state)
        self.parent = parent # pointer, for ease of use, corresponding to the previous game state
        self.children = []   # A container with children, corresponding to possible moves/subsequent game states.
        self.N = 0           # of visits to the node – this is used for exploration purposes
        self.Q = 0           # the total number of accrued points, i.e., the number of wins plus 0.5 times the number of draws.

    def isTerminal(self):
        if len(gomoku.valid_moves(self.state)) == 0:
            return True
        return False
    
    def isFullyExpanded(self):
        return len(self.children) == len(self.valid_moves) # If equal, The node is fully expanded because there is a childNode for each move.
    
    def UCT(self):
        return (self.Q / self.N) + (1 / math.sqrt(2)) * math.sqrt(2 * math.log(self.parent.N) / self.N)

def findSpotToExpand(node):
        if node.isTerminal():
            return node
        
        if not node.isFullyExpanded(): # create a new child node for a not-yet-explored move (with n as its parent)
            valid, win, childState = gomoku.move(node.state, random.choice(node.valid_moves))
            childNode = GameTreeNode(childState, node)
            node.Children.append(childNode)
            return childNode
        
        bestChildNode = None
        bestUCT = 0

        for child in node.children:
            childScore = child.UCT()
            if childScore > bestUCT:
                bestChildNode = child
                bestUCT = childScore

        bestChildNode = node.highestUCT()
        return findSpotToExpand(bestChildNode)

def rollout(node):
    state = node.state

    


class ahmet_agent:
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

    def move(self, state: GameState, last_move: Move, max_time_to_move: int = 1000) -> Move:
        """This is the most important method: the agent will get:
        1) the current state of the game
        2) the last move by the opponent
        3) the available moves you can play (this is a special service we provide ;-) )
        4) the maximum time until the agent is required to make a move in milliseconds [diverging from this will lead to disqualification].
        """
        n_root = GameTreeNode(state, None,)
    
        while max_time_to_move != 0:
            n_leaf = findSpotToExpand(n_root)
            val = rollout(n_leaf)
            BackupValue(n_leaf, val)
            max_time_to_move -= 1

    def id(self) -> str:
        """Please return a string here that uniquely identifies your submission e.g., "name (student_id)" """
        return "Ahmet Serdar Çanak (1760039)"