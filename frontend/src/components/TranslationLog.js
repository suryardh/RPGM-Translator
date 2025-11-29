import React, { useEffect, useRef } from "react";
const TranslationLog = ({ logs }) => {
  const logContainerRef = useRef(null);
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs]);
  const formatLogEntry = (log, index) => {
    if (typeof log === "string") {
      return log;
    }
    if (typeof log === "object" && log !== null) {
      switch (log.type) {
        case "dialog":
        case "object":
        case "common_event":
          return `------------------------------------------------\n${
            log.type
          } (${String(log.index).padStart(2, "0")}/${log.total}) - File: ${
            log.file
          }\nRaw: ${log.raw}\nTranslated: ${
            log.translated
          }\n------------------------------------------------`;
        case "anomaly":
          return `Anomaly found at (${log.path}): ${log.raw}`;
        case "error":
          return `ERROR: ${log.message}`;
        default:
          return JSON.stringify(log);
      }
    }
    return String(log);
  };
  const formattedLogs = logs
    .map((log, index) => formatLogEntry(log, index))
    .join("\n\n");
  return (
    <div className="mt-6">
      <h3 className="text-lg font-medium text-gray-900 mb-2">
        Translation Log
      </h3>
      <div
        ref={logContainerRef}
        className="log-container bg-gray-50 border border-gray-200 rounded-md p-3 text-sm text-gray-700"
      >
        {formattedLogs ? formattedLogs : "No logs yet..."}
      </div>
    </div>
  );
};
export default TranslationLog;
