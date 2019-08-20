import numpy as np


def draw(size=9):
    s = size
    _board = None
    while _board is None:
        _board = _board_randomize(s)
    return _board


def _board_randomize(s):
    size = s
    try:
        root = int(np.sqrt(size))
        assert root == np.sqrt(size)
    except AssertionError as e:
        print("Size must be squarable")
        exit()
    else:
        _board = np.zeros(size ** 2, dtype=np.int32).reshape(size, size)
        numbers = np.arange(1, size + 1, 1)

        for row in range(size):
            for column in range(size):
                np.random.shuffle(numbers)
                block_row, block_column = row - row % root, column - column % root
                _block = _board[block_row:block_row + root, block_column:block_column + root]
                _row = _board[row]
                _column = _board[:, [column]]

                for n in numbers:
                    if (n not in _row
                            and n not in _column
                            and n not in _block
                    ):
                        _board[row][column] = n
                        break
                else:
                    return None
        return _board

