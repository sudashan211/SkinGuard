import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Camera, X, Image as ImageIcon, Loader2 } from 'lucide-react'
import { formatFileSize } from '@/utils/helpers'

interface DiagnosticUploaderProps {
  onImageSelect: (file: File) => void
  isLoading?: boolean
}

export default function DiagnosticUploader({ onImageSelect, isLoading }: DiagnosticUploaderProps) {
  const [preview, setPreview] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setError(null)

    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0]
      if (rejection.errors[0]?.code === 'file-too-large') {
        setError('File is too large. Maximum size is 10MB.')
      } else if (rejection.errors[0]?.code === 'file-invalid-type') {
        setError('Invalid file type. Please upload a JPG, JPEG, or PNG image.')
      } else {
        setError('Failed to upload file. Please try again.')
      }
      return
    }

    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0]
      setSelectedFile(file)
      
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
      
      onImageSelect(file)
    }
  }, [onImageSelect])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false,
    disabled: isLoading,
  })

  const handleCameraCapture = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
      
      onImageSelect(file)
    }
  }

  const clearImage = () => {
    setPreview(null)
    setSelectedFile(null)
    setError(null)
  }

  return (
    <div className="space-y-4">
      {!preview ? (
        <>
          {/* Dropzone */}
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400'}
              ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <input {...getInputProps()} />
            <Upload className="mx-auto mb-4 text-gray-400" size={48} />
            <p className="text-lg font-medium text-gray-700 mb-2">
              {isDragActive ? 'Drop image here' : 'Drag & drop your image here'}
            </p>
            <p className="text-sm text-gray-500 mb-4">
              or click to browse files
            </p>
            <p className="text-xs text-gray-400">
              Supported formats: JPG, JPEG, PNG (Max 10MB)
            </p>
          </div>

          {/* Camera Capture (Mobile) */}
          <div className="relative">
            <input
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handleCameraCapture}
              className="hidden"
              id="camera-input"
              disabled={isLoading}
            />
            <label
              htmlFor="camera-input"
              className={`
                btn btn-secondary w-full flex items-center justify-center
                ${isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              <Camera className="mr-2" size={20} />
              Take Photo with Camera
            </label>
          </div>
        </>
      ) : (
        /* Preview */
        <div className="space-y-4">
          <div className="relative rounded-lg overflow-hidden bg-gray-100">
            <img
              src={preview}
              alt="Preview"
              className="w-full h-auto max-h-96 object-contain"
            />
            {!isLoading && (
              <button
                onClick={clearImage}
                className="absolute top-2 right-2 p-2 bg-white rounded-full shadow-lg hover:bg-gray-100 transition-colors"
              >
                <X size={20} />
              </button>
            )}
            {isLoading && (
              <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                <div className="text-center text-white">
                  <Loader2 className="animate-spin mx-auto mb-2" size={48} />
                  <p className="text-lg font-medium">Analyzing image...</p>
                  <p className="text-sm">This may take up to 30 seconds</p>
                </div>
              </div>
            )}
          </div>

          {selectedFile && !isLoading && (
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <ImageIcon className="text-gray-400" size={24} />
                <div>
                  <p className="text-sm font-medium text-gray-700">
                    {selectedFile.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="p-3 bg-danger-50 border border-danger-200 rounded-lg">
          <p className="text-sm text-danger-600">{error}</p>
        </div>
      )}

      {/* Guidelines */}
      <div className="p-4 bg-primary-50 border border-primary-200 rounded-lg">
        <h4 className="text-sm font-semibold text-primary-900 mb-2">
          Image Guidelines
        </h4>
        <ul className="text-xs text-primary-800 space-y-1">
          <li>• Ensure good lighting and focus</li>
          <li>• Minimum resolution: 512x512 pixels</li>
          <li>• Capture the entire lesion clearly</li>
          <li>• Avoid blurry or dark images</li>
          <li>• Include a reference object for scale if possible</li>
        </ul>
      </div>
    </div>
  )
}
