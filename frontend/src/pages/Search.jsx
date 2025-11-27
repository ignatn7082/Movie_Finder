// components/search/Search.jsx
import React, { useState } from "react";
import Navbar from "../components/Navbar";
import SearchSidebar from "../components/search/SearchSidebar";
import SearchTabs from "../components/search/SearchTabs";
import ImageSearchInput from "../components/search/ImageSearchInput";
import TextSearchInput from "../components/search/TextSearchInput";
import SearchResults from "../components/search/SearchResults";
import MovieDetailModal from "../components/search/MovieDetailModal";



function Search() {
  const [tab, setTab] = useState("image");
  const [query, setQuery] = useState("");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [selectedImageModel, setSelectedImageModel] = useState("two_steps_resnet");
  const [results, setResults] = useState([]);
  const [actorInfo, setActorInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState(null);

  const BaseURL = "http://localhost:8000/static/";
  const API_HOST = "http://localhost:8000";


   const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setSelected(null); // Reset chi tiết khi chọn file mới
      setResults([]);
      setActorInfo(null);
    } else {
      setFile(null);
      setPreview(null);
    }
  };

  const handleSetSelected = (item) => {
        // LOG 5: Dữ liệu chi tiết phim được chọn
        console.log("--- CHI TIẾT PHIM ĐƯỢC CHỌN ---");
        console.log("Đối tượng Selected:", item);
        console.log("Tên gốc:", item.original_title);
        console.log("Đạo diễn:", item.director);
        console.log("Thể loại:", item.genres_vn);
        console.log("Diễn viên chính:", item.stars);
        console.log("Tóm tắt:", item.overview);
        console.log("-------------------------------");
        setSelected(item);
    };

  const handleSearch = async (e) => {
    e.preventDefault();
    setResults([]);
    setActorInfo(null);
    setSelected(null);
    setLoading(true);

    try {
      let res, data;

      if (tab === "image" && file) {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("model", selectedImageModel); // Gửi mô hình tìm kiếm ảnh

        // send request
        res = await fetch(`${API_HOST}/search/image`, {
          method: "POST",
          body: formData,
        });
        data = await res.json();

        console.log("--- KẾT QUẢ API /search/image TRẢ VỀ ---");
        console.log(data);
        console.log("-----------------------------------------");

        if (!res.ok) {
          throw new Error(`Lỗi API: ${data.detail || res.statusText}`);
        }

        // xử lý response: luôn setResults thành mảng nếu có movies
        if (data.status === "success") {
          setResults(Array.isArray(data.movies) ? data.movies : []);

          // nếu API trả message (tổng hợp), hiển thị như thông báo
          if (data.message) {
            const topActor = data.actor_similarities && data.actor_similarities.length > 0 ? data.actor_similarities[0][0] : null;
            const topSimilarity = data.actor_similarities && data.actor_similarities.length > 0 ? data.actor_similarities[0][1] : 0.0;
            setActorInfo({
              actor: topActor,
              similarity: topSimilarity,
              message: data.message,
            });
          } else {
            setActorInfo(null);
          }
        } else {
          setResults([]);
          setActorInfo({ error: data.message || "Lỗi không xác định khi tìm kiếm ảnh." });
        }
      } else if (tab === "text" && query.trim()) {
        res = await fetch(`${API_HOST}/search/text?query=${encodeURIComponent(query)}`);
        data = await res.json();

        console.log("--- KẾT QUẢ API /search/text TRẢ VỀ ---");
        console.log(data);
        console.log("----------------------------------------");

        if (!res.ok) throw new Error(`Lỗi API: ${data.detail || res.statusText}`);

        if (data.results && Array.isArray(data.results)) {
          setResults(data.results);
          setActorInfo(null);
        } else if (data.movies && Array.isArray(data.movies)) {
          setResults(data.movies);
          if (data.message) {
            const topActor = data.actor_similarities && data.actor_similarities.length > 0 ? data.actor_similarities[0][0] : null;
            const topSimilarity = data.actor_similarities && data.actor_similarities.length > 0 ? data.actor_similarities[0][1] : 0.0;
            setActorInfo({
              actor: topActor,
              similarity: topSimilarity,
              message: data.message,
            });
          } else {
            setActorInfo(null);
          }
        } else if (data.title && !Array.isArray(data)) {
          setResults([data]);
          setActorInfo(null);
        } else {
          setResults([]);
          setActorInfo(null);
        }
      } else {
        alert("Hãy nhập mô tả hoặc chọn ảnh để tìm kiếm!");
        setLoading(false);
        return;
      }
    } catch (error) {
      console.error("Lỗi trong quá trình tìm kiếm:", error);
      setResults([]);
      setActorInfo({ error: `Đã xảy ra lỗi: ${error.message}. Vui lòng kiểm tra console.` });
    } finally {
      setLoading(false);
    }
  };

  // Hàm xử lý khi người dùng click vào một ví dụ tìm kiếm
  const handleExampleClick = (exampleQuery) => {
    if (tab === 'text') {
      setTab('text'); 
      setQuery(exampleQuery);
      setActorInfo(null);
      setResults([]);
      setSelected(null);
    }
  };

  const fallbackPoster = (title) => {
    if (!title) return "posters/default_poster.jpg"; 
    // Logic tạo tên file poster fallback (giữ nguyên logic gốc)
    const fallbackName = title
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/\s+/g, "_")
      .replace(/[^a-z0-9_]/g, '') // Thêm: Lọc bỏ ký tự đặc biệt khác
      + ".jpg";
    return "posters/" + fallbackName;
  };
 
