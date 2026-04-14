import React from 'react';
import { Upload, Image as ImageIcon } from 'lucide-react';

export default function UploadZone({ onFileSelect, selectedFile }) {
  return (
    <div className="w-full">
      <label
        htmlFor="file-upload"
        className={`relative flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-2xl cursor-pointer transition-all duration-300 ${
          selectedFile ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-white hover:border-blue-400 hover:bg-gray-50'
        }`}
      >
        <div className="flex flex-col items-center justify-center pb-8 pt-5">
          {selectedFile ? (
            <ImageIcon className="w-12 h-12 text-blue-500 mb-3" />
          ) : (
            <Upload className="w-12 h-12 text-gray-400 mb-3" />
          )}
          <p className={`text-sm font-medium ${selectedFile ? 'text-blue-600' : 'text-gray-500'}`}>
            {selectedFile ? selectedFile.name : "Click to upload or drag and"}
          </p>
        </div>
      </label>
    </div>
  );
}