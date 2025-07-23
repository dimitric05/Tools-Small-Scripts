import os

#Used to filter out mass amounts of JPEG files by specific string since windows file explorer is slow.

directory = r"#[REMOVED]"  
substring = "ex. TOP IMAGE"  
# ──────────────────────────────────────────────────────────────────────────────

for fname in os.listdir(directory):
    if fname.lower().endswith(".jpg") and substring in fname:
        full_path = os.path.join(directory, fname)
        try:
            os.remove(full_path)
            print(f"Deleted: {full_path}")
        except Exception as e:
            print(f"Could not delete {full_path}: {e}")