const cleanPath = (path) => {
    if (!path) return "";
    // Loại bỏ dấu gạch chéo ở cuối
    return path.replace(/\/+$/, '');
};

// Hàm này giúp loại bỏ dấu gạch chéo ở đầu chuỗi
const cleanLeadingSlash = (path) => {
    if (!path) return "";
    // Loại bỏ dấu gạch chéo ở đầu
    return path.replace(/^\/+/, '');
};  

const getPosterUrl = (result) => {
    // Ưu tiên kiểm tra result.poster
    if (result.poster) {
        let posterPath = result.poster;
        
        // 1. Kiểm tra URL hoàn chỉnh
        if (posterPath.startsWith('http://') || posterPath.startsWith('https://')) {
            return posterPath;
        }

        // 2. Chuẩn hóa đường dẫn tương đối để loại bỏ ký tự thừa
        if (posterPath.startsWith(API_HOST)) {
            posterPath = posterPath.substring(API_HOST.length);
        }
        if (posterPath.startsWith('/static/')) {
            posterPath = posterPath.substring('/static/'.length);
        } else if (posterPath.startsWith('static/')) {
            posterPath = posterPath.substring('static/'.length);
        }

        // 3. Nối BaseURL (đã chuẩn hóa) với posterPath (đã chuẩn hóa)
        posterPath = cleanLeadingSlash(posterPath); 
        
        // BaseURL hiện tại là: http://localhost:8000/static/
        return cleanPath(BaseURL) + "/" + posterPath;

    } 
    // 4. Fallback: Nối BaseURL với kết quả từ fallbackPoster
    const fallbackPath = fallbackPoster(result.title || result.original_title);
    return cleanPath(BaseURL) + "/" + cleanLeadingSlash(fallbackPath);
};

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-gray-800 dark:to-indigo-950 font-sans">
      <Navbar />

      <main className="container mx-auto px-4 py-8 md:py-12">
        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-6xl font-extrabold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
            Tìm Phim Thông Minh
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Dùng AI để tìm phim bằng <span className="text-indigo-600 font-bold">văn bản</span> hoặc <span className="text-purple-600 font-bold">hình ảnh</span>
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-3">
            <SearchSidebar tab={tab} onExampleClick={(q) => { setTab("text"); setQuery(q); }} />
          </div>

          {/* Main Content */}
          <div className="lg:col-span-9">
            <div className="bg-white/80 dark:bg-gray-800/90 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 dark:border-gray-700 p-8">
              <SearchTabs tab={tab} setTab={setTab} onTabChange={() => {
                setQuery(""); setFile(null); setPreview(null); setResults([]); setActorInfo(null); setSelected(null);
              }} />

              <form onSubmit={handleSearch} className="mb-10">
                {tab === "image" ? (
                  <ImageSearchInput
                    file={file}
                    preview={preview}
                    selectedImageModel={selectedImageModel}
                    setFile={setFile}
                    setPreview={setPreview}
                    setSelectedImageModel={setSelectedImageModel}
                  />
                ) : (
                  <TextSearchInput query={query} setQuery={setQuery} />
                )}

                <button
                  type="submit"
                  disabled={loading || (tab === "image" && !file) || (tab === "text" && !query.trim())}
                  className="mt-8 w-full py-5 px-8 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-extrabold text-xl rounded-2xl shadow-2xl transform hover:scale-105 transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {loading ? (
                    <>Đang tìm kiếm...</>
                  ) : (
                    <>{tab === "image" ? "Tìm Phim Bằng Ảnh" : "Tìm Phim Bằng Văn Bản"}</>
                  )}
                </button>
              </form>

              <SearchResults
                loading={loading}
                results={results}
                actorInfo={actorInfo}
                onSelectMovie={setSelected}
                getPosterUrl={getPosterUrl}
                BaseURL={BaseURL}
              />
            </div>
          </div>
        </div>

        <MovieDetailModal movie={selected} onClose={() => setSelected(null)} getPosterUrl={getPosterUrl} />
      </main>
    </div>
  );
}

export default Search;