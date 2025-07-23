#This takes the cell ID out of the raw JPEG file name so we can quickly list the IDs from a significant amount of images.

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def extract_segment(filename: str) -> str | None:
    """
    1) right-most 27 chars of the filename
    2) left-most 10 of those
    """
    base = os.path.basename(filename)
    if len(base) < 24:
        return None
    return base[-28:][:10]           

class SegmentExtractorApp(ttk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master, padding=10)
        master.title("Cell ID JPG Extractor")
        master.resizable(False, False)

        # Buttons
        ttk.Button(self, text="Select JPG Files", command=self.pick_files) \
            .grid(row=0, column=0, sticky="ew")

        # Results box
        self.results = tk.Text(self, width=40, height=12, wrap="none")
        self.results.grid(row=1, column=0, pady=8)
        self.results.configure(state="disabled")

        self.grid()

    def pick_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Choose JPG files",
            filetypes=[("JPEG images", "*.jpg;*.jpeg"), ("All files", "*.*")]
        )
        if not paths:
            return

        segments = []
        for p in paths:
            seg = extract_segment(p)
            if seg:
                segments.append(seg)
            else:
                messagebox.showwarning(
                    "Filename too short",
                    f"'{os.path.basename(p)}' isn’t long enough"
                )

        # Show results
        self.results.configure(state="normal")
        self.results.delete("1.0", "end")
        for s in segments:
            self.results.insert("end", s + "\n")
        self.results.configure(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    SegmentExtractorApp(root)
    root.mainloop()
