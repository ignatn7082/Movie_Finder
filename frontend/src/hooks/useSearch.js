import { useState } from "react";


const useSearch = () => {
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
            setSelected(null);
            setResults([]);
            setActorInfo(null);
        } else {
            setFile(null);
            setPreview(null);
        }
    };

    const handleSetSelected = (item) => {
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
                formData.append("model", selectedImageModel);

                res = await fetch(`${API_HOST}/search/image`, {
                    method: "POST",
                    body: formData,
                });
                // read raw text first to avoid JSON parse errors on 404/empty responses
                const raw = await res.text();
                if (!res.ok) {
                    // include server message if any
                    throw new Error(raw || res.statusText || `HTTP ${res.status}`);
                }
                let data = {};
                try {
                    data = raw ? JSON.parse(raw) : {};
                } catch (e) {
                    console.warn("Response is not valid JSON:", raw);
                    data = {};
                }

                if (data.status === "success") {
                    setResults(Array.isArray(data.movies) ? data.movies : []);
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

    const handleExampleClick = (exampleQuery) => {
        if (tab === 'text') {
            setTab('text');
            setQuery(exampleQuery);
            setActorInfo(null);
            setResults([]);
            setSelected(null);
        }
    };

    return {
        tab,
        setTab,
        selectedImageModel,
        setSelectedImageModel,
        query,
        setQuery,
        file,
        setFile,
        preview,
        setPreview,
        results,
        setResults,
        actorInfo,
        setActorInfo,
        loading,
        setLoading,
        selected,
        setSelected,
        handleFileChange,
        handleSetSelected,
        handleSearch,
        handleExampleClick,
    };
};

export default useSearch;