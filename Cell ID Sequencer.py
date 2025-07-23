import pandas as pd
import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

#Takes raw produciton data and collected OK cell IDs from before and after any sequence of 3 NG IDs

class CsvNgAnalyzerApp:
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("NG Mark Vision ID Sequencer")
        self.root.resizable(False, False)

        
        self.selected_files: list[str] = []
        self.output_path = tk.StringVar()
        self.ng_length = tk.IntVar(value=3)  # default sequence length

        
        self._build_file_selector()
        self._build_parameters()
        self._build_progress_bar()
        self._build_action_buttons()

    def _build_file_selector(self) -> None:
        frame = ttk.LabelFrame(self.root, text="CSV Files")
        frame.grid(row=0, column=0, padx=10, pady=6, sticky="nsew")

        select_btn = ttk.Button(frame, text="Select CSV Files", command=self._browse_csvs)
        select_btn.pack(anchor="w", pady=4)

        self.file_listbox = tk.Listbox(frame, height=6, width=60)
        self.file_listbox.pack(fill="both", expand=True, padx=4, pady=(0, 4))

    def _build_parameters(self) -> None:
        frame = ttk.LabelFrame(self.root, text="Parameters")
        frame.grid(row=1, column=0, padx=10, pady=6, sticky="ew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="NG Sequence Length:").grid(row=0, column=0, sticky="w", padx=4, pady=3)
        ng_spin = ttk.Spinbox(frame, from_=1, to=100, textvariable=self.ng_length, width=6)
        ng_spin.grid(row=0, column=1, sticky="w", pady=3)

        ttk.Label(frame, text="Output File:").grid(row=1, column=0, sticky="w", padx=4, pady=3)
        out_entry = ttk.Entry(frame, textvariable=self.output_path, width=40)
        out_entry.grid(row=1, column=1, sticky="ew", pady=3)
        ttk.Button(frame, text="Browse", command=self._browse_output).grid(row=1, column=2, padx=4, pady=3)

    def _build_progress_bar(self) -> None:
        self.progress = ttk.Progressbar(self.root, orient="horizontal", mode="determinate", length=450)
        self.progress.grid(row=2, column=0, padx=12, pady=(0, 6), sticky="ew")

    def _build_action_buttons(self) -> None:
        start_btn = ttk.Button(self.root, text="Start Analysis", command=self._start_analysis)
        start_btn.grid(row=3, column=0, pady=(0, 10))


    def _browse_csvs(self) -> None:
        files = filedialog.askopenfilenames(title="Select CSV Files", filetypes=[("CSV Files", "*.csv")])
        if files:
            self.selected_files = list(files)
            self.file_listbox.delete(0, tk.END)
            for fp in self.selected_files:
                self.file_listbox.insert(tk.END, os.path.basename(fp))

    def _browse_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save output CSV as",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="output.csv",
        )
        if path:
            self.output_path.set(path)

    def _start_analysis(self) -> None:
        if not self.selected_files:
            messagebox.showwarning("No files", "Please select at least one CSV file.")
            return
        if not self.output_path.get():
            messagebox.showwarning("No output path", "Please specify where to save the results.")
            return

        # Reset & configure progress bar
        self.progress["value"] = 0
        self.progress["maximum"] = len(self.selected_files)

        # Run in background thread to keep UI responsive
        threading.Thread(target=self._run_analysis, daemon=True).start()


    def _run_analysis(self) -> None:
        output_data: list[list[str]] = []
        sequence_len = self.ng_length.get()

        for idx, csv_path in enumerate(self.selected_files, start=1):
            df = self._read_csv_with_error_handling(csv_path)
            if df is not None:
                output_data.extend(self._analyze_df(df, os.path.basename(csv_path), sequence_len))
            # Update progress bar safely from worker thread
            self.progress.after(0, lambda v=idx: self.progress.config(value=v))

        # Save results
        columns = [
            "File",
            "Before NG Sequence IDs",
            "After NG Sequence IDs",
            "NG Sequence IDs",
        ]
        pd.DataFrame(output_data, columns=columns).to_csv(self.output_path.get(), index=False)

        # Auto‑open the result and notify user
        self._open_file(self.output_path.get())
        messagebox.showinfo("Completed", "Processing complete. Results saved and opened.")


    @staticmethod
    def _read_csv_with_error_handling(csv_path: str):
        try:
            return pd.read_csv(csv_path, on_bad_lines="skip")
        except pd.errors.ParserError as e:
            print(f"Error in file {csv_path}: {e}")
            return None

    @staticmethod
    def _analyze_df(df: pd.DataFrame, filename: str, seq_len: int):
        results = []
        ng_start = None

        for i in range(len(df)):
            if df.loc[i, "Result"] == "NG":
                if ng_start is None:
                    ng_start = i
            else:
                if ng_start is not None and (i - ng_start) >= seq_len:
                    before_ok = ng_start - 1
                    after_ok = i

                    if 0 <= before_ok < len(df) and df.loc[before_ok, "Result"] == "OK":
                        if 0 <= after_ok < len(df) and df.loc[after_ok, "Result"] == "OK":
                            before_id = df.loc[before_ok, "CELL-ID"]
                            after_id = df.loc[after_ok, "CELL-ID"]
                            ng_ids = df.iloc[ng_start:i]["CELL-ID"].tolist()
                            results.append([
                                filename,
                                before_id,
                                after_id,
                                ", ".join(map(str, ng_ids)),
                            ])
                ng_start = None
        return results


    @staticmethod
    def _open_file(path: str) -> None:
        try:
            if sys.platform.startswith("darwin"):
                subprocess.call(["open", path])
            elif os.name == "nt":
                os.startfile(path)  # type: ignore[attr-defined]
            else:
                subprocess.call(["xdg-open", path])
        except Exception as exc:
            print(f"Could not open file: {exc}")



def main() -> None:
    root = tk.Tk()
    CsvNgAnalyzerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
