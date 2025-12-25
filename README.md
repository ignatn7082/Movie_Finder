<p align="center">
  <img src="https://via.placeholder.com/1200x400/1a1a1a/ffffff?text=Movie+Finder+-+Khám+Phá+Thế+Giới+Phim+Ảnh" alt="Movie Finder Banner" width="100%"/>
  <br/><br/>
  <h1 align="center">Movie Finder</h1>
  <h3 align="center">Ứng dụng tìm kiếm và khám phá phim hiện đại – Tìm nhanh, Xem chi tiết, Lưu yêu thích</h3>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Đang+phát+triển-yellow?style=for-the-badge" alt="Status"/>
  <img src="https://img.shields.io/badge/Frontend-JavaScript-f7df1e?style=for-the-badge&logo=javascript" alt="Frontend"/>
  <img src="https://img.shields.io/badge/Backend-Python-3776ab?style=for-the-badge&logo=python" alt="Backend"/>
  <img src="https://img.shields.io/badge/Database-PostgreSQL-336791?style=for-the-badge&logo=postgresql" alt="Database"/>
  <img src="https://img.shields.io/badge/Container-Docker-2496ed?style=for-the-badge&logo=docker" alt="Docker"/>
  <img src="https://img.shields.io/badge/Fullstack-Yes-4caf50?style=for-the-badge" alt="Fullstack"/>
</p>

**Movie Finder** là một ứng dụng web full-stack dành cho những người yêu phim, giúp bạn dễ dàng khám phá thế giới điện ảnh với các tính năng mạnh mẽ và giao diện thân thiện.

### ✨ Tính năng nổi bật

- **Tìm kiếm thông minh**: Tìm phim theo tên, diễn viên, đạo diễn, thể loại, năm phát hành...
- **Thông tin chi tiết phong phú**: Poster chất lượng cao, trailer, tóm tắt nội dung, điểm đánh giá (IMDb/TMDB), danh sách diễn viên, đạo diễn, thời lượng...
- **Danh sách yêu thích (Watchlist)**: Lưu phim yêu thích, đánh dấu đã xem, tạo danh sách cá nhân hóa
- **Giao diện responsive**: Hoạt động mượt mà trên desktop, tablet và mobile
- **Tích hợp API phim**: Sử dụng nguồn dữ liệu đáng tin cậy (TMDB hoặc tương tự) để cập nhật thông tin mới nhất
- **Hiệu suất cao**: Backend tối ưu, tìm kiếm nhanh chóng với phân trang


### 🚀 Hướng dẫn cài đặt & chạy dự án

#### Cách khuyến nghị: Sử dụng Docker Compose 

1. Clone repository:
   ```bash
   git clone https://github.com/ignatn7082/Movie_Finder.git
   cd Movie_Finder

Build và chạy toàn bộ ứng dụng:Bashdocker compose up --build -d
Truy cập:
Frontend: http://localhost:3000 (hoặc port được cấu hình trong docker-compose.yml)
Backend API: http://localhost:8000 (hoặc port tương ứng)


Lần đầu chạy sẽ mất vài phút để build image và khởi tạo database.
Cách chạy thủ công (không dùng Docker)

Backend:Bashcd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Cấu hình database trong file config (nếu có)
python main.py  # hoặc lệnh chạy server chính (flask run / uvicorn ...)
Frontend:Bashcd frontend
npm install  # hoặc yarn install / pnpm install
npm start    # hoặc yarn dev
Database:
Cài đặt PostgreSQL locally
Tạo database và user theo cấu hình trong backend
Chạy migration nếu có (alembic / django migrate ...)


📸 Ảnh chụp màn hình
(Hiện tại chưa có ảnh thực tế – bạn có thể thêm sau khi chụp và upload vào thư mục .github/assets/)

📌 Roadmap (Tính năng dự kiến phát triển)

 Tìm kiếm cơ bản & hiển thị danh sách phim
 Trang chi tiết phim với poster và thông tin
 Hệ thống đăng nhập/đăng ký người dùng (JWT/Auth)
 Watchlist cá nhân hóa & đánh dấu đã xem
 Đánh giá và bình luận phim
 Gợi ý phim dựa trên lịch sử xem
 Hỗ trợ đa ngôn ngữ (Tiếng Việt + Tiếng Anh)
 Tối ưu SEO và PWA (Progressive Web App)

🤝 Đóng góp vào dự án
Chúng tôi rất hoan nghênh mọi đóng góp! Hãy giúp dự án tốt hơn bằng cách:

Fork repository
Tạo branch mới:Bashgit checkout -b feature/ten-tinh-nang
# hoặc bugfix/loi-sua
Commit thay đổi:Bashgit commit -m "Thêm tính năng X / Sửa lỗi Y"
Push branch và tạo Pull Request

Vui lòng tuân theo code style hiện có và viết test nếu có thể.
⚖️ Giấy phép
Dự án hiện sử dụng MIT License (hoặc bạn có thể thay đổi). Xem chi tiết tại file LICENSE.


  Cảm ơn bạn đã quan tâm đến Movie Finder! ⭐ Nếu thấy hữu ích, hãy cho repository một ngôi sao để ủng hộ nhé!

```

