import React, { useState } from "react";
import { Loader2, Search as SearchIcon, Image, Type, User, AlertTriangle, X } from "lucide-react";
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

// Component Hướng dẫn và Ví dụ được tùy chỉnh theo tab hiện tại
const SidebarGuide = ({ tab, handleExampleClick }) => {
    // Xác định tab hiện tại
    const isTextTab = tab === 'text';
    // Chọn ví dụ tương ứng
    const examples = isTextTab ? searchExamples.text : searchExamples.image;

    return (
      <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 h-full overflow-y-auto">
        <h3 className="text-xl font-extrabold text-blue-700 dark:text-blue-400 mb-4 border-b pb-2">
          <SearchIcon className="inline mr-2 w-5 h-5"/> Hướng Dẫn {isTextTab ? "Tìm Kiếm Văn Bản" : "Tìm Kiếm Bằng Ảnh"}
        </h3>

        {/* PHẦN HƯỚNG DẪN CỤ THỂ THEO TAB */}
        <div className="mb-6">
          {isTextTab ? (
            // Hướng dẫn cho Tab Văn bản
            <ul className="list-disc list-inside ml-4 text-sm text-gray-600 dark:text-gray-400 space-y-2">
              <li className='font-semibold text-gray-800 dark:text-gray-200'>Mục tiêu: Tìm phim bằng mô tả, tên, thể loại, đạo diễn, hoặc diễn viên/vai diễn.</li>
              <li>Sử dụng ngôn ngữ tự nhiên, tiếng Việt có dấu.</li>
              <li>Hệ thống hỗ trợ tìm kiếm ngữ nghĩa (semantic search).</li>
              <li>Hỗ trợ tìm kiếm diễn viên/vai diễn.</li>
            </ul>
          ) : (
            // Hướng dẫn cho Tab Ảnh
            <ul className="list-disc list-inside ml-4 text-sm text-gray-600 dark:text-gray-400 space-y-2">
              <li className='font-semibold text-gray-800 dark:text-gray-200'>Mục tiêu: Tìm phim dựa trên hình ảnh.</li>
              <li>Bạn có thể tải lên poster phim, ảnh diễn viên, hoặc ảnh một cảnh phim.</li>
              <li>Chọn Mô hình: Thử nghiệm với các mô hình CLIP hoặc ResNet50.</li>
              <li>Lưu ý: Độ chính xác phụ thuộc vào chất lượng hình ảnh.</li>
            </ul>
          )}
        </div>
        
        {/* VÍ DỤ TÌM KIẾM CỤ THỂ THEO TAB */}
        <h4 className="text-lg font-extrabold text-gray-800 dark:text-gray-200 flex items-center mb-3 border-t pt-4">
          {isTextTab ? 
            <Type className="inline mr-2 w-5 h-5 text-indigo-500"/> : 
            <Image className="inline mr-2 w-5 h-5 text-orange-500"/>
          }
          Ví Dụ {isTextTab ? "Văn Bản (Click để thử)" : "Hình Ảnh"}
        </h4>
        <div className="space-y-2">
          {examples.map((example, index) => (
            <div 
              key={index} 
              className={`p-3 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm transition-all ${isTextTab ? 'cursor-pointer hover:bg-blue-50 dark:hover:bg-gray-600' : ''}`}
              onClick={isTextTab ? () => handleExampleClick(example.query) : undefined}
              title={isTextTab ? `Click để điền: ${example.query}` : ''}
            >
              <p className="font-semibold text-sm text-gray-900 dark:text-white mb-1">{example.title}</p>
              <p className={`text-xs italic truncate ${isTextTab ? 'text-blue-600 dark:text-blue-300' : 'text-gray-600 dark:text-gray-400'}`}>
                {isTextTab ? `"${example.query}"` : example.info}
              </p>
            </div>
          ))}
        </div>
      </div>
    );
  };



