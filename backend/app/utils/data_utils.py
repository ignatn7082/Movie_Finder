import os
import pandas as pd
from functools import lru_cache

@lru_cache(maxsize=1)
def load_movie_metadata():
    """
    Đọc CSV metadata phim (chỉ load 1 lần, tự cache trong RAM).
    Tự động tìm file trong thư mục 'data/Movies_vi_with_poster.csv'.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    csv_path = os.path.join(base_dir, "data", "Movies_vi_with_poster.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Không tìm thấy file metadata: {csv_path}")

    df = pd.read_csv(csv_path, encoding="utf-8")
    print(f"[INFO] Loaded movie metadata: {len(df)} records from {csv_path}")
    return df
