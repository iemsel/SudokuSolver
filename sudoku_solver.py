def find_empty(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None

def valid(board, num, pos):

    row, col = pos

    for i in range(9):
        if board[row][i] == num and i != col:
            return False

    for i in range(9):
        if board[i][col] == num and i != row:
            return False

    box_x = col // 3
    box_y = row // 3

    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if board[i][j] == num and (i, j) != pos:
                return False

    return True

def solve(board):

    empty = find_empty(board)

    if not empty:
        return True

    row, col = empty

    for num in range(1,10):

        if valid(board, num, (row,col)):

            board[row][col] = num

            if solve(board):
                return True

            board[row][col] = 0

    return False