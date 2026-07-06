import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, FileText, Image, Video } from 'lucide-react';
import { useUpload } from '../../hooks/useDocuments';
import UploadProgress from './UploadProgress';
import { useNavigate } from 'react-router-dom';

const ACCEPT = {
  'application/pdf':  ['.pdf'],
  'image/jpeg':       ['.jpg', '.jpeg'],
  'image/png':        ['.png'],
  'image/webp':       ['.webp'],
  'video/mp4':        ['.mp4'],
  'video/quicktime':  ['.mov'],
  'video/webm':       ['.webm'],
};

function TypeIcon({ type }: { type: string }) {
  if (type.startsWith('image')) return <Image size={36} className="text-green-400" />;
  if (type.startsWith('video')) return <Video size={36} className="text-purple-400" />;
  return <FileText size={36} className="text-blue-400" />;
}

export default function DropZone() {
  const { upload, uploading, progress, error, result, reset } = useUpload();
  const navigate = useNavigate();

  const onDrop = useCallback(async (accepted: File[]) => {
    if (!accepted[0]) return;
    const res = await upload(accepted[0]);
    if (res) {
      setTimeout(() => navigate(`/documents/${res.doc_id}`), 500);
    }
  }, [upload, navigate]);

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    onDrop,
    accept: ACCEPT,
    maxFiles: 1,
    maxSize: 25 * 1024 * 1024,
    disabled: uploading,
  });

  if (result) {
    return <UploadProgress docId={result.doc_id} onDone={() => navigate(`/documents/${result.doc_id}`)} />;
  }

  return (
    <div className="max-w-xl mx-auto mt-12 px-6">
      <h1 className="text-xl font-semibold text-gray-800 mb-6">Upload Document</h1>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}`}
      >
        <input {...getInputProps()} />
        <UploadCloud className="mx-auto text-gray-400 mb-3" size={40} />
        <p className="text-sm text-gray-600">
          {isDragActive ? 'Drop your file here…' : 'Drag & drop a file, or click to browse'}
        </p>
        <p className="text-xs text-gray-400 mt-2">PDF · PNG · JPG · WEBP · MP4 · MOV · WEBM</p>
        <p className="text-xs text-gray-400">Max 20 MB · Videos ≤ 60s</p>
      </div>

      {acceptedFiles[0] && !uploading && !error && (
        <div className="mt-4 flex items-center gap-3 p-3 bg-gray-50 rounded-xl border border-gray-200">
          <TypeIcon type={acceptedFiles[0].type} />
          <div>
            <p className="text-sm font-medium text-gray-700">{acceptedFiles[0].name}</p>
            <p className="text-xs text-gray-400">{(acceptedFiles[0].size / 1024 / 1024).toFixed(1)} MB</p>
          </div>
        </div>
      )}

      {uploading && (
        <div className="mt-4">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>Uploading…</span><span>{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-blue-500 h-2 rounded-full transition-all" style={{ width: `${progress}%` }} />
          </div>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-600">
          {error}
          <button onClick={reset} className="ml-2 underline">Try again</button>
        </div>
      )}
    </div>
  );
}
