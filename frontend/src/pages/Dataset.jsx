function Dataset() {
  return (
    <div className="p-6 text-center">
      <h1 className="text-2xl font-bold mb-4 text-blue-600">🎞️ Movie Dataset</h1>
      <p className="text-gray-700 mb-4">
        Browse through the available movie dataset used for training and testing the AI model.
      </p>
      <div className="border rounded-xl p-4 shadow-md bg-gray-50">
        <p className="text-sm text-gray-500">Dataset preview will be displayed here once connected to the backend.</p>
      </div>
    </div>
  );
}

export default Dataset;
