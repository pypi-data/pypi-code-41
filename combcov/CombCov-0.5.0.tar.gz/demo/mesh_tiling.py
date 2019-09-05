import logging
from collections import namedtuple
from itertools import chain, combinations, product

from permuta import Av, MeshPatt, Perm, PermSet
from permuta.misc import flatten, ordered_set_partitions

from combcov import CombCov, Rule

logger = logging.getLogger("MeshTiling")


class MockAvCoPatts():
    def __init__(self, av_patts, co_patts):
        self.base_perm_set = Av(av_patts)

        if isinstance(co_patts, (Perm, MeshPatt)):
            self.filter = lambda perm: perm.contains(co_patts)
        elif all(isinstance(patt, (Perm, MeshPatt)) for patt in co_patts):
            self.filter = lambda perm: any(perm.contains(patt)
                                           for patt in co_patts)
        else:
            raise ValueError("Variable 'co_patts' not as expected: "
                             "'{}'".format(co_patts))

    def of_length(self, size):
        return filter(self.filter, self.base_perm_set.of_length(size))


class Cell(namedtuple('Cell', ['obstructions', 'requirements'])):
    __slots__ = ()

    def is_empty(self):
        return self.obstructions == frozenset({Perm((0,))})

    def is_point(self):
        return self.obstructions == frozenset({Perm((0, 1)), Perm((1, 0))}) \
               and self.requirements == frozenset({Perm((0,))})

    def is_anything(self):
        return self.obstructions == frozenset() \
               and self.requirements == frozenset()

    def is_avoiding(self):
        return len(self.obstructions) > 0

    def is_containing(self):
        return len(self.requirements) > 0

    def flip(self):
        return Cell(self.requirements, self.obstructions)

    def get_permclass(self):
        if self.is_empty():
            return Av(Perm((0,)))
        elif self.is_point():
            return PermSet(1)
        elif self.is_anything():
            return PermSet()
        elif self.is_avoiding() and not self.is_containing():
            return Av(self.obstructions)
        else:
            return MockAvCoPatts(self.obstructions, self.requirements)

    def __repr__(self):
        if self.is_empty():
            return " "
        elif self.is_point():
            return "o"
        elif self.is_anything():
            return "S"
        elif self.is_avoiding() and not self.is_containing():
            return "Av({})".format(
                ", ".join(repr(patt) for patt in self.obstructions))
        elif self.is_containing() and not self.is_avoiding():
            return "Co({})".format(
                ", ".join(repr(patt) for patt in self.requirements))
        else:
            return "Av({}) and Co({})".format(
                ", ".join(repr(patt) for patt in self.obstructions),
                ", ".join(repr(patt) for patt in self.requirements))

    def __str__(self):
        # ToDo: Instead return multi-line mesh patterns
        return repr(self)


