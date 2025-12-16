// components/search/Search.jsx
import React, { useState } from "react";
import { Loader2, Sparkles } from "lucide-react";

import Navbar from "../components/Navbar";
import SearchSidebar from "../components/search/SearchSidebar";
import SearchTabs from "../components/search/SearchTabs";
import ImageSearchInput from "../components/search/ImageSearchInput";
import TextSearchInput from "../components/search/TextSearchInput";
import SearchResults from "../components/search/SearchResults";
import MovieDetailModal from "../components/search/MovieDetailModal";


const API_HOST = "http://localhost:8000";
const BaseURL = "http://localhost:8000/static/";

function Search() {
  const [tab, setTab] = useState("image"); // "image" | "text"
  const [searchMode, setSearchMode] = useState("actor"); // "actor" | "content" (chỉ dùng khi tab=image)
  const [query, setQuery] = useState("");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [actorInfo, setActorInfo] = useState(null);
  const [selected, setSelected] = useState(null);
  const [errorMsg, setErrorMsg] = useState("");


  const getPosterUrl = (movie) => {
    if (!movie?.poster) return BaseURL + "300x450/1a1a1a/ffffff?text=No+Poster";
    if (movie.poster.startsWith("http")) return movie.poster;
    return BaseURL + movie.poster.replace(/^\/+/, "");
  };

  const handleTabChange = (newTab) => {
    setTab(newTab);
    setQuery("");
    setFile(null);
    setPreview(null);
    setResults([]);
    setActorInfo(null);
    setSelected(null);
    if (newTab === "text") setSearchMode("actor"); // reset mode khi chuyển sang text
  };

  // const handleSearch = async (e) => {
  //   e.preventDefault();
  //   if (tab === "image" && !file) return;
  //   if (tab === "text" && !query.trim()) return;

  //   setLoading(true);
  //   setResults([]);
  //   setActorInfo(null);
  //   setSelected(null);

  //   try {
  //     let res, data;

  //     if (tab === "image" && file) {
  //       const formData = new FormData();
  //       formData.append("file", file);
  //       formData.append("mode", searchMode);

  //       res = await fetch(`${API_HOST}/search/image`, {
  //         method: "POST",
  //         body: formData,
  //       });
  //       data = await res.json();

  //       if (data.status === "success") {
  //         if (data.search_mode === "actor") {
  //           setActorInfo({
  //             detected_actor: data.detected_actor,
  //             actor_filmography: data.actor_filmography || [],
  //             actor_similarities: data.actor_similarities || [],
  //           });
  //         }
  //         setResults(data.movies || []);
  //       }
  //     } 
  //     else if (tab === "text" && query.trim()) {
  //       res = await fetch(`${API_HOST}/search/text?query=${encodeURIComponent(query)}`);
  //       data = await res.json();
  //       setResults(data.results || data.movies || []);
  //     }
  //   } catch (err) {
  //     console.error("Lỗi tìm kiếm:", err);
  //   } finally {
  //     setLoading(false);
  //   }
  // };

  const handleSearch = async (e) => {
  e.preventDefault();

  // Reset lỗi cũ
  setErrorMsg("");

  // === VALIDATE INPUT ===
  if (tab === "image" && !file) {
    setErrorMsg(
      searchMode === "actor"
        ? "⚠️ Vui lòng tải lên ảnh diễn viên trước khi tìm kiếm."
        : "⚠️ Vui lòng tải lên ảnh cảnh phim trước khi tìm kiếm."
    );
    return;
  }

  if (tab === "text" && !query.trim()) {
    setErrorMsg("⚠️ Vui lòng nhập nội dung tìm kiếm.");
    return;
  }

  // === HỢP LỆ → TIẾP TỤC ===
  setLoading(true);
  setResults([]);
  setActorInfo(null);
  setSelected(null);

  try {
    let res, data;

    if (tab === "image" && file) {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("mode", searchMode);

      res = await fetch(`${API_HOST}/search/image`, {
        method: "POST",
        body: formData,
      });
      data = await res.json();

      if (data.status === "success") {
        if (data.search_mode === "actor") {
          setActorInfo({
            detected_actor: data.detected_actor,
            actor_filmography: data.actor_filmography || [],
            actor_similarities: data.actor_similarities || [],
          });
        }
        setResults(data.movies || []);
      }
    } else if (tab === "text") {
      res = await fetch(
        `${API_HOST}/search/text?query=${encodeURIComponent(query)}`
      );
      data = await res.json();
      setResults(data.results || data.movies || []);
    }
  } catch (err) {
    console.error("Lỗi tìm kiếm:", err);
    setErrorMsg("❌ Có lỗi xảy ra trong quá trình tìm kiếm.");
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:to-indigo-950">
      <Navbar />

      <main className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-6xl font-extrabold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
            Công cụ tìm kiếm phim
            
          </h1>
          {/* <p className="text-xl text-gray-600 dark:text-gray-300">
            Dùng AI để tìm phim bằng <strong className="text-indigo-600">văn bản</strong> hoặc{" "}
            <strong className="text-purple-600">hình ảnh</strong>
          </p> */}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-3">
            <SearchSidebar tab={tab} onExampleClick={(q) => { setTab("text"); setQuery(q); }} />
          </div>

          {/* Main Content */}
          <div className="lg:col-span-9">
            <div className="bg-white/80 dark:bg-gray-800/90 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 dark:border-gray-700 p-8">
              {/* Tab chuyển đổi */}
              <SearchTabs tab={tab} setTab={handleTabChange} />

              {/* Form tìm kiếm */}
              <form onSubmit={handleSearch} className="mt-10">
                {tab === "image" ? (
                  <ImageSearchInput
                    file={file}
                    preview={preview}
                    searchMode={searchMode}
                    setSearchMode={setSearchMode}
                    setFile={setFile}
                    setPreview={setPreview}
                  />
                ) : (
                  <TextSearchInput query={query} setQuery={setQuery} />
                )}

                <button
                  type="submit"
                  // disabled={loading || (tab === "image" && !file) || (tab === "text" && !query.trim())}
                  disabled={loading}
                  className="mt-10 w-full py-6 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-extrabold text-2xl rounded-3xl shadow-2xl transform hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-4"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-8 h-8 animate-spin" />
                      Đang tìm kiếm...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-8 h-8" />
                      {tab === "image"
                        ? searchMode === "actor" ? "Tìm Diễn Viên Bằng Ảnh" : "Tìm Phim Theo Nội Dung"
                        : "Tìm Phim Bằng Văn Bản"}
                    </>
                  )}
                </button>
                {errorMsg && (
  <div className="mt-6 text-center text-red-600 font-bold text-lg">
    {errorMsg}
  </div>
)}

              </form>

              {/* Kết quả */}
              <div className="mt-12">
                <SearchResults
                  loading={loading}
                  results={results}
                  actorInfo={actorInfo}
                  searchMode={tab === "image" ? searchMode : null}
                  onSelectMovie={setSelected}
                  getPosterUrl={getPosterUrl}
                  BaseURL={BaseURL}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Modal chi tiết phim */}
        <MovieDetailModal
 overestimate          movie={selected}
          onClose={() => setSelected(null)}
          getPosterUrl={getPosterUrl}
        />
      </main>
    </div>
  );
}

export default Search;