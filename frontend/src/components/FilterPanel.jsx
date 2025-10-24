export default function FilterPanel({ filters, onFilterChange }) {
  const handleChange = (e) => {
    onFilterChange({ ...filters, [e.target.name]: e.target.value });
  };

  return (
    <div className="flex flex-wrap gap-3 border-b pb-3 mb-4">
      <select
        name="genre"
        onChange={handleChange}
        className="p-2 rounded-md border bg-white dark:bg-gray-800"
      >
        <option value="">🎭 Thể loại</option>
        <option value="Drama">Drama</option>
        <option value="Action">Action</option>
        <option value="Comedy">Comedy</option>
      </select>

      <select
        name="director"
        onChange={handleChange}
        className="p-2 rounded-md border bg-white dark:bg-gray-800"
      >
        <option value="">🎬 Đạo diễn</option>
        <option value="Trịnh Công Sơn">Trịnh Công Sơn</option>
        <option value="Victor Vũ">Victor Vũ</option>
      </select>

      <select
        name="year"
        onChange={handleChange}
        className="p-2 rounded-md border bg-white dark:bg-gray-800"
      >
        <option value="">📅 Năm</option>
        {[2025, 2024, 2023, 2022, 2021].map((y) => (
          <option key={y} value={y}>
            {y}
          </option>
        ))}
      </select>
    </div>
  );
}
