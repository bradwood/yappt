"""Holds functions for processing, parsing and validating slide layouts."""
from .exceptions import LayoutError
from typing import Tuple


class Layout:
    """This class holds layout details for a slide."""
    def __init__(self, layout_str: str):
        # here we explode the string into a tuple of tuples like so:
        # '1-2-3-2-1' -> ((0),(0,0),(0,0,0),(0,0),(0)) where 0 is actually `False`
        self.layout_str = layout_str

        try:
            assert isinstance(layout_str, str)
            layout_flat = tuple(map(int, layout_str.split('-')))

            layout_nested: list = []
            for item in layout_flat:
                layout_nested.append(tuple([False for _ in range(item)]))
            self._parsed_layout = tuple(layout_nested)
        except (ValueError, AttributeError):
            le = LayoutError(f'Could not parse: \'{layout_str}\'.')
            raise le

    @property
    def row_count(self):
        """Return number of rows in layout."""
        return len(self._parsed_layout)

    @property
    def cell_count(self):
        """Return number of cells in layout."""
        cell_count = 0
        for rows in self._parsed_layout:
            cell_count += len(rows)
        return cell_count


    def active_cells(self, actives: Tuple):
        """Generate a tuple with active cells flagged as True."""
        # here we take the exploded tuple of tuple layout field and turn those cells which are active to True:
        # so  ((0),(0,0),(0,0,0),(0,0),(0)) -> ((0),(0,0),(1,0,1),(0,0),(0)) give the actives of (3,5)

        counter = 0
        active_cells = []
        for row in self._parsed_layout:
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
