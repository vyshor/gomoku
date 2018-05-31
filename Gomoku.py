import random
import pickle
import math

first = 0
playerplaying = int(input("Player playing?"))
if playerplaying == 1:
    first = int(input("Player playing first?"))
boardsize = int(input("what board size u want?"))
AIweight = [[0.1, 0.2, 0.1, 0.2, 0.1, 0.2], [0.2, 0.2, 0.3, 0.3, 0.1, 0.1]]
WINRATIO = [0, 0]

lastmove = False
previousmove = [[], []]
game = []
GRADING = {}
tier1_grades = 0
tier1_used = False
tier1_records = []
tier1_history = []
tier1_history_scores = []
tier1_nodes = []
tier1_nodes_weight = []

for z in range(81):
    mydict = {}
    for x in range(3):
        temp_msg = str(x)
        for x2 in range(3):
            temp_msg += str(x2)
            for x3 in range(3):
                temp_msg += str(x3)
                for x4 in range(3):
                    temp_msg += str(x4)
                    mydict[temp_msg] = random.uniform(0, 1)
                    temp_msg = temp_msg[:-1]
                temp_msg = temp_msg[:-1]
            temp_msg = temp_msg[:-1]
    tier1_nodes.append(mydict)

for z in range(81):
    tier1_nodes_weight.append(random.uniform(0, 1))

with open("AIweight.txt", 'rb') as f:
    AIweight[0] = pickle.load(f)
    AIweight[1] = pickle.load(f)
    tier1_nodes_weight = pickle.load(f)
    tier1_nodes = pickle.load(f)


# AIweight for 6 nodes

# check ownself got sure win or not
# then check if opponent got next win sure win or not  then block it
# otherwise check if can create surewin conditions such as 4 in a row
# then it goes into neural network after that
# to decide to block opponent build into createsurewin
# or put another piece to get 4 in a row to force opp nxt move
# or set up for a surewin 4-4 in a row, 3-4 in a row, 3-3 in a row

# one node to check empty spots, whether each empty spots, how many own tiles is adjacent to it
# another node to do the same, but opponent tiles is adjacent to it
# one node to check on empty spots such that own tiles is EXX
# and another node to check for opponent EOO
# node to check for EXXX
# and another node to check for EOOO

# use each node to generate a list of possible moves
# then combine the possible moves
# then run each possible moves to generate the respective relative score for each node
# then the relative score times the weight to get the total score for each possible move
# then get the max total score, and play the move

# rewarding system
# if opponent can createsurewin, then penalise
# penalise by reducing the weightage in proportion
# if own player can win or createsurewin, reward
# reward by increasing in weight in proportion

# since now is final score of each point = sum(score for that node * weight of node / max score for that node)
# d(final score)/d(weight) = score for that node/max score for that node

def otherplayer(turn):
    if turn == 1:
        return 2
    else:
        return 1


def sigmoid(t):
    if t < 0:
        return 1 - 1 / (1 + math.exp(t))
    else:
        return 1 / (1 + math.exp(-t))


def invsigmoid(p):
    return math.log((p + 1e-10) / (1 - p + 1e-10))


# Definite algorithm to check win/create win conditions