class MeshTiling(Rule):
    empty_cell = Cell(frozenset({Perm((0,))}), frozenset())
    point_cell = Cell(frozenset({Perm((0, 1)), Perm((1, 0))}),
                      frozenset({Perm((0,))}))
    anything_cell = Cell(frozenset(), frozenset())

    def __init__(self, cells={}):
        # Sane and fast-running default values, overwrite as needed
        self.MAX_COLUMN_DIMENSION = 2
        self.MAX_ROW_DIMENSION = 2
        self.MAX_ACTIVE_CELLS = 3

        # Clean empty rows and columns and save cells with shifted coordinates
        Xs, Ys = set(x for (x, y) in cells), set(y for (x, y) in cells)
        self.columns, self.rows = max(1, len(Xs)), max(1, len(Ys))

        compression_dict = {
            'col': {old: new for (new, old) in enumerate(sorted(Xs))},
            'row': {old: new for (new, old) in enumerate(sorted(Ys))}
        }

        self.cells = {}
        self.tiling = [self.empty_cell] * (self.columns * self.rows)
        for (old_col, old_row), cell in cells.items():
            col = compression_dict['col'][old_col]
            row = compression_dict['row'][old_row]
            self.cells[(col, row)] = cell
            self.tiling[
                self.convert_coordinates_to_linear_number(col, row)] = cell

    # Linear number = (column, row)
    #   -----------------------------------
    #  | 3 = (0,1) | 4 = (1,1) | 5 = (2,1) |
    #  |-----------+-----------+-----------|
    #  | 0 = (0,0) | 1 = (1,0) | 2 = (2,0) |
    #   -----------------------------------
    def convert_linear_number_to_coordinates(self, number):
        if number < 0 or number >= self.columns * self.rows:
            raise IndexError
        else:
            col = number % self.columns
            row = number // self.columns
            return (col, row)

    def get_obstructions_lists(self):
        for cell in self.cells.values():
            if not cell.is_empty() and not cell.is_point():
                yield cell.obstructions

    def get_requirements_lists(self):
        for cell in self.cells.values():
            if not (cell.is_empty() or cell.is_point() or cell.is_anything()):
                yield cell.requirements

    def convert_coordinates_to_linear_number(self, col, row):
        if col < 0 or col >= self.columns or row < 0 or row >= self.rows:
            raise IndexError
        else:
            return row * self.columns + col

    def get_elmnts(self, of_size):
        # Return permutations of length 'of_size' on a MeshTiling like this:
        #
        #      ------------------------
        #     |          | o |         |
        #     |----------+---+---------|
        #     | Av(31#2) |   | Av(1#2) |
        #      ------------------------
        #
        # The following code was shamelessly ported and adapted from
        # PermutaTriangle/grids repo, grids/Tilings.py file

        w = self.columns
        h = self.rows

        tiling = self.tiling

        def permute(arr, perm):
            res = [None] * len(arr)
            for i in range(len(arr)):
                res[i] = arr[perm[i]]
            return res

        def count_assignments(at, left):
            if at == len(self):
                # base case in recursion
                if left == 0:
                    yield []
            else:
                if tiling[at].is_point():
                    # one point in cell
                    if left > 0:
                        for ass in count_assignments(at + 1, left - 1):
                            yield [1] + ass
                elif tiling[at].is_empty():
                    # no point in cell
                    for ass in count_assignments(at + 1, left):
                        yield [0] + ass
                else:
                    for cur in range(left + 1):
                        for ass in count_assignments(at + 1, left - cur):
                            yield [cur] + ass

        elmnts_list = []
        for count_ass in count_assignments(0, of_size):
            cntz = [[0 for j in range(w)] for i in range(h)]

            for i, k in enumerate(count_ass):
                (col, row) = self.convert_linear_number_to_coordinates(i)
                cntz[row][col] = k

            rowcnt = [sum(cntz[ro][co] for co in range(w)) for ro in range(h)]
            colcnt = [sum(cntz[ro][co] for ro in range(h)) for co in range(w)]

            for colpart in product(*[
                    ordered_set_partitions(
                        range(colcnt[col]), [
                            cntz[row][col] for row in range(h)
                        ]
                    ) for col in range(w)]):
                scolpart = [[sorted(colpart[i][j]) for j in range(h)] for i in
                            range(w)]
                for rowpart in product(*[
                    ordered_set_partitions(range(rowcnt[row]),
                                           [cntz[row][col] for col in
                                            range(w)]) for row in range(h)]):
                    srowpart = [[sorted(rowpart[i][j]) for j in range(w)] for i
                                in range(h)]
                    for perm_ass in product(
                            *[s.get_permclass().of_length(cnt) for
                              cnt, s in zip(count_ass, tiling)]):
                        arr = [[[] for j in range(w)] for i in range(h)]

                        for i, perm in enumerate(perm_ass):
                            (col,
                             row) = self.convert_linear_number_to_coordinates(
                                i)
                            arr[row][col] = perm

                        res = [[None] * colcnt[col] for col in range(w)]

                        cumul = 0
                        for row in range(h):
                            for col in range(w):
                                for idx, val in zip(scolpart[col][row],
                                                    permute(srowpart[row][col],
                                                            arr[row][col])):
                                    res[col][idx] = cumul + val
                            cumul += rowcnt[row]
                        elmnts_list.append(Perm(flatten(res)))

        return elmnts_list

    def get_subrules(self):
        # Subrules are MeshTilings of sizes ranging from 1 x 1 to 3 x 3
        # (adjustable with self.MAX_COLUMN_DIMENSION and self.MAX_ROW_DIMENSION
        # variables). Each cell contains a mix of requirements (Perms) and
        # obstructions (MeshPatts) where the obstructions are sub mesh patterns
        # of any of the obstructions in the root object.

        logger.info(
            "About to generate subrules with up to {} active cells "
            "and dimensions up to {}x{}".format(
                self.MAX_ACTIVE_CELLS, self.MAX_COLUMN_DIMENSION,
                self.MAX_ROW_DIMENSION
            )
        )

        perms, mesh_patts = set(), set()
        for obstructions_list in chain(
                self.get_obstructions_lists(), self.get_requirements_lists()):
            for obstruction in obstructions_list:
                n = len(obstruction)
                if isinstance(obstruction, Perm):
                    for l in range(n):
                        perms.update(
                            Perm.to_standard((obstruction[i] for i in indices))
                            for indices in combinations(range(n), l + 1)
                        )
                elif isinstance(obstruction, MeshPatt):
                    for l in range(n):
                        for indices in combinations(range(n), l + 1):
                            mesh_patt = obstruction.sub_mesh_pattern(indices)
                            if len(mesh_patt.shading) > 0:
                                mesh_patts.add(mesh_patt)
                            else:
                                # A mesh patt without shading is just a perm
                                perms.add(mesh_patt.pattern)
                else:
                    raise ValueError(
                        "[ERROR] obstruction '{}' is neither a MeshPatt "
                        "or Perm!".format(obstruction))

        origin_cell = self.tiling[0]
        cell_choices = {self.point_cell, self.anything_cell}
        cell_choices.add(
            origin_cell if origin_cell.is_avoiding() else origin_cell.flip()
        )

        for patt in MeshTiling.clean_patts(perms, mesh_patts):
            av_cell = Cell(frozenset({patt}), frozenset())
            if not av_cell.is_empty():
                cell_choices.add(av_cell)

        logger.info("{} cell choices: {}".format(
            len(cell_choices), cell_choices))

        subrules = 1
        yield MeshTiling()  # always include the empty rule

        for (dim_col, dim_row) in product(
                range(1, self.columns + self.MAX_COLUMN_DIMENSION),
                range(1, self.rows + self.MAX_ROW_DIMENSION)
        ):

            nr_of_cells = dim_col * dim_row
            for how_many_active_cells in range(min(dim_col, dim_row),
                                               self.MAX_ACTIVE_CELLS + 1):
                for active_cells in product(
                        cell_choices, repeat=how_many_active_cells):
                    for combination in combinations(
                            range(nr_of_cells), how_many_active_cells):
                        cells = {}
                        for i, cell_index in enumerate(combination):
                            c = cell_index % dim_col
                            r = cell_index // dim_col
                            cells[(c, r)] = active_cells[i]

                        subrules += 1
                        yield MeshTiling(cells)

        logger.info("Generated in total {} subrules ".format(subrules))

    def get_dimension(self):
        return (self.columns, self.rows)

    def _key(self):
        return frozenset(self.cells.items()),

    def __len__(self):
        return self.columns * self.rows

    def __str__(self):
        # ToDo: Implement proper multi-line Cell.__str__() and use instead
        tiling_representation = [repr(cell) for cell in self.tiling]

        col_widths = [
            max(len(tiling_representation[
                        self.convert_coordinates_to_linear_number(col, row)
                    ]) for row in range(self.rows)) + 2 for col in
            range(self.columns)
        ]

        top_bottom_lines = " " + "-".join("-" * l for l in col_widths) + " \n"
        middle_lines = "|" + "+".join("-" * l for l in col_widths) + "|\n"

        cell_lines = ["|" + "|".join("{:^{}}".format(
            tiling_representation[
                self.convert_coordinates_to_linear_number(col, row)],
            col_widths[col]) for col in range(self.columns)
        ) + "|\n" for row in reversed(range(self.rows))]

        return "\n" + \
               top_bottom_lines + \
               middle_lines.join(line for line in cell_lines) + \
               top_bottom_lines

    @staticmethod
    def clean_patts(perms, mesh_patts):
        unique_patts = dict()
        for patt in chain(sorted(perms), sorted(mesh_patts)):
            perms_from_cell = set()
            cell = Cell(frozenset({patt}), frozenset())
            for length in range(min(7, 2 * len(patt) + 1)):
                perms_from_cell.update(cell.get_permclass().of_length(length))

            perms_from_cell = frozenset(perms_from_cell)
            if perms_from_cell not in unique_patts:
                unique_patts[perms_from_cell] = patt

        return set(unique_patts.values())


def main():
    logging.getLogger().setLevel(logging.INFO)

    perm = Perm((2, 0, 1))
    mesh_patt = MeshPatt(perm, ((2, 0), (2, 1), (2, 2), (2, 3)))
    mesh_tiling = MeshTiling({
        (0, 0): Cell(
            obstructions=frozenset({mesh_patt}),
            requirements=frozenset()
        ),
    })
    mesh_tiling.MAX_COLUMN_DIMENSION = 3
    mesh_tiling.MAX_ROW_DIMENSION = 2
    mesh_tiling.MAX_ACTIVE_CELLS = 3

    max_elmnt_size = 5
    comb_cov = CombCov(mesh_tiling, max_elmnt_size)
    comb_cov.print_outcome()


if __name__ == "__main__":
    main()
