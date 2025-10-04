import React, { useState, useCallback } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle, Loader } from 'lucide-react';

interface DocumentUploadProps {
  onUploadComplete?: (result: any) => void;
  maxFileSize?: number; // in MB
  acceptedTypes?: string[];
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUploadComplete,
  maxFileSize = 50,
  acceptedTypes = ['.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg']
}) => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResults, setUploadResults] = useState<any[]>([]);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFiles = Array.from(e.dataTransfer.files);
      validateAndAddFiles(droppedFiles);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      validateAndAddFiles(selectedFiles);
    }
  };

  const validateAndAddFiles = (newFiles: File[]) => {
    const validFiles: File[] = [];
    const errors: string[] = [];

    newFiles.forEach(file => {
      // Check file size
      if (file.size > maxFileSize * 1024 * 1024) {
        errors.push(`${file.name}: File size exceeds ${maxFileSize}MB limit`);
        return;
      }

      // Check file type
      const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!acceptedTypes.includes(fileExt)) {
        errors.push(`${file.name}: Unsupported file type. Accepted: ${acceptedTypes.join(', ')}`);
        return;
      }

      validFiles.push(file);
    });

    if (errors.length > 0) {
      alert('Some files were rejected:\n' + errors.join('\n'));
    }

    setFiles(prev => [...prev, ...validFiles]);
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;

    setUploading(true);
    setUploadResults([]);

    try {
      const formData = new FormData();

      files.forEach((file, index) => {
        formData.append('files', file);
      });

      const response = await fetch('/api/unstructured/batch-process', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        setUploadResults([{ success: true, message: result.message, files: result.files }]);
        setFiles([]);
        onUploadComplete?.(result);
      } else {
        setUploadResults([{ success: false, message: result.error || 'Upload failed' }]);
      }
    } catch (error) {
      setUploadResults([{ success: false, message: 'Network error occurred' }]);
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Document Upload</h2>
        <p className="text-gray-600">
          Upload documents for processing and analysis. Supported formats: {acceptedTypes.join(', ')}
        </p>
      </div>

      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <div className="mb-4">
          <p className="text-lg font-medium text-gray-700 mb-2">
            Drop files here or click to browse
          </p>
          <p className="text-sm text-gray-500">
            Maximum file size: {maxFileSize}MB per file
          </p>
        </div>
        <input
          type="file"
          multiple
          accept={acceptedTypes.join(',')}
          onChange={handleFileSelect}
          className="hidden"
          id="file-upload"
        />
        <label
          htmlFor="file-upload"
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 cursor-pointer transition-colors"
        >
          Choose Files
        </label>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-medium text-gray-800 mb-3">Selected Files</h3>
          <div className="space-y-2">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-md"
              >
                <div className="flex items-center space-x-3">
                  <FileText className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="font-medium text-gray-800">{file.name}</p>
                    <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="text-red-500 hover:text-red-700 p-1"
                  disabled={uploading}
                >
                  ×
                </button>
              </div>
            ))}
          </div>

          <div className="mt-4 flex justify-end">
            <button
              onClick={uploadFiles}
              disabled={uploading}
              className="inline-flex items-center px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {uploading ? (
                <>
                  <Loader className="animate-spin h-4 w-4 mr-2" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4 mr-2" />
                  Upload {files.length} File{files.length !== 1 ? 's' : ''}
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Upload Results */}
      {uploadResults.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-medium text-gray-800 mb-3">Upload Results</h3>
          <div className="space-y-2">
            {uploadResults.map((result, index) => (
              <div
                key={index}
                className={`p-3 rounded-md flex items-center space-x-3 ${
                  result.success
                    ? 'bg-green-50 border border-green-200'
                    : 'bg-red-50 border border-red-200'
                }`}
              >
                {result.success ? (
                  <CheckCircle className="h-5 w-5 text-green-600" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-red-600" />
                )}
                <div>
                  <p className={`font-medium ${
                    result.success ? 'text-green-800' : 'text-red-800'
                  }`}>
                    {result.success ? 'Success' : 'Error'}
                  </p>
                  <p className={`text-sm ${
                    result.success ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {result.message}
                  </p>
                  {result.files && (
                    <p className="text-sm text-gray-600 mt-1">
                      Files queued: {result.files.join(', ')}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;