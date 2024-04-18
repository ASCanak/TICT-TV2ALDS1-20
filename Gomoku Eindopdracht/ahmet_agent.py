import gomoku, random, math, time
from gomoku import Board, Move, GameState
from copy import deepcopy

class GameTreeNode:
    """
    This is a node in the tree used to represent possible game states. It keeps track of the game state, the parent node, the last move made, 
    valid moves, children of the node, and some statistics for the MCTS algorithm such as the number of visits and the total score.
    """
    def __init__(self, state, parent=None, lastMove=None):
        self.state      = deepcopy(state)
        self.parent     = parent
        self.validMoves = gomoku.valid_moves(self.state)
        self.lastMove   = lastMove # pointer, for ease of use, corresponding to the previous game state
        self.children   = []       # A container with children, corresponding to possible moves/subsequent game states.
        self.N          = 0        # of visits to the node – this is used for exploration purposes
        self.Q          = 0        # the total number of accrued points, i.e., the number of wins plus 0.5 times the number of draws.

    def isTerminal(self): 
        """
        Checks whether the current game has ended by looking at winning conditions or an empty list of valid moves.

        Time-Complexity O(1): This is because it simply checks for win conditions and the presence of valid moves, both of which can be determined with fixed, constant-time operations.
        """
        if gomoku.check_win(self.state[0], self.lastMove) or len(self.validMoves) == 0:
            return True
        return False

    def isFullyExpanded(self):
        """
        Checks whether all possible children of the node have been generated.
        
        Time-Complexity O(1): This comparison involves accessing the lengths of two lists, which are operations that take constant time, regardless of the size of the lists.
        """
        return len(self.children) == len(self.validMoves)

    def UCT(self): 
        """
        Calculates the Upper Confidence Bound for Trees (UCT) score for a child of the node. 
        This is used to select the child node to expand during the selection phase of MCTS.
        
        Time-Complexity O(1): This is because its time complexity is not dependent on any input size, but rather on fixed operations and accessing attributes of the node, which are constant-time operations.
        """
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
        """ Determines who has won the game based on the current state and the last move.
        Return: Who won, 1 == You, -1 == Opponent, 0 == Draw.
        """
        if gomoku.check_win(state[0], node.lastMove):
            if state[1] % 2 != self.black:
                return 1
            if state[1] % 2 == self.black:
                return -1
        return 0

    def findSpotToExpand(self, node): # Algoritme (22) uit de reader.
        """
        Chooses a node to expand according to the MCTS algorithm. It first tries to find unexplored moves, 
        and otherwise chooses the child node with the highest UCT score.

        Time-Complexity O(n): This is because the most significant factor influencing the time complexity is the computation of the list of valid moves, which takes O(n) time. 
        The other operations within the method, such as iterating over the children or shuffling the list of valid moves, 
        are relatively minor compared to the linear time complexity of generating the list of valid moves. 
        """
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
        """
        Performs a roll-out from the given node to the end of the game and determines the winner.
        
        Time-Complexity O(n): This is because the dominant factor in the time complexity of rollout is the generation and shuffling of the list of valid moves, 
        both of which have a time complexity of O(n) where n is the number of valid moves. 
        """
        state = deepcopy(node.state)
        valid_moves = deepcopy(gomoku.valid_moves(node.state))
        random.shuffle(valid_moves)

        while not node.isTerminal() and len(valid_moves) != 0:
            action = valid_moves.pop()
            _, _, state = gomoku.move(state, action)

        return self.whoWon(node, state)

    def BackupValue(self, val, node): # Algoritme (24) uit de reader.
        """
        Updates the statistics of all nodes along the path from the expanded node to the root with the outcome of the roll-out.
        
        Time-Complexity O(1): This is because it is just based on a single node.
        """
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