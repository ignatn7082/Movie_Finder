Movie_Finder
Movie Finder là một ứng dụng web đầy đủ (full-stack) cho phép người dùng tìm kiếm, khám phá và quản lý thông tin phim. Dự án sử dụng kiến trúc client-server với frontend và backend riêng biệt, cùng cơ sở dữ liệu PostgreSQL.
Công nghệ sử dụng

Frontend: JavaScript (có thể là React, Vue hoặc plain JS – nằm trong thư mục frontend/)
Backend: Python (có thể là Flask, Django hoặc FastAPI – nằm trong thư mục backend/)
Database: PostgreSQL (dữ liệu lưu trong postgres_data/)
Containerization: Docker Compose (sử dụng file docker-compose.yml để chạy toàn bộ ứng dụng)

Tính năng chính (dự kiến)

Tìm kiếm phim theo tên, thể loại, năm phát hành,...
Hiển thị thông tin chi tiết phim (poster, mô tả, diễn viên, đánh giá,...)
Có thể tích hợp API phim bên thứ ba như TMDB hoặc OMDB
Giao diện thân thiện, responsive

Yêu cầu hệ thống

Docker và Docker Compose (khuyến khích cách chạy dễ nhất)
Hoặc: Node.js (cho frontend), Python 3.x (cho backend), PostgreSQL

Cách cài đặt và chạy dự án
Cách 1: Sử dụng Docker Compose (khuyến nghị)

Clone repository:Bashgit clone https://github.com/ignatn7082/Movie_Finder.git
cd Movie_Finder
Chạy ứng dụng bằng Docker Compose:Bashdocker-compose up --build
Truy cập ứng dụng tại: http://localhost:3000 (frontend) hoặc port tương ứng được định nghĩa trong docker-compose.yml.

Cách 2: Chạy thủ công (không dùng Docker)

Backend:Bashcd backend
pip install -r requirements.txt  # nếu có file requirements.txt
python app.py  # hoặc lệnh chạy server chính
Frontend:Bashcd frontend
npm install  # hoặc yarn install
npm start
Database: Cấu hình kết nối PostgreSQL theo file config trong backend.
