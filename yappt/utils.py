"""Misc util functions."""
from typing import Tuple

def explode_layout_string(layout: str) -> Tuple:
    # here we explode the string into a tuple of tuples like so:
    # '1-2-3-2-1' -> ((0),(0,0),(0,0,0),(0,0),(0)) where 0 is actually `False`
    assert isinstance(layout, str)
    layout_flat = tuple(map(int, layout.split('-')))

    layout_nested: list = []
    for item in layout_flat:
        layout_nested.append(tuple([False for _ in range(item)]))

    return tuple(layout_nested)

def create_active_cells(layout: Tuple, actives: Tuple):
    # here we take the exploded tuple of tuple layout field and turn those cells which are active to True:
    # so  ((0),(0,0),(0,0,0),(0,0),(0)) -> ((0),(0,0),(1,0,1),(0,0),(0)) give the actives of (3,5)

    counter = 0
    active_cells = []
    for row in layout:
        current_row = []
        for _ in row:
            if counter in actives:
                current_row.append(True)
            else:
                current_row.append(False)
            counter += 1
        row_tup = tuple(current_row)
        active_cells.append(row_tup)
    return tuple(active_cells)
