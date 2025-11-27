import React, { useState } from "react";
import { Loader2, Search as SearchIcon, Image, Type, User, AlertTriangle, X, Upload, Sparkles, Film, Calendar, Clapperboard, Users } from "lucide-react";
import Navbar from "../components/Navbar";

// Dữ liệu mẫu cho phần hướng dẫn
const searchExamples = {
  text: [
    { title: "Tìm theo tên/mô tả", query: "Phim về người lính sau chiến tranh" },
    { title: "Tìm theo đạo diễn", query: "Đạo diễn Bùi Thạc Chuyên" },
    { title: "Tìm theo thể loại", query: "Phim tâm lý xã hội" },
    { title: "Tìm theo diễn viên/vai diễn", query: "Diễn viên Thái Hòa" },
  ],
  image: [
    { title: "Tìm bằng poster phim", info: "Tải lên poster phim 'Hai Phượng'" },
    { title: "Tìm bằng ảnh diễn viên", info: "Tải lên ảnh Trấn Thành" },
    { title: "Tìm bằng ảnh một cảnh phim", info: "Tải lên ảnh một cảnh trong 'Mắt Biếc'" },
  ]
};

const SidebarGuide = ({ tab, handleExampleClick }) => {
  const isTextTab = tab === 'text';
  const examples = isTextTab ? searchExamples.text : searchExamples.image;

  return (
    <div className="p-6 bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-gray-900 dark:to-gray-800 rounded-2xl shadow-xl border border-indigo-200 dark:border-indigo-900 h-full overflow-y-auto">
      <div className="flex items-center mb-6">
        <div className="p-3 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl shadow-lg mr-4">
          <Sparkles className="w-6 h-6 text-white" />
        </div>
        <h3 className="text-2xl font-extrabold text-indigo-700 dark:text-indigo-400">
          Hướng Dẫn {isTextTab ? "Tìm Văn Bản" : "Tìm Bằng Ảnh"}
        </h3>
      </div>

      <div className="space-y-6">
        <div className="bg-white dark:bg-gray-800 p-5 rounded-xl shadow-md border border-indigo-100 dark:border-indigo-800">
          <ul className="space-y-3 text-sm">
            {isTextTab ? (
              <>
                <li className="flex items-start"><span className="text-indigo-600 mr-2">•</span> <strong>Tìm bằng mô tả tự nhiên</strong> – "Phim buồn về tình yêu tuổi trẻ"</li>
                <li className="flex items-start"><span className="text-indigo-600 mr-2">•</span> Hỗ trợ tìm đạo diễn, diễn viên, thể loại</li>
                <li className="flex items-start"><span className="text-indigo-600 mr-2">•</span> Công nghệ tìm kiếm ngữ nghĩa AI</li>
              </>
            ) : (
              <>
                <li className="flex items-start"><span className="text-purple-600 mr-2">•</span> <strong>Poster, ảnh diễn viên hoặc cảnh phim</strong></li>
                <li className="flex items-start"><span className="text-purple-600 mr-2">•</span> Hỗ trợ 2 mô hình AI: CLIP & ResNet50</li>
                <li className="flex items-start"><span className="text-purple-600 mr-2">•</span> Nhận diện cả diễn viên trong ảnh</li>
              </>
            )}
          </ul>
        </div>

        <div>
          <h4 className="text-lg font-bold text-gray-800 dark:text-gray-200 mb-4 flex items-center">
            {isTextTab ? <Type className="w-5 h-5 mr-2 text-indigo-600" /> : <Image className="w-5 h-5 mr-2 text-purple-600" />}
            Ví dụ {isTextTab ? "tìm kiếm" : "hình ảnh"}
          </h4>
          <div className="space-y-3">
            {examples.map((example, index) => (
              <div 
                key={index}
                onClick={isTextTab ? () => handleExampleClick(example.query) : undefined}
                className={`p-4 rounded-xl border-2 transition-all transform hover:scale-105 ${
                  isTextTab 
                    ? 'bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 border-blue-300 dark:border-blue-700 cursor-pointer shadow-md hover:shadow-xl' 
                    : 'bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600'
                }`}
              >
                <p className="font-bold text-gray-800 dark:text-gray-200">{example.title}</p>
                <p className={`text-sm mt-1 ${isTextTab ? 'text-indigo-600 dark:text-indigo-400 font-medium' : 'text-gray-600 dark:text-gray-400 italic'}`}>
                  {isTextTab ? `“${example.query}”` : example.info}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

function Search() {
  const [tab, setTab] = useState("image");
  const [selectedImageModel, setSelectedImageModel] = useState("two_steps_resnet");
  const [query, setQuery] = useState("");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
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
        {/* Tiêu đề chính */}
        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-6xl font-extrabold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
            Tìm Phim Thông Minh
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Dùng AI để tìm phim bằng <span className="text-indigo-600 font-bold">văn bản</span> hoặc <span className="text-purple-600 font-bold">hình ảnh</span>
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Cột trái - Hướng dẫn */}
          <div className="lg:col-span-3">
            <SidebarGuide tab={tab} handleExampleClick={handleExampleClick} />
          </div>

          {/* Cột phải - Form & Kết quả */}
          <div className="lg:col-span-9">
            <div className="bg-white/80 dark:bg-gray-800/90 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 dark:border-gray-700 p-8">
              {/* Tab chuyển đổi đẹp hơn */}
              <div className="flex justify-center mb-10">
                <div className="inline-flex bg-gray-100 dark:bg-gray-700 p-2 rounded-2xl shadow-inner">
                  <button
                    onClick={() => { setTab("image"); setQuery(""); setActorInfo(null); setResults([]); setSelected(null); }}
                    className={`flex items-center px-8 py-4 rounded-xl font-bold text-lg transition-all duration-300 ${
                      tab === "image"
                        ? "bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg"
                        : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                    }`}
                  >
                    <Image className="w-6 h-6 mr-3" />
                    Tìm bằng Ảnh
                  </button>
                  <button
                    onClick={() => { setTab("text"); setFile(null); setPreview(null); setActorInfo(null); setResults([]); setSelected(null); }}
                    className={`flex items-center px-8 py-4 rounded-xl font-bold text-lg transition-all duration-300 ${
                      tab === "text"
                        ? "bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg"
                        : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                    }`}
                  >
                    <Type className="w-6 h-6 mr-3" />
                    Tìm bằng Văn Bản
                  </button>
                </div>
              </div>

              {/* Form tìm kiếm */}
              <form onSubmit={handleSearch} className="mb-10">
                {tab === "image" ? (
                  <div className="relative group">
                    <label htmlFor="image-upload" className="block cursor-pointer">
                      <input id="image-upload" type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
                      <div className={`border-4 border-dashed rounded-3xl p-12 text-center transition-all duration-300 ${
                        preview 
                          ? "border-indigo-400 bg-indigo-50/50 dark:bg-indigo-900/20" 
                          : "border-gray-300 dark:border-gray-600 hover:border-indigo-500 hover:bg-indigo-50/30 dark:hover:bg-gray-700 group"
                      }`}>
                        {preview ? (
                          <div className="space-y-6">
                            <img src={preview} alt="Preview" className="mx-auto max-h-96 rounded-2xl shadow-2xl border-4 border-white" />
                            <p className="text-indigo-600 dark:text-indigo-400 font-bold text-lg animate-pulse">
                              <Upload className="inline w-5 h-5 mr-2" />
                              Nhấn để thay đổi ảnh
                            </p>
                          </div>
                        ) : (
                          <div>
                            <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center shadow-2xl">
                              <Image className="w-12 h-12 text-white" />
                            </div>
                            <p className="text-2xl font-bold text-gray-700 dark:text-gray-300 mb-2">
                              Tải lên Poster, Ảnh Diễn Viên hoặc Cảnh Phim
                            </p>
                            <p className="text-gray-500 dark:text-gray-400">Kéo thả hoặc nhấn để chọn ảnh</p>
                          </div>
                        )}
                      </div>
                    </label>

                    {/* Chọn mô hình */}
                    <div className="mt-6 flex justify-center items-center space-x-4">
                      <span className="text-lg font-medium text-gray-700 dark:text-gray-300">Mô hình AI:</span>
                      <select
                        value={selectedImageModel}
                        onChange={(e) => setSelectedImageModel(e.target.value)}
                        className="px-6 py-3 bg-gradient-to-r from-indigo-100 to-purple-100 dark:from-indigo-900 dark:to-purple-900 rounded-xl font-bold text-indigo-700 dark:text-indigo-300 shadow-lg"
                      >
                        <option value="two_steps_clip">CLIP (Thông minh hơn)</option>
                        <option value="two_steps_resnet">ResNet50 (Nhanh hơn)</option>
                      </select>
                    </div>
                  </div>
                ) : (
                  <div className="relative">
                    <textarea
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="Ví dụ: Phim về người lính trở về từ chiến tranh, đạo diễn Victor Vũ, diễn viên Lan Ngọc..."
                      className="w-full p-6 pr-16 text-lg bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-gray-700 dark:to-gray-800 rounded-2xl border-2 border-indigo-200 dark:border-indigo-700 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-300 dark:focus:ring-indigo-800 shadow-xl resize-none transition-all"
                      rows="5"
                    />
                    <SearchIcon className="absolute right-6 top-6 w-8 h-8 text-indigo-500" />
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading || (tab === "image" && !file) || (tab === "text" && !query.trim())}
                  className="mt-8 w-full py-5 px-8 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-extrabold text-xl rounded-2xl shadow-2xl transform hover:scale-105 transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-8 h-8 mr-3 animate-spin" />
                      Đang tìm kiếm...
                    </>
                  ) : (
                    <>
                      <SearchIcon className="w-8 h-8 mr-3" />
                      {tab === "image" ? "Tìm Phim Bằng Ảnh" : "Tìm Phim Bằng Văn Bản"}
                    </>
                  )}
                </button>
              </form>

              {/* Kết quả */}
<div className="mt-10">
                <h3 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-8">
                  Kết Quả Tìm Kiếm {results.length > 0 && `(${results.length})`}
                </h3>

                {loading && (
                  <div className="flex flex-col items-center py-20">
                    <div className="relative">
                      <Loader2 className="w-20 h-20 text-indigo-600 animate-spin" />
                      <Film className="w-10 h-10 text-purple-600 absolute top-5 left-5 animate-pulse" />
                    </div>
                    <p className="mt-6 text-xl text-gray-600 dark:text-gray-400">AI đang phân tích...</p>
                  </div>
                )}

                {/* Nhận diện diễn viên chính */}
                {actorInfo && actorInfo.actor && (
                  <div className="mb-10 p-8 bg-gradient-to-r from-yellow-100 to-orange-100 dark:from-yellow-900/30 dark:to-orange-900/30 rounded-3xl border-2 border-yellow-400 dark:border-yellow-700 shadow-2xl">
                    <h4 className="text-2xl font-bold text-orange-700 dark:text-orange-400 flex items-center mb-4">
                      <User className="w-10 h-10 mr-4" />
                      Phát hiện diễn viên: <span className="ml-3 text-3xl">{actorInfo.actor}</span>
                    </h4>
                    <p className="text-lg font-bold text-green-600 dark:text-green-400">
                      Độ tương đồng: {(actorInfo.similarity * 100).toFixed(1)}%
                    </p>
                  </div>
                )}

                {/* Danh sách phim – chỉ hiển thị khi KHÔNG phải kết quả nhận diện diễn viên */}
                {!loading && results.length > 0 && !(actorInfo && actorInfo.actor) && (
                  <div className="grid gap-10">
                    {results.map((item, idx) => (
                      <div
                        key={idx}
                        onClick={() => handleSetSelected(item)}
                        className="group bg-white dark:bg-gray-800 rounded-3xl shadow-xl hover:shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden transform hover:scale-[1.02] transition-all duration-500 cursor-pointer"
                      >
                        <div className="flex flex-col lg:flex-row">
                          {/* Poster */}
                          <div className="lg:w-64 flex-shrink-0 relative overflow-hidden">
                            <img
                              src={getPosterUrl(item)}
                              alt={item.title}
                              className="w-full h-96 lg:h-full object-cover group-hover:scale-110 transition-transform duration-700"
                              onError={(e) => {
                                e.target.onerror = null;
                                e.target.src = BaseURL + "300x450/1a1a1a/ffffff?text=No+Poster";
                              }}
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 flex items-end p-6">
                              <p className="text-white font-bold text-lg">Xem chi tiết</p>
                            </div>
                          </div>

                          {/* Nội dung */}
                          <div className="p-8 flex-grow flex flex-col lg:flex-row gap-8">
                            {/* Thông tin phim */}
                            <div className="flex-1 space-y-5">
                              <h4 className="text-3xl font-extrabold text-indigo-600 dark:text-indigo-400">
                                {item.title}
                              </h4>

                              <div className="flex flex-wrap items-center gap-4 text-sm">
                                <span className="flex items-center text-gray-600 dark:text-gray-400">
                                  <Calendar className="w-5 h-5 mr-2" />
                                  {item.release_date?.split('-')[0] || "N/A"}
                                </span>
                                {item.similarity && (
                                  <span className="px-4 py-2 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-full font-bold">
                                    {(item.similarity * 100).toFixed(1)}% khớp
                                  </span>
                                )}
                              </div>

                              <p className="text-gray-700 dark:text-gray-300 leading-relaxed line-clamp-4">
                                {item.overview || "Chưa có tóm tắt."}
                              </p>

                              <div className="flex flex-wrap gap-6 text-sm">
                                <div className="flex items-center text-gray-600 dark:text-gray-400">
                                  <Clapperboard className="w-5 h-5 mr-2 text-indigo-600" />
                                  <span className="font-medium">Đạo diễn:</span> {item.director || "Đang cập nhật"}
                                </div>
                                <div className="flex items-center text-gray-600 dark:text-gray-400">
                                  <Users className="w-5 h-5 mr-2 text-purple-600" />
                                  <span className="font-medium">Diễn viên:</span> {item.stars?.split(',')[0] || "Nhiều diễn viên"}
                                </div>
                              </div>
                            </div>

                            {/* BẢNG ĐỘ TƯƠNG ĐỒNG DIỄN VIÊN – ĐÃ SỬA LẠI ĐẸP & SCROLL */}
                            {item.actors && Array.isArray(item.actors) && item.actors.length > 0 && (
                              <div className="lg:w-80">
                                <h5 className="text-xl font-bold text-gray-800 dark:text-gray-200 mb-4 flex items-center">
                                  <User className="w-6 h-6 mr-2 text-purple-600" />
                                  Diễn viên khớp theo ảnh
                                </h5>

                                <div className="bg-gray-50 dark:bg-gray-700/50 rounded-2xl border border-gray-200 dark:border-gray-600 overflow-hidden">
                                  <div className="max-h-64 overflow-y-auto scrollbar-thin scrollbar-thumb-indigo-500 scrollbar-track-gray-200 dark:scrollbar-thumb-indigo-400 dark:scrollbar-track-gray-700">
                                    <table className="w-full text-sm">
                                      <thead className="bg-indigo-100 dark:bg-indigo-900/50 sticky top-0">
                                        <tr>
                                          <th className="px-4 py-3 text-left font-bold text-indigo-700 dark:text-indigo-300">Diễn viên</th>
                                          <th className="px-4 py-3 text-right font-bold text-green-600 dark:text-green-400">Độ tương đồng</th>
                                        </tr>
                                      </thead>
                                      <tbody className="divide-y divide-gray-200 dark:divide-gray-600">
                                        {item.actors.map((actorItem, i) => (
                                          <tr key={i} className="hover:bg-indigo-50 dark:hover:bg-indigo-900/30 transition-colors">
                                            <td className="px-4 py-3 font-medium text-gray-800 dark:text-gray-200 truncate">
                                              {actorItem.actor}
                                            </td>
                                            <td className="px-4 py-3 text-right">
                                              <span className="inline-block px-3 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-full font-bold text-sm">
                                                {(actorItem.similarity * 100).toFixed(1)}%
                                              </span>
                                            </td>
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  </div>
                                </div>

                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
                                  {item.actors.length} diễn viên được phát hiện
                                </p>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Không có kết quả */}
                {!loading && results.length === 0 && !actorInfo && (
                  <div className="text-center py-20">
                    <Film className="w-24 h-24 mx-auto text-gray-300 dark:text-gray-700 mb-6" />
                    <p className="text-xl text-gray-500 dark:text-gray-400">
                      Chưa có kết quả. Hãy thử tìm kiếm bằng từ khóa hoặc hình ảnh khác nhé!
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        
        {/* Modal chi tiết phim - đẹp hơn */}
        {selected && (
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-6" onClick={() => setSelected(null)}>
            <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-3xl max-w-5xl w-full max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
              <div className="relative">
                <button
                  onClick={() => setSelected(null)}
                  className="absolute -top-4 -right-4 bg-red-600 text-white p-4 rounded-full shadow-2xl hover:bg-red-700 transition z-10"
                >
                  <X className="w-6 h-6" />
                </button>
                <div className="grid md:grid-cols-2">
                  <div className="p-8">
                    <img
                      src={getPosterUrl(selected)}
                      alt={selected.title}
                      className="w-full rounded-2xl shadow-2xl border-8 border-white dark:border-gray-700"
                    />
                  </div>
                  <div className="p-10 space-y-6">
                    <h2 className="text-4xl font-extrabold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                      {selected.title}
                    </h2>
                    <p className="text-2xl text-gray-600 dark:text-gray-400">{selected.original_title}</p>
                    <div className="space-y-4 text-lg">
                      <p><strong className="text-indigo-600">Đạo diễn:</strong> {selected.director}</p>
                      <p><strong className="text-purple-600">Thể loại:</strong> {selected.genres_vn}</p>
                      <p><strong className="text-green-600">Diễn viên:</strong> {selected.stars}</p>
                    </div>
                    <div className="pt-6 border-t-2 border-gray-200 dark:border-gray-700">
                      <h3 className="text-2xl font-bold mb-4 text-indigo-600">Tóm tắt nội dung</h3>
                      <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-lg">
                        {selected.overview || "Đang cập nhật..."}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default Search;