def checksurewin(turn):  # check for immediate win
    for x in range(0, boardsize):
        for y in range(0, boardsize):
            if game[x][y] == turn:
                for h in [3, -3]:
                    if boardsize - 1 >= x + h >= 0 and boardsize - 1 >= x - 2 * (h // 3) >= 0:
                        lst = [game[x + z][y] for z in range(-2 * (h // 3), 4 * (h // 3), h // 3)]
                        ind = 2
                        if h == -3:
                            lst.reverse()
                        for i in [-1, 0]:
                            if lst[i] == otherplayer(turn):
                                lst.pop(i)
                                ind = i
                        if len(lst) == 6 and lst.count(0) == 2:
                            for t in [0, -1]:
                                if lst[t] == 0:
                                    lst.pop(t)
                                    ind = t
                                    break
                        if len(set(lst)) == 2 and len(lst) == 5 and lst.count(0) == 1:
                            if h == 3:
                                ha = lst.index(0) - 2
                            else:
                                ha = lst.index(0) - 3
                            if ind == 0:
                                ha += 1
                            return x + ha, y

                    if boardsize - 1 >= y + h >= 0 and boardsize - 1 >= y - 2 * (h // 3) >= 0:
                        lst = [game[x][y + z] for z in range(-2 * (h // 3), 4 * (h // 3), h // 3)]
                        ind = 2
                        if h == -3:
                            lst.reverse()
                        for i in [-1, 0]:
                            if lst[i] == otherplayer(turn):
                                lst.pop(i)
                                ind = i
                        if len(lst) == 6 and lst.count(0) == 2:
                            for t in [0, -1]:
                                if lst[t] == 0:
                                    lst.pop(t)
                                    ind = t
                                    break
                        if len(set(lst)) == 2 and len(lst) == 5 and lst.count(0) == 1:
                            if h == 3:
                                ha = lst.index(0) - 2
                            else:
                                ha = lst.index(0) - 3
                            if ind == 0:
                                ha += 1
                            return x, y + ha

                    for d in [1, -1]:  # forgot to consider the other diagnol
                        if boardsize - 1 >= y + d * h >= 0 and boardsize - 1 >= y - 2 * d * (
                                    h // 3) >= 0 and boardsize - 1 >= x + h >= 0 and boardsize - 1 >= x - 2 * (
                                    h // 3) >= 0:
                            lst = [game[x + z][y + d * z] for z in range(-2 * (h // 3), 4 * (h // 3), h // 3)]
                            ind = 2
                            if h == -3:
                                lst.reverse()
                            for i in [-1, 0]:
                                if lst[i] == otherplayer(turn):
                                    lst.pop(i)
                                    ind = i
                            if len(lst) == 6 and lst.count(0) == 2:
                                for t in [0, -1]:
                                    if lst[t] == 0:
                                        lst.pop(t)
                                        ind = t
                                        break
                            if len(set(lst)) == 2 and len(lst) == 5 and lst.count(0) == 1:
                                if h == 3:
                                    ha = lst.index(0) - 2
                                else:
                                    ha = lst.index(0) - 3
                                if ind == 0:
                                    ha += 1
                                return x + ha, y + ha * d

    return False


def printboard():
    global lastmove
    for y in range(-1, boardsize * 2 + 1):
        if y == -1:
            st = "    "
            for x in range(0, boardsize):
                st += "{:^3} ".format(x + 1)
            print(st)
        else:
            if y % 2 == 0:
                st = "    "
                for x in range(0, boardsize):
                    st += "--- "
                print(st)
            else:
                st = "{:>3}|".format(y // 2 + 1)
                for x in range(0, boardsize):
                    move = " "
                    if lastmove and x == lastmove[0] and y // 2 == lastmove[1]:
                        move = "["
                    if game[x][y // 2] == 1:
                        move += "X"
                    elif game[x][y // 2] == 2:
                        move += "O"
                    else:
                        move += " "
                    if lastmove and x == lastmove[0] and y // 2 == lastmove[1]:
                        move += "]"
                    else:
                        move += " "
                    st += move + "|"
                print(st)


def createsurewin(turn):
    for x in range(0, boardsize):
        for y in range(0, boardsize):
            if game[x][y] == turn:
                # this is check for 3 in a row EXXXE
                if boardsize - 1 >= x + 2 >= 0 and boardsize - 1 >= x - 2 >= 0:
                    lst = []
                    for z in range(-2, 3):
                        lst.append(game[x + z][y])
                    if lst[1] == lst[2] == lst[3] == turn and lst[0] == lst[-1] == 0:
                        if not ((not boardsize - 1 >= x - 3 >= 0 or game[x - 3][y] == otherplayer(turn)) and (
                                    not boardsize - 1 >= x + 3 >= 0 or game[x + 3][y] == otherplayer(turn))):
                            if not boardsize - 1 >= x - 3 >= 0 or game[x - 3][y] == otherplayer(turn):
                                return x + 2, y
                            else:
                                return x - 2, y

                if boardsize - 1 >= y + 2 >= 0 and boardsize - 1 >= y - 2 >= 0:
                    lst = []
                    for z in range(-2, 3):
                        lst.append(game[x][y + z])
                    if lst[1] == lst[2] == lst[3] == turn and lst[0] == lst[-1] == 0:
                        if not ((not boardsize - 1 >= y - 3 >= 0 or game[x][y - 3] == otherplayer(turn)) and (
                                    not boardsize - 1 >= y + 3 >= 0 or game[x][y + 3] == otherplayer(turn))):
                            if not boardsize - 1 >= y - 3 >= 0 or game[x][y - 3] == otherplayer(turn):
                                return x, y + 2
                            else:
                                return x, y - 2
                for d in [1, -1]:  # for to check other diaganol
                    if boardsize - 1 >= x + 2 >= 0 and boardsize - 1 >= x - 2 >= 0 and boardsize - 1 >= y + d * 2 >= 0 and boardsize - 1 >= y - d * 2 >= 0:
                        lst = []
                        for z in range(-2, 3):
                            lst.append(game[x + z][y + d * z])
                        if lst[1] == lst[2] == lst[3] == turn and lst[0] == lst[-1] == 0:
                            if not (
                                        (not boardsize - 1 >= x - 3 >= 0 or not boardsize - 1 >= y - d * 3 >= 0 or
                                                 game[x - 3][
                                                         y - d * 3] == otherplayer(turn)) and (
                                                    not boardsize - 1 >= x + 3 >= 0 or not boardsize - 1 >= y + d * 3 >= 0 or
                                                    game[x + 3][
                                                            y + d * 3] == otherplayer(turn))):
                                if not boardsize - 1 >= x - 3 >= 0 or not boardsize - 1 >= y - d * 3 >= 0 or \
                                                game[x - 3][
                                                            y - d * 3] == otherplayer(turn):
                                    return x + 2, y + d * 2
                                else:
                                    return x - 2, y - d * 2

                # this is to check for EX[X]EXE
                for k in [4, -4]:
                    if boardsize - 1 >= x + k - 1 >= 0 and boardsize - 1 >= x - 2 * (k // 4) >= 0:
                        lst = [z for z in range(-2 * (k // 4), k, (k // 4))]
                        for h in range(6):
                            lst[h] = game[x + lst[h]][y]
                        if lst[1] == lst[4] == turn and lst[0] == lst[3] == lst[5] == 0:
                            return x + (k // 4), y

                    if boardsize - 1 >= y + k - 1 >= 0 and boardsize - 1 >= y - 2 * (k // 4) >= 0:
                        lst = [z for z in range(-2 * (k // 4), k, (k // 4))]
                        for h in range(6):
                            lst[h] = game[x][y + lst[h]]
                        if lst[1] == lst[4] == turn and lst[0] == lst[3] == lst[5] == 0:
                            return x, y + (k // 4)

                    for d in [1, -1]:
                        if boardsize - 1 >= x + k - 1 >= 0 and boardsize - 1 >= x - 2 * (
                                    k // 4) >= 0 and boardsize - 1 >= y + d * (
                                    k + 1) >= 0 and boardsize - 1 >= y - 2 * (k // 4) * d >= 0:
                            lst = [z for z in range(-2 * (k // 4), k, (k // 4))]
                            for h in range(6):
                                lst[h] = game[x + lst[h]][y + d * lst[h]]
                            if lst[1] == lst[4] == turn and lst[0] == lst[3] == lst[5] == 0:
                                return x + (k // 4), y + d * (k // 4)

    return False


def forcemove(turn):
    possiblemoves = []
    mustmoves = []
    for x in range(boardsize):
        for y in range(boardsize):
            if game[x][y] == 0:
                for h in [4, 0, -4]:
                    for h2 in [4, 0, -4]:
                        if h == h2 == 0:
                            continue

                        if boardsize - 1 >= x + h >= 0 and boardsize - 1 >= y + h2 >= 0:
                            code = ""
                            for z in range(1, 5):
                                piece = game[x + z * (h // 4)][y + z * (h2 // 4)]
                                if piece == turn:  # 1 for own piece, 2 for opponent piece
                                    code += "1"
                                elif piece == otherplayer(turn):
                                    code += "2"
                                else:
                                    code += "0"

                            if code == "1011" or code == "1101" or code == "0111" or (
                                                    code == "1010" and boardsize - 1 >= x - (
                                                        h // 4) >= 0 and boardsize - 1 >= y - (h2 // 4) >= 0 and
                                            game[x - (h // 4)][
                                                    y - (h2 // 4)] == turn):
                                pos = code.find("0")
                                x2 = x + (pos + 1) * (h // 4)
                                y2 = y + (pos + 1) * (h2 // 4)
                                if (x, y) not in possiblemoves:
                                    possiblemoves.append((x, y))
                                    mustmoves.append((x2, y2))

                                if (x2, y2) not in possiblemoves:
                                    possiblemoves.append((x2, y2))
                                    mustmoves.append((x, y))

    return possiblemoves, mustmoves


def forcemovechecker(turn):
    lst, lst2 = forcemove(turn)
    answer = False
    if lst:
        for z in range(len(lst)):
            coordinate = lst[z]
            x = coordinate[0]
            y = coordinate[1]
            game[x][y] = turn

            coordinate2 = lst2[z]
            x2 = coordinate2[0]
            y2 = coordinate2[1]
            game[x2][y2] = otherplayer(turn)

            if not checksurewin(otherplayer(turn)) and (checksurewin(turn) or createsurewin(turn)):
                answer = (x, y)

            # remember reset back
            game[x][y] = 0
            game[x2][y2] = 0

    return answer


def setupmove(turn):
    move = False
    for x in range(boardsize):
        for y in range(boardsize):
            if game[x][y] == 0:
                game[x][y] == turn  # presume u make this move
                if createsurewin(turn):  # means you can create surewin in next move and opponent need to block
                    b = createsurewin(turn)
                    game[b[0]][b[1]] = otherplayer(turn)  # other player tries to block
                    if not checksurewin(otherplayer(turn)) and createsurewin(
                            turn):  # but you need make sure other player cannot instant win because of that move
                        move = createsurewin(turn)  # but you still can set up
                    game[b[0]][b[1]] = 0
                game[x][y] == 0
    return move


# Tier 1

def grading(turn, coordinate):
    x = coordinate[0]
    y = coordinate[1]
    totalscore = 0
    for nodeindex in range(len(tier1_nodes)):
        mini_sum = 0
        for h in [4, 0, -4]:
            for h2 in [4, 0, -4]:
                if h == h2 == 0:
                    continue

                if boardsize - 1 >= x + h >= 0 and boardsize - 1 >= y + h2 >= 0:
                    code = ""
                    for z in range(1, 5):
                        piece = game[x + z * (h // 4)][y + z * (h2 // 4)]
                        if piece == turn:  # 1 for own piece, 2 for opponent piece
                            code += "1"
                        elif piece == otherplayer(turn):
                            code += "2"
                        else:
                            code += "0"

                    mini_sum += tier1_nodes[nodeindex][code]
        totalscore += mini_sum * tier1_nodes_weight[nodeindex]

    return totalscore


def specificgrading(turn, coordinate):
    x = coordinate[0]
    y = coordinate[1]
    records = []
    for node_index in range(len(tier1_nodes)):
        chart = {}
        for h in [4, 0, -4]:
            for h2 in [4, 0, -4]:
                if h == h2 == 0:
                    continue

                if boardsize - 1 >= x + h >= 0 and boardsize - 1 >= y + h2 >= 0:
                    code = ""
                    for z in range(1, 5):
                        piece = game[x + z * (h // 4)][y + z * (h2 // 4)]
                        if piece == turn:  # 1 for own piece, 2 for opponent piece
                            code += "1"
                        elif piece == otherplayer(turn):
                            code += "2"
                        else:
                            code += "0"

                    if code in chart.keys():
                        chart[code] += tier1_nodes[node_index][code]
                    else:
                        chart[code] = tier1_nodes[node_index][code]

        records.append(chart)
    return records


def boardgrading(turn):
    lstscore = []
    lstlocation = []
    for x in range(boardsize):
        for y in range(boardsize):
            if game[x][y] == 0:
                lstscore.append(grading(turn, (x, y)))
                lstlocation.append((x, y))

    return lstscore, lstlocation


def gradingdecision(turn):
    global tier1_history
    global tier1_history_scores
    lstscore, lstlocation = boardgrading(turn)
    maxscore = 0
    finalcoordinate = "error"
    for x in range(len(lstscore)):
        if lstscore[x] > maxscore:
            finalcoordinate = lstlocation[x]
            maxscore = lstscore[x]

    tier1_history_scores.append(maxscore)
    tier1_history.append(specificgrading(turn, finalcoordinate))
    return finalcoordinate


def tier1_learning(turn, coordinate, before_after):  # before = 0, after = 1,2,3
    # 1 is check if boardscore of opponent decrease or not
    # 2 is penalise regardless of boardscore
    # 3 is reward regardless of boardscore
    global tier1_grades
    if before_after == 0:
        tier1_grades = sum(boardgrading(otherplayer((turn)))[0])
    elif before_after == 1:  # originally with the idea that, if it makes opponent, having worse condition, then good
        if sum(boardgrading(otherplayer(turn))[0]) <= tier1_grades:
            # penalise
            chart = specificgrading(turn, coordinate)
            totalgrade = sum(chart.values())
            for key in chart.keys():
                t = invsigmoid(GRADING[key]) - chart[key] / totalgrade
                GRADING[key] = sigmoid(t)
        else:
            # reward
            chart = specificgrading(turn, coordinate)
            totalgrade = sum(chart.values())
            for key in chart.keys():
                t = invsigmoid(GRADING[key]) + chart[key] / totalgrade
                GRADING[key] = sigmoid(t)
    elif before_after == 2:  # penalise
        for x in range(len(tier1_history)):
            records = tier1_history[x]
            for node_index in range(len(records)):  # change the values of each pattern first in each node
                totalgrade = sum(records[node_index].values())
                for key in records[node_index].keys():
                    t = invsigmoid(tier1_nodes[node_index][key]) - (tier1_nodes_weight[node_index] /
                                                                    tier1_history_scores[x]) * (
                                                                   records[node_index][key] / totalgrade) * math.exp(
                        (x + 1) / len(tier1_history))
                    tier1_nodes[node_index][key] = sigmoid(t)

                t = invsigmoid(tier1_nodes_weight[node_index]) - (tier1_nodes_weight[node_index] * sum(
                    records[node_index].values()) / tier1_history_scores[x]) * math.exp((x + 1) / len(tier1_history))
                tier1_nodes_weight[node_index] = sigmoid(t)

    elif before_after == 3:  # reward

        for x in range(len(tier1_history)):

            records = tier1_history[x]

            for node_index in range(len(records)):  # change the values of each pattern first in each node

                totalgrade = sum(records[node_index].values())

                for key in records[node_index].keys():
                    t = invsigmoid(tier1_nodes[node_index][key]) + (
                                                                       tier1_nodes_weight[node_index] /
                                                                       tier1_history_scores[x]) * (
                                                                       records[node_index][
                                                                           key] / totalgrade) * math.exp(
                        (x + 1) / 10)

                    tier1_nodes[node_index][key] = sigmoid(t)

                t = invsigmoid(tier1_nodes_weight[node_index]) + (tier1_nodes_weight[node_index] * sum(
                    records[node_index].values()) / tier1_history_scores[x]) * math.exp((x + 1) / 10)

                tier1_nodes_weight[node_index] = sigmoid(t)


# Tier 0

def checkownadj(turn):
    maxcount = 1
    lstpoints = []
    for x in range(boardsize):
        for y in range(boardsize):
            if game[x][y] == 0:
                owncount = 0
                for h in [1, -1]:
                    if boardsize - 1 >= x + h >= 0:
                        if game[x + h][y] == turn:
                            owncount += 1

                    if boardsize - 1 >= y + h >= 0:
                        if game[x][y + h] == turn:
                            owncount += 1

                    if boardsize - 1 >= x + h >= 0 and boardsize - 1 >= y + h >= 0:
                        if game[x + h][y + h] == turn:
                            owncount += 1

                    if boardsize - 1 >= x + h >= 0 and boardsize - 1 >= y - h >= 0:
                        if game[x + h][y - h] == turn:
                            owncount += 1

                if owncount == maxcount:
                    lstpoints.append((x, y))

                if owncount > maxcount:
                    lstpoints = [(x, y)]
                    maxcount = owncount

    return lstpoints, maxcount


def checkadjtilescore(turn, coordinate):
    x = coordinate[0]
    y = coordinate[1]
    owncount = 0
    for h in [1, -1]:
        if boardsize - 1 >= x + h >= 0:
            if game[x + h][y] == turn:
                owncount += 1

        if boardsize - 1 >= y + h >= 0:
            if game[x][y + h] == turn:
                owncount += 1

        if boardsize - 1 >= x + h >= 0 and boardsize - 1 >= y + h >= 0:
            if game[x + h][y + h] == turn:
                owncount += 1

        if boardsize - 1 >= x + h >= 0 and boardsize - 1 >= y - h >= 0:
            if game[x + h][y - h] == turn:
                owncount += 1
    return owncount


def checktwoadj(turn):
    lstpoints = []
    points = []
    for x in range(boardsize):
        for y in range(boardsize):
            if game[x][y] == turn:
                if boardsize - 1 >= x + 1 >= 0 and boardsize - 1 >= x - 1 >= 0:
                    z = [game[x - 1][y], game[x + 1][y]]
                    if 0 in z and turn in z:
                        tempint = int(z.index(0) / 0.5) - 1
                        if (x + tempint, y) in lstpoints:
                            points[lstpoints.index((x + tempint, y))] += 1
                        else:
                            lstpoints.append((x + tempint, y))
                            points.append(1)

                if boardsize - 1 >= y + 1 >= 0 and boardsize - 1 >= y - 1 >= 0:
                    z = [game[x][y - 1], game[x][y + 1]]
                    if 0 in z and turn in z:
                        tempint = int(z.index(0) / 0.5) - 1
                        if (x, y + tempint) in lstpoints:
                            points[lstpoints.index((x, y + tempint))] += 1
                        else:
                            lstpoints.append((x, y + tempint))
                            points.append(1)

                for d in [1, -1]:
                    if boardsize - 1 >= x + 1 >= 0 and boardsize - 1 >= x - 1 >= 0 and boardsize - 1 >= y + d * 1 >= 0 and boardsize - 1 >= y - d * 1 >= 0:
                        z = [game[x - 1][y - 1 * d], game[x + 1][y + 1 * d]]
                        if 0 in z and turn in z:
                            tempint = int(z.index(0) / 0.5) - 1
                            if (x + tempint, y + tempint * d) in lstpoints:
                                points[lstpoints.index((x + tempint, y + tempint * d))] += 1
                            else:
                                lstpoints.append((x + tempint, y + tempint * d))
                                points.append(1)

    lstpoints2 = []
    maxpoints = 0
    if lstpoints:
        maxpoints = max(points)
    if maxpoints == 0:
        maxpoints = 1
    for z in range(len(points)):
        if points[z] == maxpoints:
            lstpoints2.append(lstpoints[z])

    return lstpoints2, maxpoints


def checktwoadjtilescore(turn, coordinate):
    x = coordinate[0]
    y = coordinate[1]
    owncount = 0
    for h in [-2, 2]:
        if boardsize - 1 >= x + h >= 0:
            if game[x + h][y] == turn and game[x + h // 2][y] == turn:
                owncount += 1

        if boardsize - 1 >= y + h >= 0:
            if game[x][y + h] == turn and game[x][y + h // 2] == turn:
                owncount += 1

        if boardsize - 1 >= x + h >= 0 and boardsize - 1 >= y + h >= 0:
            if game[x + h][y + h] == turn and game[x + h // 2][y + h // 2] == turn:
                owncount += 1

        if boardsize - 1 >= x + h >= 0 and boardsize - 1 >= y - h >= 0:
            if game[x + h][y - h] == turn and game[x + h // 2][y - h // 2] == turn:
                owncount += 1
    return owncount


def checkthreeadj(turn):
    maxcount = 1
    pointslst = []
    for x in range(boardsize):
        for y in range(boardsize):
            if game[x][y] == 0:
                owncount = 0
                for h in [-3, 3]:
                    if boardsize - 1 >= x + h >= 0:
                        if game[x + h][y] == turn and game[x + h // 3][y] == turn and game[x + 2 * (h // 3)][y] == turn:
                            owncount += 1

                    if boardsize - 1 >= y + h >= 0:
                        if game[x][y + h] == turn and game[x][y + h // 3] == turn and game[x][y + 2 * (h // 3)] == turn:
                            owncount += 1

                    if boardsize - 1 >= x + h >= 0 and boardsize - 1 >= y + h >= 0:
                        if game[x + h][y + h] == turn and game[x + h // 3][y + h // 3] == turn and \
                                        game[x + 2 * (h // 3)][y + 2 * (h // 3)] == turn:
                            owncount += 1

                    if boardsize - 1 >= x + h >= 0 and boardsize - 1 >= y - h >= 0:
                        if game[x + h][y - h] == turn and game[x + h // 3][y - h // 3] == turn and \
                                        game[x + 2 * (h // 3)][y - 2 * (h // 3)] == turn:
                            owncount += 1

                if owncount == maxcount:
                    pointslst.append((x, y))

                if owncount > maxcount:
                    pointslst = [(x, y)]
                    maxcount = owncount
    return pointslst, maxcount


def checkthreeadjtilescore(turn, coordinate):
    x = coordinate[0]
    y = coordinate[1]
    owncount = 0
    for h in [-3, 3]:
        if boardsize - 1 >= x + h >= 0:
            if game[x + h][y] == turn and game[x + h // 3][y] == turn and game[x + 2 * (h // 3)][y] == turn:
                owncount += 1

        if boardsize - 1 >= y + h >= 0:
            if game[x][y + h] == turn and game[x][y + h // 3] == turn and game[x][y + 2 * (h // 3)] == turn:
                owncount += 1

        if boardsize - 1 >= x + h >= 0 and boardsize - 1 >= y + h >= 0:
            if game[x + h][y + h] == turn and game[x + h // 3][y + h // 3] == turn and game[x + 2 * (h // 3)][
                        y + 2 * (h // 3)] == turn:
                owncount += 1

        if boardsize - 1 >= x + h >= 0 and boardsize - 1 >= y - h >= 0:
            if game[x + h][y - h] == turn and game[x + h // 3][y - h // 3] == turn and game[x + 2 * (h // 3)][
                        y - 2 * (h // 3)] == turn:
                owncount += 1
    return owncount


def losingmechanics(turn, coordinates):
    lst = previousmove[turn - 1]
    point = coordinates
    if lst:
        totalscore = sum(lst)
        for x in range(len(lst)):
            t = invsigmoid(AIweight[turn - 1][x]) - lst[x] / totalscore / 100
            AIweight[turn - 1][x] = sigmoid(t)


def winningmechanics(turn):
    lst = previousmove[turn - 1]
    if lst:
        totalscore = sum(lst)
        for x in range(len(lst)):
            t = invsigmoid(AIweight[turn - 1][x]) + lst[x] / totalscore / 100
            AIweight[turn - 1][x] = sigmoid(t)


def tier0_decision(turn):
    possiblepoints = checkownadj(turn)[0] + checkownadj(otherplayer(turn))[0]
    possiblepoints += checktwoadj(turn)[0] + checktwoadj(otherplayer(turn))[0]
    possiblepoints += checkthreeadj(turn)[0] + checkthreeadj(otherplayer(turn))[0]
    possiblepoints = list(set(possiblepoints))  # avoid repeats

    # after adding in all the possible points

    bestscore = []
    bestscore.append(checkownadj(turn)[1])
    bestscore.append(checkownadj(otherplayer(turn))[1])
    bestscore.append(checktwoadj(turn)[1])
    bestscore.append(checktwoadj(otherplayer(turn))[1])
    bestscore.append(checkthreeadj(turn)[1])
    bestscore.append(checkthreeadj(otherplayer(turn))[1])

    # check the best score for each node
    pointsheet = []

    for point in possiblepoints:
        pointscore = []
        pointscore.append(checkadjtilescore(turn, point))
        pointscore.append(checkadjtilescore(otherplayer(turn), point))
        pointscore.append(checktwoadjtilescore(turn, point))
        pointscore.append(checktwoadjtilescore(otherplayer(turn), point))
        pointscore.append(checkthreeadjtilescore(turn, point))
        pointscore.append(checkthreeadjtilescore(otherplayer(turn), point))

        templst = [pointscore[z] * AIweight[turn - 1][z] / bestscore[z] for z in range(len(pointscore))]
        pointsheet.append(sum(templst))

    theindex = 0
    maxpointsheet = 0
    for element in range(len(pointsheet)):
        if pointsheet[element] > maxpointsheet:
            theindex = element
            maxpointsheet = pointsheet[element]

    # saving the previous move
    point = possiblepoints[theindex]
    pointscore = []
    pointscore.append(checkadjtilescore(turn, point))
    pointscore.append(checkadjtilescore(otherplayer(turn), point))
    pointscore.append(checktwoadjtilescore(turn, point))
    pointscore.append(checktwoadjtilescore(otherplayer(turn), point))
    pointscore.append(checkthreeadjtilescore(turn, point))
    pointscore.append(checkthreeadjtilescore(otherplayer(turn), point))

    previousmove[turn - 1] = [pointscore[z] * AIweight[turn - 1][z] / bestscore[z] for z in range(len(pointscore))]

    return possiblepoints[theindex]


# End of Tier 0

# Tier negative (pure random)

def tier_negative():
    x, y = random.randint(0, boardsize - 1), random.randint(0, boardsize - 1)
    while game[x][y] != 0:
        x, y = random.randint(0, boardsize - 1), random.randint(0, boardsize - 1)
    print("random")
    return x, y


# End of Tier negative

def checkwin(turn):
    for x in range(0, boardsize):
        for y in range(0, boardsize):
            if game[x][y] == turn:
                for h in [4, -4]:
                    if boardsize - 1 >= x + h >= 0 and game[x + h][y] == turn:
                        for z in range(0, h, h // 4):
                            if game[x + z][y] != turn:
                                break
                            if z == h - 1:
                                return True
                    if boardsize - 1 >= y + h >= 0 and game[x][y + h] == turn:
                        for z in range(0, h, h // 4):
                            if game[x][y + z] != turn:
                                break
                            if z == h - 1:
                                return True
                    if boardsize - 1 >= y + h >= 0 and boardsize - 1 >= x + h >= 0 and game[x + h][y + h] == turn:
                        for z in range(0, h, h // 4):
                            if game[x + z][y + z] != turn:
                                break
                            if z == h - 1:
                                return True
                    if boardsize - 1 >= y - h >= 0 and boardsize - 1 >= x + h >= 0 and game[x + h][
                                y - h] == turn:
                        for z in range(0, h, h // 4):
                            if game[x + z][y - z] != turn:
                                break
                            if z == h - 1:
                                return True
    return False


def AIturn(turn):
    global tier1_used
    if max([max(x) for x in game]) == 0:  # if is it first move
        return boardsize // 2, boardsize // 2
    elif checksurewin(turn):  # if can win at next move
        b = checksurewin(turn)
        # if tier1_used == True:
        #     tier1_learning(otherplayer(turn), b, 2)
        #     print("it learnt abit")
        #     tier1_used = False

        winningmechanics(turn)
        print("checksurewin")
        return b
    elif checksurewin(otherplayer(turn)):  # check if opponent can win next turn and tries to block
        b = checksurewin(otherplayer(turn))

        # if tier1_used == True:
        #     tier1_learning(otherplayer(turn), b, 3)
        #     print("it learnt alot")
        #     tier1_used = False

        winningmechanics(otherplayer(turn))
        losingmechanics(turn, b)
        print("checksurewinopponent")
        return b
    elif createsurewin(turn):  # check if can create four in a row, a case to win on the next turn
        winningmechanics(turn)
        b = createsurewin(turn)
        # if tier1_used == True:
        #     tier1_learning(otherplayer(turn), b, 2)
        #     print("it learnt alot more")
        #     tier1_used = False

        print("createsurewin")
        return b

    elif forcemovechecker(turn):
        b = forcemovechecker(turn)

        print("win in 2")
        return b

    elif createsurewin(otherplayer(turn)):
        b = createsurewin(otherplayer(turn))

        print("stopenemycreatesurewin")
        return b


    elif forcemovechecker(otherplayer(turn)):
        b = forcemovechecker(otherplayer(turn))

        print("prevent win in 2")
        return b

    elif setupmove(turn):
        b = setupmove(turn)

        print("win in 3")
        return b

    elif setupmove(otherplayer(turn)):
        b = setupmove(otherplayer(turn))

        print("block win in 3")
        return b
    else:  # goes into neural network

        if turn == 1:
            move = gradingdecision(turn)
            tier1_learning(turn, move, 0)
            tier1_used = True
            return move

        elif turn == 2:
            tier1_used = False
            return tier0_decision(turn)


def startgame():
    global game
    global tier1_used
    global tier1_records
    global tier1_history
    global tier1_history_scores
    global lastmove
    global first
    lastmove = False
    tier1_history = []
    tier1_history_scores = []
    tier1_records = []

    game = []
    for z in range(0, boardsize):
        game.append([0] * boardsize)

    turn = 1
    if first == 1:
        turn = 2

    while min([min(x) for x in game]) == 0:
        printboard()

        print("Player", turn, "'s turn to move")
        if turn == 2:
            if playerplaying == 1:
                st = input("Input by coordinates in x,y")
                lt = [int(x) for x in st.split(",")]
            else:
                lt = list(x + 1 for x in list(AIturn(turn)))
                print("AI's move:", lt)
        elif turn == 1:
            lt = list(x + 1 for x in list(AIturn(turn)))
            print("AI's move:", lt)

        if game[lt[0] - 1][lt[1] - 1] == 0:
            game[lt[0] - 1][lt[1] - 1] = turn
            lastmove = (lt[0] - 1, lt[1] - 1)

            # if tier1_used == True:
            #     tier1_learning(turn,(lt[0]-1,lt[1]-1) , 1)
            #     print("it learnt")
            #     tier1_used = False

            if checkwin(turn):
                losingmechanics(otherplayer(turn), (lt[0] - 1, lt[0] - 1))
                WINRATIO[turn - 1] += 1
                printboard()

                if turn == 2:
                    tier1_learning(turn, (0, 0), 3)
                    print("learning to win more")
                elif turn == 1:
                    tier1_learning(turn, (0, 0), 2)
                    print("learning to make less mistakes")

                with open('AIweight.txt', 'wb') as f:
                    pickle.dump(AIweight[0], f)
                    pickle.dump(AIweight[1], f)
                    pickle.dump(tier1_nodes_weight, f)
                    pickle.dump(tier1_nodes, f)
                print("Player", turn, "wins")
                break
            # print("Sure win:", checksurewin(turn))
            if turn >= 2:
                turn = 1
            else:
                turn += 1
                # print("Create sure win:", createsurewin(turn))

        else:
            print("The spot is already taken, pick another!")
    else:
        printboard()
        with open('AIweight.txt', 'wb') as f:
            pickle.dump(AIweight[0], f)
            pickle.dump(AIweight[1], f)
            pickle.dump(tier1_nodes_weight, f)
            pickle.dump(tier1_nodes, f)
            pickle.dump(WINRATIO, f)

        print("Its a TIE!")


# while 1:
#     startgame()
# #     print(AIweight)
while 1:
    startgame()
    print(tier1_nodes_weight)
    print(tier1_nodes)
    print(AIweight[0])
    print(WINRATIO)

startgame()
print(GRADING)
print(AIweight[0])
print(AIweight[1])
print(WINRATIO)

# print(AIweight[1])
