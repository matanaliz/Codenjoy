import websocket
import re
import random

sign_to_digit = {
    '2': 2,
    '4': 4,
    '8': 8,
    'A': 16,
    'B': 32,
    'C': 64,
    'D': 128,
    'E': 256,
    'F': 512,
    'G': 1024,
    'H': 2048,
    'I': 4096,
    ' ': 0
}

actions = []
#board dimention
dim = 5


def print_board(data):
    print "HELLO BOARD\n",
    for row in data:
        print row


def parse_board(data):
    board = [[0] * dim for i in range(dim)]
    for j in range(dim):
        for i in range(dim):
            board[j][i] = int(sign_to_digit[data[i + (j * dim)]])

    return board


def count_free_space(data):
    count = 0
    for row in data:
        count += row.count(0)

    return count


def stuck_row_left(row):
    score = 0
    new_row = [0 for i in range(dim)]

    #move all left
    stucked_row = []
    for i in range(dim):
        if row[i] != 0:
            stucked_row.append(row[i])
    append_list = [0 for i in range(dim - len(stucked_row))]
    stucked_row.extend(append_list)

    for i in range(dim - 1):
        if stucked_row[i] == stucked_row[i + 1]:
            #Copying before stuck
            for j in range(i):
                new_row[j] = stucked_row[j]

            #Stucking
            new_row[i] = stucked_row[i] + stucked_row[i + 1]
            #Adding score
            score += stucked_row[i] ** 2

            #Copying after suck
            for j in range(i + 1, dim - 1):
                new_row[j] = stucked_row[j + 1]

            #Adding zero in the end
            new_row[dim - 1] = 0
            break
    else:
        #We cannot stuck any numbers
        new_row = stucked_row

    return new_row, score


def fill_random(data):
    count = 3
    free = count_free_space(data)

    if count >= free:
        return False

    while count > 0:
        for row in data:
            for i in range(dim):
                if row[i] == 0:
                    if random.choice([0, 2]) > 0:
                        (row[i], count) = (2, count - 1)
                    else:
                        (row[i], count) = (0, count)
    return True


def move_left(data, deep=4):
    new_board = [[0] * dim for i in range(dim)]
    total_score = 0

    for row_index in range(len(data)):
        row_result = stuck_row_left(data[row_index])
        new_board[row_index] = row_result[0]
        total_score += row_result[1]

    win = fill_random(new_board)

    if not win:
        total_score = 0

    if deep > 0 and win:
        #It's 5 A.M. I'm doing it in stupid way

        board_down = zip(*new_board[::-1])
        board_right = zip(*board_down[::-1])
        board_up = zip(*board_right[::-1])

        dt = {
            move_left(new_board, deep - 1)[1]: "LEFT",
            move_left(board_right, deep - 1)[1]: "RIGHT",
            move_left(board_up, deep - 1)[1]: "UP",
            move_left(board_down, deep - 1)[1]: "DOWN"
        }

        total_score += max(dt.keys())

    return new_board, total_score


import logging
logger = logging.getLogger('2048')
hdlr = logging.FileHandler("2048.log")
formatter = logging.Formatter('%(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

moves = 0
game_score = 0
game_number = 0


def on_message(ws, message):
    global moves
    global game_score
    global game_number
    global logger

    board_left = parse_board(re.match(r"^board=(.*)$", message).group(1))
    board_down = zip(*board_left[::-1])
    board_right = zip(*board_down[::-1])
    board_up = zip(*board_right[::-1])

    if count_free_space(board_left) == 0:
        logger.info("Game: " + str(game_number))
        logger.info("Score: " + str(float(game_score / 100)) + " Moves: " + str(moves) + " PPM: " + str(float(game_score / (moves * 100))))

        logger.info("Incoming new board")
        moves = 0
        game_score = 0
        game_number += 1

    dt = {
        move_left(board_left)[1]: "LEFT",
        move_left(board_right)[1]: "RIGHT",
        move_left(board_up)[1]: "UP",
        move_left(board_down)[1]: "DOWN"
    }

    ws.send(dt[max(dt.keys())])
    moves += 1
    game_score += max(dt.keys())


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


if __name__ == "__main__":
    #websocket.enableTrace(True)


    logger.info("STARTED deep = 4, score pow 2, mod 100")

    ws = websocket.WebSocketApp("ws://tetrisj.jvmhost.net:12270/codenjoy-contest/ws?user=Player1",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()
