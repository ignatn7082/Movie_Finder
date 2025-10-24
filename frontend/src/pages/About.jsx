function About() {
  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-3 text-blue-600">About This Project</h1>
      <p className="text-gray-700 leading-relaxed">
        This web application is part of a graduation thesis project. It integrates a backend system built with FastAPI 
        and an AI-based image search pipeline that uses CLIP + FAISS for feature extraction and similarity search.
      </p>
      <p className="mt-3 text-gray-700">
        Author: <strong>LE NGOC TAN</strong> — Can Tho University
      </p>
    </div>
  );
}

export default About;