function Search() {
  const [tab, setTab] = useState("image"); // tab hiện tại: "image" | "text"
  const [selectedImageModel, setSelectedImageModel] = useState("two_steps_resnet"); // Mặc định dùng ResNet (theo logic backend)
  const [query, setQuery] = useState("");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [results, setResults] = useState([]); // luôn là mảng phim để render list
  const [actorInfo, setActorInfo] = useState(null); // lưu kết quả actor (nếu có)
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState(null);

  // API base URL
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
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900 font-[Inter] text-gray-900 dark:text-white">
            <Navbar />

            <main className="container mx-auto p-4 md:p-8">
                <h1 className="text-4xl font-extrabold text-center text-gray-900 dark:text-white mb-8">
                    Hệ Thống Tìm Kiếm Phim Thông Minh
                </h1>
                
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    
                    {/* CỘT TRÁI: Hướng Dẫn & Ví Dụ */}
                    <div className="lg:col-span-3">
                        <SidebarGuide tab={tab} handleExampleClick={handleExampleClick} />
                    </div>

                    {/* CỘT PHẢI: Form và Kết Quả */}
                    <div className="lg:col-span-9 bg-white dark:bg-gray-800 p-6 rounded-xl shadow-2xl">
                        
                        {/* Thanh Tab Chuyển Đổi */}
                        <div className="flex justify-center mb-6">
                            <button
                                onClick={() => { setTab("image"); setQuery(""); setActorInfo(null); setResults([]); setSelected(null); }}
                                className={`py-2 px-6 rounded-l-full font-semibold transition-all duration-300 flex items-center ${
                                    tab === "image"
                                        ? "bg-blue-600 text-white shadow-lg shadow-blue-500/50"
                                        : "bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
                                }`}
                            >
                                <Image className="w-5 h-5 mr-2" /> Tìm Kiếm Ảnh
                            </button>
                            <button
                                onClick={() => { setTab("text"); setFile(null); setPreview(null); setActorInfo(null); setResults([]); setSelected(null); }}
                                className={`py-2 px-6 rounded-r-full font-semibold transition-all duration-300 flex items-center ${
                                    tab === "text"
                                        ? "bg-blue-600 text-white shadow-lg shadow-blue-500/50"
                                        : "bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
                                }`}
                            >
                                <Type className="w-5 h-5 mr-2" /> Tìm Kiếm Văn Bản
                            </button>
                        </div>

                        {/* Form Tìm Kiếm */}
                        <form onSubmit={handleSearch} className="mb-8 space-y-4">
                            {tab === "image" ? (
                                // Input Ảnh
                                <div className="border-4 border-dashed border-blue-300 dark:border-blue-600 rounded-xl p-6 text-center">
                                    <label htmlFor="image-upload" className="block cursor-pointer">
                                        <input
                                            id="image-upload"
                                            type="file"
                                            accept="image/*"
                                            onChange={handleFileChange}
                                            className="hidden"
                                        />
                                        {preview ? (
                                            <div className="flex flex-col items-center">
                                                <img 
                                                    src={preview} 
                                                    alt="Ảnh xem trước" 
                                                    className="max-h-64 max-w-full object-contain rounded-lg shadow-md mb-4 border border-gray-300"
                                                />
                                                <p className="text-blue-600 dark:text-blue-400 font-medium">Click để chọn ảnh khác</p>
                                            </div>
                                        ) : (
                                            <div className="p-8">
                                                <Image className="w-12 h-12 mx-auto text-blue-500 mb-2" />
                                                <p className="text-lg font-semibold text-gray-700 dark:text-gray-300">Tải lên ảnh Poster, Diễn viên hoặc Cảnh phim</p>
                                                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Kéo thả hoặc nhấn để duyệt file (JPG, PNG)</p>
                                            </div>
                                        )}
                                    </label>
                                    
                                    {/* Chọn mô hình tìm kiếm ảnh */}
                                    <div className="mt-4 flex justify-center items-center space-x-4">
                                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Mô hình:</span>
                                        <select
                                            value={selectedImageModel}
                                            onChange={(e) => { 
                                                setSelectedImageModel(e.target.value); 
                                                console.log("Mô hình tìm kiếm ảnh được chọn:", e.target.value); 
                                            }}
                                            className="p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-blue-500 focus:border-blue-500"
                                        >
                                            <option value="two_steps_clip">CLIP</option>
                                            <option value="two_steps_resnet">ResNet50</option>
                                        </select>
                                    </div>

                                </div>
                            ) : (
                                // Input Văn bản
                                <textarea
                                    type="text"
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                    placeholder="Nhập tên phim, mô tả, đạo diễn, hoặc diễn viên..."
                                    className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-inner focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                                rows="4"
                                />
                            )}

                            <button
                                type="submit"
                                disabled={loading || (tab === "image" && !file) || (tab === "text" && !query.trim())}
                                className="w-full py-3 px-4 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition duration-300 disabled:bg-blue-400 dark:disabled:bg-blue-800 shadow-md flex items-center justify-center"
                            >
                                {loading && <Loader2 className="w-5 h-5 mr-2 animate-spin" />}
                                {tab === "image" ? "Tìm Kiếm Phim Bằng Ảnh" : "Tìm Kiếm Phim Bằng Văn Bản"}
                            </button>
                        </form>

                        {/* Kết Quả Tìm Kiếm */}
                        <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 border-b pb-2">
                            Kết Quả ({results.length > 0 ? results.length : 
                            actorInfo ? (actorInfo.error ? '0' : 'Diễn viên') : (loading ? 'Đang tìm...' : '0')})
                        </h3>
                        
                        {loading && (
                            <div className="flex justify-center items-center p-8">
                                <Loader2 className="w-8 h-8 mr-3 text-blue-500 animate-spin" />
                                <span className="text-lg text-gray-600 dark:text-gray-400">Đang tìm kiếm...</span>
                            </div>
                        )}

                        {/* Hiển thị lỗi nếu có (Dùng actorInfo.error như một cách để hiển thị lỗi chung) */}
                        {actorInfo && actorInfo.error && (
                            <div className="p-4 bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-600 text-red-700 dark:text-red-300 rounded-lg flex items-center">
                                <AlertTriangle className="w-5 h-5 mr-2" />
                                {actorInfo.error}
                            </div>
                        )}

                        {/* Hiển thị kết quả tìm kiếm diễn viên/vai diễn */}
                        {actorInfo && !actorInfo.error && actorInfo.actor && (
                            <div className="p-4 mb-4 bg-yellow-50 dark:bg-yellow-900/50 border border-yellow-300 dark:border-yellow-700 rounded-lg">
                                <h4 className="text-xl font-semibold text-yellow-800 dark:text-yellow-200 flex items-center">
                                    <User className="w-5 h-5 mr-2" /> Nhận diện Diễn viên/Vai Diễn: {actorInfo.actor}
                                </h4>
                                <p className="mt-2 text-gray-700 dark:text-gray-300">
                                    Độ chính xác: {actorInfo.similarity ? (actorInfo.similarity * 100).toFixed(2) + '%' : 'N/A'}
                                </p>
                                <p className="mt-2 text-gray-700 dark:text-gray-300">
                                    Diễn viên {actorInfo.actor} đã tham gia các phim sau:
                                </p>
                                {/* HIỂN THỊ PHIM DẠNG GRID CHO DIỄN VIÊN */}
                                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-3">
                                    {results.map((movie, idx) => (
                                        <div
                                            key={idx}
                                            onClick={() => handleSetSelected(movie)}
                                            className="bg-gray-100 dark:bg-gray-700 rounded-lg p-2 shadow-md hover:shadow-lg transition cursor-pointer group"
                                        >
                                            <img
                                                src={getPosterUrl(movie)}
                                                onError={(e) => {
                                                    e.target.onerror = null; 
                                                    e.target.src = BaseURL + "150x225/0F275F/ffffff?text=Poster+Not+Found";
                                                }}
                                                alt={movie.title}
                                                className="w-full h-48 object-cover rounded-md mb-2 group-hover:opacity-80 transition"
                                            />
                                            <p className="text-gray-900 dark:text-white font-semibold text-sm truncate">
                                                {movie.title}
                                            </p>
                                            <p className="text-blue-600 dark:text-blue-300 text-xs truncate">
                                                Vai: {movie.role_name}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Hiển thị danh sách kết quả phim (Dạng lưới - Grid) */}
                        <div className="space-y-4">
                            {/* CHỈ HIỂN THỊ KẾT QUẢ DẠNG GRID KHI results CÓ DỮ LIỆU VÀ KHÔNG PHẢI KẾT QUẢ DIỄN VIÊN (actorInfo.actor = false) */}
                            {!loading && results.length > 0 && !(actorInfo && actorInfo.actor) && (
                                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                                    {results.map((item, idx) => (
                                        <div
                                            key={idx}
                                            className="group cursor-pointer relative rounded-lg shadow-lg overflow-hidden transition-all hover:scale-[1.03] hover:shadow-xl"
                                            onClick={() => handleSetSelected(item)}
                                        >
                                            <img
                                                src={getPosterUrl(item)}
                                                onError={(e) => {
                                                    e.target.onerror = null;
                                                    // Nếu poster không load được, thử dùng poster gốc nếu có, nếu không dùng fallback chung
                                                    e.target.src = item.poster || (BaseURL + "150x225/0F275F/ffffff?text=Poster+Not+Found");
                                                }}
                                                alt={item.title}
                                                className="w-full h-72 object-cover rounded-lg"
                                            />
                                            <div className="absolute bottom-0 left-0 right-0 bg-black/70 text-white text-sm px-3 py-2 opacity-100 transition-opacity">
                                                <p className="font-semibold truncate">{item.title}</p>
                                                <p className="text-xs text-blue-300">
                                                    TĐ: {item.similarity ? (item.similarity * 100).toFixed(2) + '%' : 'N/A'}
                                                </p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                            
                            {/* Điều kiện kiểm tra không có kết quả */}
                            {!loading && results.length === 0 && !actorInfo && (
                                <p className="text-center text-gray-500 dark:text-gray-400 p-8 border border-dashed rounded-lg">
                                    {tab === "image" && !file
                                        ? "Vui lòng tải lên một hình ảnh để bắt đầu tìm kiếm."
                                        : tab === "text" && !query
                                        ? "Vui lòng nhập từ khóa để bắt đầu tìm kiếm."
                                        : "Không tìm thấy kết quả nào. Hãy thử lại với từ khóa hoặc hình ảnh khác."}
                                </p>
                            )}
                        </div>

                        {/* Chi tiết Phim được Chọn (Modal-like view) */}
                        {selected && (
                            <div className="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex justify-center items-center z-50 p-4">
                                <div className="bg-white dark:bg-gray-800 rounded-xl max-w-4xl w-full p-6 shadow-2xl relative overflow-y-auto max-h-[90vh]">
                                    <button
                                        onClick={() => setSelected(null)}
                                        className="absolute top-4 right-4 text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors p-1 rounded-full bg-gray-100 dark:bg-gray-700"
                                    >
                                        <X className="w-6 h-6" />
                                    </button>

                                    <div className="flex flex-col md:flex-row gap-6">
                                        <div className="flex-shrink-0">
                                            <img
                                                src={getPosterUrl(selected)}
                                                alt={selected.original_title}
                                                className="w-48 h-72 object-cover rounded-lg shadow-xl border-4 border-white dark:border-gray-700"
                                                style={{ maxHeight: "80vh" }}
                                                onError={(e) => {
                                                    e.target.onerror = null; 
                                                    e.target.src = selected.poster || (BaseURL + "150x225/0F275F/ffffff?text=Poster+Not+Found");
                                                }}
                                            />
                                        </div>
                                        
                                        <div className="flex-grow">
                                            <h2 className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-2">
                                                {selected.title}
                                            </h2>
                                            
                                            <p className="text-gray-700 dark:text-gray-300 mb-2 text-sm">
                                                <b>Tên gốc:</b> {selected.original_title || "Đang cập nhật"}
                                            </p>
                                            <p className="text-gray-700 dark:text-gray-300 text-sm mb-4">
                                                <b>Ngày công chiếu:</b> {selected.release_date || "Đang cập nhật"}
                                            </p>
                                            
                                            <p className="text-gray-700 dark:text-gray-300 mb-4">
                                                <b>Đạo diễn:</b> {selected.director || "Đang cập nhật"}
                                            </p>

                                            <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg mb-4">
                                                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Tóm tắt</h3>
                                                <p className="text-gray-800 dark:text-gray-200 leading-relaxed italic">
                                                    {selected.overview || "Tóm tắt đang được cập nhật."}
                                                </p>
                                            </div>

                                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                                                <p className="text-gray-600 dark:text-gray-400">
                                                    <b>Thể loại:</b> <span className="text-gray-800 dark:text-gray-200">{selected.genres_vn || "Không rõ"}</span>
                                                </p>
                                                <p className="text-gray-600 dark:text-gray-400">
                                                    <b>Diễn viên chính:</b> <span className="text-gray-800 dark:text-gray-200">{selected.stars || "Không rõ"}</span>
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                      
                    </div>
                </div>
            </main>
        </div>
    );
}

export default Search;