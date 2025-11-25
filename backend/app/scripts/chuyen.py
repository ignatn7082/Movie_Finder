import numpy as np
import os

# ******************************************************
# CẤU HÌNH: ĐIỀU CHỈNH CÁC BIẾN NÀY CHO TỪNG FILE
# ******************************************************
# Đường dẫn tương đối đến thư mục chứa file .npy
DATA_DIR = r"F:\LV\ui\backend\data" 
# Tên file .npy cần chuyển đổi
INPUT_NPY_FILENAME = "train_labels_cosine.npy" 
# Tên file .txt kết quả
OUTPUT_TXT_FILENAME = "train_labels_cosine.txt"
# ******************************************************


def convert_npy_to_txt(npy_filename, txt_filename, data_dir):
    """
    Tải file .npy và ghi nội dung mảng ra file .txt, mỗi phần tử một dòng.
    """
    input_path = os.path.join(data_dir, npy_filename)
    output_path = os.path.join(data_dir, txt_filename)

    if not os.path.exists(input_path):
        print(f"LỖI: Không tìm thấy file input: {input_path}")
        return

    try:
        # 1. Tải mảng từ file .npy
        # Cho phép tải các mảng có cấu trúc không đồng nhất (dtype=object)
        labels_array = np.load(input_path, allow_pickle=True)
        
        print(f"Đã tải thành công {len(labels_array)} nhãn từ {npy_filename}.")

        # 2. Ghi từng phần tử của mảng ra file .txt
        with open(output_path, 'w', encoding='utf-8') as f:
            for label in labels_array:
                # Đảm bảo nội dung là chuỗi trước khi ghi
                f.write(str(label) + '\n')
        
        print(f"✅ Chuyển đổi thành công! Nhãn đã được ghi vào: {output_path}")

    except Exception as e:
        print(f"LỖI xảy ra trong quá trình xử lý file {npy_filename}: {e}")

# Chạy hàm chuyển đổi với cấu hình đã cho
if __name__ == "__main__":
    convert_npy_to_txt(INPUT_NPY_FILENAME, OUTPUT_TXT_FILENAME, DATA_DIR)