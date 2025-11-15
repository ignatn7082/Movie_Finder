export default function SearchResultCard({ item, onClick }) {
  const BaseURL = "http://localhost:8000/static/";
  return (
    <div
      onClick={onClick}
      className="relative group cursor-pointer"
    >
      <img
        src={  movie.poster 
                         ? BaseURL + movie.poster 
                         : BaseURL + "posters/default_poster.jpg"}
        alt={item.title}
        className="w-full h-64 object-contain rounded-lg shadow-md group-hover:scale-105 transition-transform duration-300"
      />
      <div className="absolute bottom-0 bg-black/60 text-white text-sm w-full px-2 py-1 rounded-b-lg opacity-0 group-hover:opacity-100 transition">
        {item.title}
      </div>
    </div>
  );
}
