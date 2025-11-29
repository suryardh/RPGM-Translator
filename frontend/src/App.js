import React, { useState } from "react";
import FileUpload from "./components/FileUpload";
import LanguageSelector from "./components/LanguageSelector";
import ProgressBar from "./components/ProgressBar";
import TranslationLog from "./components/TranslationLog";
import EditModal from "./components/EditModal";
import axios from "axios";

function App() {
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000'

  const [currentStep, setCurrentStep] = useState(1);
  const [sourceLanguage, setSourceLanguage] = useState("it");
  const [targetLanguage, setTargetLanguage] = useState("id");
  const [translationProgress, setTranslationProgress] = useState(0);
  const [translationLogs, setTranslationLogs] = useState([]);
  const [jobId, setJobId] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [error, setError] = useState(null);

  const handleFileUpload = async (uploadedFile) => {
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", uploadedFile);
      const response = await axios.post("/api/upload", formData);
      setJobId(response.data.job_id);
      setCurrentStep(2);
    } catch (err) {
      setError("Failed to upload file. Please try again.");
      console.error("Upload error:", err);
    }
  };

  const handleTranslate = async () => {
    if (!jobId) return;
    setTranslationLogs([]);
    setError(null);
    
    try {
      const response = await axios.post('/api/translate', {
        job_id: jobId,
        source_language: sourceLanguage,
        target_language: targetLanguage
      });
      
      if (response.data.status === 'error') {
        setError(response.data.message);
        return;
      }
      
      const pollInterval = setInterval(async () => {
        try {
          const pollResponse = await axios.get(`/api/status/${jobId}`);
          
          if (pollResponse.data.status === 'completed') {
            clearInterval(pollInterval);
            setTranslationProgress(100);
            setTranslationLogs(pollResponse.data.logs);
            
            const absoluteDownloadUrl = `${BACKEND_URL}${pollResponse.data.download_url}`;
            setDownloadUrl(absoluteDownloadUrl);
            
            setCurrentStep(3);
          } else if (pollResponse.data.status === 'error') {
            clearInterval(pollInterval);
            setError(pollResponse.data.message);
          } else {
            const progress = pollResponse.data.total_files > 0 
              ? (pollResponse.data.current_file / pollResponse.data.total_files) * 100 
              : 0;
            setTranslationProgress(progress);
            setTranslationLogs(pollResponse.data.logs);
          }
        } catch (err) {
          clearInterval(pollInterval);
          setError('Failed to get translation status. Please try again.');
          console.error('Status polling error:', err);
        }
      }, 1000);
      
    } catch (err) {
      setError('Failed to start translation. Please try again.');
      console.error('Translation error:', err);
    }
  };

  const handleDownload = () => {
    if (downloadUrl) {
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.setAttribute("download", "");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleEdit = () => {
    setShowEditModal(true);
  };
  const handleSaveEdit = (downloadUrl) => {
    setDownloadUrl(downloadUrl);
    setShowEditModal(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">
          RPG Maker File Translator
        </h1>
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}
        {currentStep === 1 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">
              Step 1: Upload Your RPG Maker File
            </h2>
            <FileUpload onFileUpload={handleFileUpload} />
          </div>
        )}
        {currentStep === 2 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">
              Step 2: Select Translation Languages
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <LanguageSelector
                label="Source Language"
                selectedLanguage={sourceLanguage}
                onLanguageChange={setSourceLanguage}
              />
              <LanguageSelector
                label="Target Language"
                selectedLanguage={targetLanguage}
                onLanguageChange={setTargetLanguage}
              />
            </div>
            <button
              onClick={handleTranslate}
              className="mt-6 bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            >
              Start Translation
            </button>
            {translationProgress > 0 && (
              <div className="mt-6">
                <ProgressBar progress={translationProgress} />
                <TranslationLog logs={translationLogs} />
              </div>
            )}
          </div>
        )}
        {currentStep === 3 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">
              Translation Complete!
            </h2>
            <div className="flex space-x-4">
              <button
                onClick={handleDownload}
                className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              >
                Download Translated File
              </button>
              <button
                onClick={handleEdit}
                className="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              >
                Edit Translation
              </button>
            </div>
            <TranslationLog logs={translationLogs} />
          </div>
        )}
        {showEditModal && (
          <EditModal
            jobId={jobId}
            onSave={handleSaveEdit}
            onClose={() => setShowEditModal(false)}
          />
        )}
      </div>
    </div>
  );
}

export default App;
