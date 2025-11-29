import React, { useState, useEffect } from "react";
import axios from "axios";
const EditModal = ({ jobId, onSave, onClose }) => {
  const [editedLogs, setEditedLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  useEffect(() => {
    const fetchLogs = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/translated_data/${jobId}`);
        setEditedLogs(response.data.logs);
      } catch (err) {
        setError("Failed to load translation logs. Please try again.");
        console.error("Error fetching logs:", err);
      } finally {
        setLoading(false);
      }
    };
    if (jobId) {
      fetchLogs();
    }
  }, [jobId]);
  const handleTranslationChange = (index, newTranslation) => {
    const updatedLogs = [...editedLogs];
    updatedLogs[index] = { ...updatedLogs[index], translated: newTranslation };
    setEditedLogs(updatedLogs);
  };
  const handleSave = async () => {
    try {
      setSaving(true);
      const response = await axios.post(`/api/edit/${jobId}`, {
        logs: editedLogs,
      });
      if (response.data.download_url) {
        onSave(response.data.download_url);
      }
    } catch (err) {
      setError("Failed to save translations. Please try again.");
      console.error("Error saving translations:", err);
    } finally {
      setSaving(false);
    }
  };
  const editableLogs = editedLogs.filter(
    (log) => log.type !== "error" && log.type !== "anomaly"
  );
  if (loading) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center">
        <div className="text-white text-xl">Loading translation data...</div>
      </div>
    );
  }
  if (error) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center">
        <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
          <div className="text-red-500 mb-4">{error}</div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-300 text-gray-800 rounded-md hover:bg-gray-400"
          >
            Close
          </button>
        </div>
      </div>
    );
  }
  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-4/5 lg:w-11/12 shadow-lg rounded-md bg-white">
        <div className="mt-3 text-center">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Edit Translations
          </h3>
          <div className="mt-2 px-7 py-3 max-h-96 overflow-y-auto text-left">
            {editableLogs.map((log, index) => (
              <div
                key={index}
                className="mb-6 p-4 border border-gray-200 rounded-lg"
              >
                <div className="font-semibold text-gray-700 mb-2">
                  {log.file} - {log.type} ({log.index}/{log.total})
                </div>
                <div className="space-y-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-600">
                      Raw:
                    </label>
                    <div className="p-2 bg-gray-100 rounded text-sm">
                      {log.raw}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-600">
                      Translated:
                    </label>
                    <textarea
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      rows="2"
                      value={log.translated}
                      onChange={(e) =>
                        handleTranslationChange(index, e.target.value)
                      }
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="items-center px-4 py-3 flex justify-end space-x-2">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-300 text-gray-800 text-base font-medium rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-300"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-4 py-2 bg-blue-500 text-white text-base font-medium rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-300 disabled:opacity-50"
            >
              {saving ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
export default EditModal;
