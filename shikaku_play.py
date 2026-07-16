#!/usr/bin/env python3
"""Interactive Shikaku player: a Tkinter desktop app.

Drag across cells to place a rectangle; right-click a rectangle to
remove it. Rectangles are colored green once they cover exactly one
clue whose value matches the rectangle's area, orange otherwise.
"""

import sys
import random
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from shikaku_common import Clue, Puzzle, Rect
from shikaku_gen import generate_puzzle

CELL_SIZE = 40
PAD = 12

COLOR_GRID_LINE = "#888888"
COLOR_CLUE_TEXT = "#111111"
COLOR_VALID_FILL = "#b7e4c7"
COLOR_INVALID_FILL = "#f6b8a2"
COLOR_VALID_OUTLINE = "#2f9e44"
COLOR_INVALID_OUTLINE = "#d9480f"
COLOR_DRAG_OUTLINE = "#1c7ed6"
COLOR_WITNESS_OUTLINE = "#9775fa"


def rects_overlap(a: Rect, b: Rect) -> bool:
    return not (
        a.x + a.w <= b.x
        or b.x + b.w <= a.x
        or a.y + a.h <= b.y
        or b.y + b.h <= a.y
    )


def clues_in_rect(rect: Rect, clues):
    return [c for c in clues if rect.contains(c.row, c.col)]


def rect_is_valid(rect: Rect, clues) -> bool:
    contained = clues_in_rect(rect, clues)
    return len(contained) == 1 and contained[0].value == rect.area


class NewPuzzleDialog(simpledialog.Dialog):
    def body(self, master):
        self.title("New Puzzle")
        fields = [
            ("Width", "width", "10"),
            ("Height", "height", "10"),
            ("Min area", "min_area", "2"),
            ("Max area", "max_area", "10"),
            ("Split probability", "split_prob", "0.3"),
            ("Seed (blank = random)", "seed", ""),
        ]
        self.vars = {}
        for i, (label, key, default) in enumerate(fields):
            tk.Label(master, text=label).grid(row=i, column=0, sticky="w", padx=4, pady=2)
            var = tk.StringVar(value=default)
            tk.Entry(master, textvariable=var).grid(row=i, column=1, padx=4, pady=2)
            self.vars[key] = var
        return None

    def validate(self):
        try:
            self.width = int(self.vars["width"].get())
            self.height = int(self.vars["height"].get())
            self.min_area = int(self.vars["min_area"].get())
            self.max_area = int(self.vars["max_area"].get())
            self.split_prob = float(self.vars["split_prob"].get())
            seed_text = self.vars["seed"].get().strip()
            self.seed = int(seed_text) if seed_text else None
            if self.width < 1 or self.height < 1:
                raise ValueError("width/height must be >= 1")
            if self.min_area < 1 or self.max_area < self.min_area:
                raise ValueError("need min_area >= 1 and max_area >= min_area")
        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
            return False
        return True

    def apply(self):
        self.result = (self.width, self.height, self.min_area, self.max_area, self.split_prob, self.seed)


class ShikakuPlayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shikaku Player")

        self.puzzle: Puzzle = None
        self.placed: list[Rect] = []
        self.drag_start = None
        self.drag_current = None
        self.show_witness = tk.BooleanVar(value=False)

        toolbar = tk.Frame(root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=6, pady=6)
        tk.Button(toolbar, text="Open...", command=self.open_puzzle).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="New...", command=self.new_puzzle).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Clear", command=self.clear).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Check", command=self.check_solution).pack(side=tk.LEFT, padx=2)
        self.witness_check = tk.Checkbutton(
            toolbar, text="Show witness solution", variable=self.show_witness, command=self.redraw
        )
        self.witness_check.pack(side=tk.LEFT, padx=12)

        self.canvas = tk.Canvas(root, background="white")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<ButtonPress-3>", self.on_right_click)

        self.status_var = tk.StringVar(value="Open a puzzle file or generate a new one to begin.")
        tk.Label(root, textvariable=self.status_var, anchor="w").pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=4)

    # -- puzzle loading -------------------------------------------------

    def open_puzzle(self):
        path = filedialog.askopenfilename(
            title="Open Shikaku puzzle", filetypes=[("Shikaku puzzle", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        with open(path, encoding="utf-8") as f:
            text = f.read()
        try:
            puzzle = Puzzle.from_text(text)
        except Exception as e:
            messagebox.showerror("Failed to load puzzle", str(e))
            return
        self.load_puzzle(puzzle)

    def new_puzzle(self):
        dialog = NewPuzzleDialog(self.root)
        if dialog.result is None:
            return
        width, height, min_area, max_area, split_prob, seed = dialog.result
        rng = random.Random(seed)
        puzzle = generate_puzzle(width, height, min_area, max_area, split_prob, rng)
        self.load_puzzle(puzzle)

    def load_puzzle(self, puzzle: Puzzle):
        self.puzzle = puzzle
        self.placed = []
        self.drag_start = None
        self.drag_current = None
        width_px = PAD * 2 + puzzle.width * CELL_SIZE
        height_px = PAD * 2 + puzzle.height * CELL_SIZE
        self.canvas.config(width=width_px, height=height_px)
        self.status_var.set(f"Loaded {puzzle.width}x{puzzle.height} puzzle with {len(puzzle.clues)} clues.")
        self.redraw()

    # -- coordinate helpers -----------------------------------------------

    def cell_from_event(self, event):
        col = (event.x - PAD) // CELL_SIZE
        row = (event.y - PAD) // CELL_SIZE
        col = min(max(col, 0), self.puzzle.width - 1)
        row = min(max(row, 0), self.puzzle.height - 1)
        return row, col

    def cell_to_px(self, row, col):
        return PAD + col * CELL_SIZE, PAD + row * CELL_SIZE

    # -- mouse handlers ----------------------------------------------------

    def on_press(self, event):
        if self.puzzle is None:
            return
        self.drag_start = self.cell_from_event(event)
        self.drag_current = self.drag_start
        self.redraw()

    def on_drag(self, event):
        if self.puzzle is None or self.drag_start is None:
            return
        self.drag_current = self.cell_from_event(event)
        self.redraw()

    def on_release(self, event):
        if self.puzzle is None or self.drag_start is None:
            return
        r1, c1 = self.drag_start
        r2, c2 = self.cell_from_event(event)
        top, bottom = min(r1, r2), max(r1, r2)
        left, right = min(c1, c2), max(c1, c2)
        rect = Rect(x=left, y=top, w=right - left + 1, h=bottom - top + 1)

        self.drag_start = None
        self.drag_current = None

        if any(rects_overlap(rect, other) for other in self.placed):
            self.status_var.set("Can't place that rectangle: it overlaps one already placed.")
        else:
            self.placed.append(rect)
            self.status_var.set(f"Placed a {rect.w}x{rect.h} rectangle at row {rect.y}, col {rect.x}.")
        self.redraw()
        self.check_win_silent()

    def on_right_click(self, event):
        if self.puzzle is None:
            return
        row, col = self.cell_from_event(event)
        for rect in reversed(self.placed):
            if rect.contains(row, col):
                self.placed.remove(rect)
                self.status_var.set("Removed a rectangle.")
                self.redraw()
                return

    # -- editing actions -----------------------------------------------

    def undo(self):
        if self.placed:
            self.placed.pop()
            self.status_var.set("Undid last rectangle.")
            self.redraw()

    def clear(self):
        self.placed = []
        self.status_var.set("Cleared all placed rectangles.")
        self.redraw()

    # -- validation -------------------------------------------------------

    def check_win_silent(self):
        if self.puzzle is None:
            return
        covered = sum(r.area for r in self.placed)
        total = self.puzzle.width * self.puzzle.height
        all_valid = all(rect_is_valid(r, self.puzzle.clues) for r in self.placed)
        if covered == total and all_valid and len(self.placed) == len(self.puzzle.clues):
            self.status_var.set("Solved! Every clue matches its rectangle and the grid is fully covered.")

    def check_solution(self):
        if self.puzzle is None:
            messagebox.showinfo("Check", "No puzzle loaded.")
            return

        total = self.puzzle.width * self.puzzle.height
        covered = sum(r.area for r in self.placed)
        invalid = [r for r in self.placed if not rect_is_valid(r, self.puzzle.clues)]
        uncovered_clues = [
            c for c in self.puzzle.clues if not any(r.contains(c.row, c.col) for r in self.placed)
        ]

        if not invalid and not uncovered_clues and covered == total:
            messagebox.showinfo("Check", "Solved! Every clue matches its rectangle and the grid is fully covered.")
            return

        problems = []
        if invalid:
            problems.append(f"{len(invalid)} rectangle(s) don't match a single clue's area.")
        if uncovered_clues:
            problems.append(f"{len(uncovered_clues)} clue(s) not yet covered by any rectangle.")
        if covered < total:
            problems.append(f"{total - covered} cell(s) still uncovered.")
        messagebox.showwarning("Not solved yet", "\n".join(problems))

    # -- drawing -------------------------------------------------------

    def redraw(self):
        self.canvas.delete("all")
        if self.puzzle is None:
            return
        puzzle = self.puzzle

        if self.show_witness.get() and puzzle.solution is not None:
            for rect in puzzle.solution:
                x0, y0 = self.cell_to_px(rect.y, rect.x)
                x1, y1 = self.cell_to_px(rect.y + rect.h, rect.x + rect.w)
                self.canvas.create_rectangle(
                    x0, y0, x1, y1, outline=COLOR_WITNESS_OUTLINE, width=2, dash=(4, 3)
                )

        for rect in self.placed:
            x0, y0 = self.cell_to_px(rect.y, rect.x)
            x1, y1 = self.cell_to_px(rect.y + rect.h, rect.x + rect.w)
            valid = rect_is_valid(rect, puzzle.clues)
            fill = COLOR_VALID_FILL if valid else COLOR_INVALID_FILL
            outline = COLOR_VALID_OUTLINE if valid else COLOR_INVALID_OUTLINE
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline=outline, width=2)

        for row in range(puzzle.height + 1):
            x0, y0 = self.cell_to_px(row, 0)
            x1, _ = self.cell_to_px(row, puzzle.width)
            self.canvas.create_line(x0, y0, x1, y0, fill=COLOR_GRID_LINE)
        for col in range(puzzle.width + 1):
            x0, y0 = self.cell_to_px(0, col)
            _, y1 = self.cell_to_px(puzzle.height, col)
            self.canvas.create_line(x0, y0, x0, y1, fill=COLOR_GRID_LINE)

        for clue in puzzle.clues:
            cx, cy = self.cell_to_px(clue.row, clue.col)
            self.canvas.create_text(
                cx + CELL_SIZE / 2,
                cy + CELL_SIZE / 2,
                text=str(clue.value),
                fill=COLOR_CLUE_TEXT,
                font=("Segoe UI", 14, "bold"),
            )

        if self.drag_start is not None and self.drag_current is not None:
            r1, c1 = self.drag_start
            r2, c2 = self.drag_current
            top, bottom = min(r1, r2), max(r1, r2)
            left, right = min(c1, c2), max(c1, c2)
            x0, y0 = self.cell_to_px(top, left)
            x1, y1 = self.cell_to_px(bottom + 1, right + 1)
            self.canvas.create_rectangle(x0, y0, x1, y1, outline=COLOR_DRAG_OUTLINE, width=2, dash=(3, 2))


def main():
    root = tk.Tk()
    app = ShikakuPlayApp(root)

    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            puzzle = Puzzle.from_text(f.read())
        app.load_puzzle(puzzle)

    root.mainloop()


if __name__ == "__main__":
    main()
