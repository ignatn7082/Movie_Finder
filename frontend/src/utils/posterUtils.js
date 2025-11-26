// src/utils/posterUtils.js

export const fallbackPoster = (title) => {
    if (!title) return "posters/default_poster.jpg"; 
    const fallbackName = title
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .replace(/\s+/g, "_")
        .replace(/[^a-z0-9_]/g, '') 
        + ".jpg";
    return "posters/" + fallbackName;
};

export const cleanPath = (path) => {
    if (!path) return "";
    return path.replace(/\/+$/, '');
};

export const cleanLeadingSlash = (path) => {
    if (!path) return "";
    return path.replace(/^\/+/, '');
};

export const getPosterUrl = (result, API_HOST, BaseURL) => {
    if (result.poster) {
        let posterPath = result.poster;
        
        if (posterPath.startsWith('http://') || posterPath.startsWith('https://')) {
            return posterPath;
        }

        if (posterPath.startsWith(API_HOST)) {
            posterPath = posterPath.substring(API_HOST.length);
        }
        if (posterPath.startsWith('/static/')) {
            posterPath = posterPath.substring('/static/'.length);
        } else if (posterPath.startsWith('static/')) {
            posterPath = posterPath.substring('static/'.length);
        }

        posterPath = cleanLeadingSlash(posterPath); 
        return cleanPath(BaseURL) + "/" + posterPath;
    } 

    const fallbackPath = fallbackPoster(result.title || result.original_title);
    return cleanPath(BaseURL) + "/" + cleanLeadingSlash(fallbackPath);
};