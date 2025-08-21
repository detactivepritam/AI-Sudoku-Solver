from collections import defaultdict
from typing import List, Set, Dict, Tuple, Optional

Digits = set("123456789")

def cross(A: str, B: str) -> List[str]:
    return [a + b for a in A for b in B]

ROWS = "ABCDEFGHI"
COLS = "123456789"
CELLS = cross(ROWS, COLS)

ROW_UNITS = [cross(r, COLS) for r in ROWS]
COL_UNITS = [cross(ROWS, c) for c in COLS]
BOX_UNITS = [cross(rs, cs) for rs in ("ABC", "DEF", "GHI") for cs in ("123", "456", "789")]
UNITS = {s: [u for u in (ROW_UNITS + COL_UNITS + BOX_UNITS) if s in u] for s in CELLS}
PEERS = {s: set(sum(UNITS[s], [])) - {s} for s in CELLS}

def chunk(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i+n]

class SudokuSolver:
    def __init__(self, grid):
        self.values: Dict[str, Set[str]] = {s: set(Digits) for s in CELLS}
        if isinstance(grid, str):
            grid = grid.strip()
            if len(grid) != 81:
                raise ValueError("Grid string must be exactly 81 characters.")
            for s, ch in zip(CELLS, grid):
                if ch in Digits:
                    if not self.assign(s, ch):
                        raise ValueError("Invalid puzzle (contradiction on load).")
        elif isinstance(grid, list):
            flat = "".join(str(x) for row in grid for x in row)
            flat = flat.replace("0", ".")
            self.__init__(flat)
        else:
            raise TypeError("Grid must be an 81-char string or a 9x9 list.")

    def assign(self, cell: str, d: str) -> bool:
        other = self.values[cell] - {d}
        return all(self.eliminate(cell, d2) for d2 in list(other))

    def eliminate(self, cell: str, d: str) -> bool:
        if d not in self.values[cell]:
            return True
        self.values[cell].remove(d)
        if len(self.values[cell]) == 0:
            return False
        if len(self.values[cell]) == 1:
            d2 = next(iter(self.values[cell]))
            for p in PEERS[cell]:
                if not self.eliminate(p, d2):
                    return False
        for unit in UNITS[cell]:
            places = [s for s in unit if d in self.values[s]]
            if len(places) == 0:
                return False
            if len(places) == 1:
                if not self.assign(places[0], d):
                    return False
        return True

    def hidden_singles(self) -> bool:
        changed = False
        for unit in ROW_UNITS + COL_UNITS + BOX_UNITS:
            for d in Digits:
                places = [s for s in unit if d in self.values[s]]
                if len(places) == 1:
                    if self.assign(places[0], d) is False:
                        return False
                    changed = True
        return changed

    def naked_pairs(self) -> bool:
        changed = False
        for unit in ROW_UNITS + COL_UNITS + BOX_UNITS:
            pairs = defaultdict(list)
            for s in unit:
                if len(self.values[s]) == 2:
                    pairs[frozenset(self.values[s])].append(s)
            for candset, cells in pairs.items():
                if len(cells) == 2:
                    for s in unit:
                        if s not in cells and self.values[s].intersection(candset):
                            self.values[s] -= candset
                            if len(self.values[s]) == 0:
                                return False
                            changed = True
        return changed

    def pointing_pairs(self) -> bool:
        changed = False
        row_map = {r: [r + c for c in COLS] for r in ROWS}
        col_map = {c: [r + c for r in ROWS] for c in COLS}
        for box in BOX_UNITS:
            for d in Digits:
                pos = [s for s in box if d in self.values[s]]
                if len(pos) < 2:
                    continue
                rows_in = {s[0] for s in pos}
                cols_in = {s[1] for s in pos}
                if len(rows_in) == 1:
                    r = next(iter(rows_in))
                    for s in row_map[r]:
                        if s not in box and d in self.values[s]:
                            self.values[s].discard(d)
                            changed = True
                if len(cols_in) == 1:
                    c = next(iter(cols_in))
                    for s in col_map[c]:
                        if s not in box and d in self.values[s]:
                            self.values[s].discard(d)
                            changed = True
        return changed

    def propagate_all(self) -> bool:
        stalled = False
        while not stalled:
            snapshot = self._snapshot()
            if self.hidden_singles() is False:
                return False
            res = self.naked_pairs()
            if res is False:
                return False
            changed_pp = self.pointing_pairs()
            if changed_pp is False:
                return False
            stalled = (snapshot == self._snapshot())
        return True

    def _snapshot(self) -> Tuple[Tuple[str, Tuple[str, ...]], ...]:
        return tuple(sorted((s, tuple(sorted(self.values[s]))) for s in CELLS))

    def is_solved(self) -> bool:
        return all(len(self.values[s]) == 1 for s in CELLS) and self._valid_grid()

    def _valid_grid(self) -> bool:
        def unit_ok(unit):
            vals = [next(iter(self.values[s])) for s in unit if len(self.values[s]) == 1]
            return len(vals) == len(set(vals))
        return all(unit_ok(u) for u in ROW_UNITS + COL_UNITS + BOX_UNITS)

    def validate_solution(self) -> bool:
        """Check if the current grid is a valid solved Sudoku."""
        if not self.is_solved():
            return False

        def valid_group(group):
            vals = [next(iter(self.values[s])) for s in group]
            return set(vals) == set("123456789")

        for unit in ROW_UNITS + COL_UNITS + BOX_UNITS:
            if not valid_group(unit):
                return False
        return True

    def search(self) -> Optional[Dict[str, Set[str]]]:
        if not self.propagate_all():
            return None
        if self.is_solved():
            return self.values
        unsolved = [s for s in CELLS if len(self.values[s]) > 1]
        cell = min(unsolved, key=lambda s: len(self.values[s]))
        def lcv_score(d):
            score = 0
            for p in PEERS[cell]:
                if d in self.values[p]:
                    score += 1
            return score
        candidates = sorted(self.values[cell], key=lcv_score)
        snapshot = self._deepcopy()
        for d in candidates:
            self._restore(snapshot)
            trial = self._deepcopy()
            if self.assign(cell, d) and self.search() is not None:
                return self.values
            self._restore(trial)
        return None

    def solve(self) -> str:
        if self.is_solved():
            if self.validate_solution():
                return "Sudoku is already solved and valid:\n\n" + self.__str__()
            else:
                return "Sudoku grid is filled but invalid:\n\n" + self.__str__()
        if self.search() is None:
            raise ValueError("No solution found (or puzzle invalid).")

        return "Solved Sudoku:\n\n" + self.__str__()

    def _deepcopy(self) -> Dict[str, Set[str]]:
        return {k: set(v) for k, v in self.values.items()}

    def _restore(self, snapshot: Dict[str, Set[str]]):
        self.values = {k: set(v) for k, v in snapshot.items()}

    def as_string(self) -> str:
        out = []
        for s in CELLS:
            if len(self.values[s]) == 1:
                out.append(next(iter(self.values[s])))
            else:
                out.append(".")
        return "".join(out)

    def __str__(self) -> str:
        width = 1 + max(len(self.values[s]) for s in CELLS)
        line = "+".join(["-" * (width * 3)] * 3)
        rows = []
        for r in ROWS:
            row = ""
            for c in COLS:
                s = r + c
                val = next(iter(self.values[s])) if len(self.values[s]) == 1 else "".join(sorted(self.values[s]))
                row += val.center(width)
                if c in "36":
                    row += "|"
            rows.append(row)
            if r in "CF":
                rows.append(line)
        return "\n".join(rows)


if __name__ == "__main__":
    hard = "000000907000420180000705026100904000050000040000507009920108000034059000507000000"
    s = SudokuSolver(hard)
    print("Input:")
    print(s)
    print("\nSolving...")
    print(s.solve())
    print("\nAs 81-char string:")
    print(s.as_string())