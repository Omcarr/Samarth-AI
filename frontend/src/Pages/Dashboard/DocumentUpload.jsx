import React, { useState, useRef } from 'react';
import { Upload, Check, FileText } from 'lucide-react';

const DocumentUpload = () => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const fileInputRef = useRef(null);

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    setSelectedFiles(files);
  };

  const handleSubmit = async () => {
    const formData = new FormData();

    selectedFiles.forEach((file) => {
      formData.append('documents', file);
    });

    try {
      const response = await fetch('https://815d-117-96-43-108.ngrok-free.app/pdfupload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        alert('Documents uploaded successfully!');
        setSelectedFiles([]); // Clear files after successful upload
      } else {
        alert('Document upload failed');
      }
    } catch (error) {
      console.error('Error submitting documents:', error);
      alert('Error uploading documents');
    }
  };

  return (
    <div className="h-screen w-full flex items-center justify-center  bg-[#EEEEE8] text-gray-800">
      <div className="w-full max-w-xl rounded-2xl overflow-hidden bg-white shadow-2xl">
        {/* Header */}
        <div className="p-6 bg-zinc-900">
          <h1 className="text-3xl font-bold text-white flex items-center">
            <FileText className="mr-3" />
            Policy Management
          </h1>
        </div>

        {/* Content: Upload Files */}
        <div className="p-6 space-y-4">
          <h2 className="text-2xl font-semibold text-gray-800">
            Upload Documents
          </h2>
          <input
            type="file"
            ref={fileInputRef}
            multiple
            onChange={handleFileUpload}
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current.click()}
            className="w-full py-4 border-2 border-dashed border-zinc-700 text-zinc-900 rounded-xl hover:bg-blue-50 transition-colors flex items-center justify-center space-x-2"
          >
            <Upload className="mr-2" />
            <span>Upload Documents</span>
          </button>

          {selectedFiles.length > 0 && (
            <div className="mt-4 space-y-2">
              {selectedFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center p-3 rounded-lg space-x-2 bg-blue-50"
                >
                  <Check className="text-green-500" />
                  <span className="text-gray-700">{file.name}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="px-6 pb-6">
          <button
            onClick={handleSubmit}
            disabled={selectedFiles.length === 0}
            className="w-full border border-black text-black  py-3 rounded-lg  disabled:opacity-50 transition-colors"
          >
            Submit Documents
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentUpload;
