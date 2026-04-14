import React, { useState, useEffect } from 'react';
import {
  AlertCircle,
  Loader2,
  CheckCircle2,
  ArrowLeft,
  Upload,
  Image as ImageIcon,
  Info,
  AlertTriangle,
  Zap,
} from 'lucide-react';
import { analyzeSituation } from './api/client';

const APP_CONFIG = {
  TITLE: 'Last 60 Seconds Engine',
  SUBTITLE: 'Before you ignore, check.',
  EXPLAINER:
    'Upload a photo of a potentially dangerous situation to receive immediate intervention guidance.',
};

const LOADING_PHASES = [
  'Analyzing visual data...',
  'Assessing potential risk...',
  'Preparing recommendation...',
];

const URGENCY_MAP = {
  high: {
    bannerText: 'IMMEDIATE INTERVENTION REQUIRED',
    colorClass: 'bg-red-600',
    textClass: 'text-red-100',
    icon: AlertCircle,
  },
  medium: {
    bannerText: 'CAUTION ADVISED',
    colorClass: 'bg-orange-500',
    textClass: 'text-orange-50',
    icon: AlertTriangle,
  },
  low: {
    bannerText: 'SITUATION MONITORING',
    colorClass: 'bg-blue-600',
    textClass: 'text-blue-50',
    icon: Info,
  },
};

function normalizeUrgency(urgency) {
  const normalized = String(urgency || 'low').toLowerCase();
  return URGENCY_MAP[normalized] ? normalized : 'low';
}

function normalizeConfidence(confidence) {
  const numeric = Number(confidence);
  if (Number.isNaN(numeric)) return 0.5;
  return Math.min(Math.max(numeric, 0), 1);
}

const UploadZone = ({ onFileSelect, selectedFile }) => {
  const hasFile = Boolean(selectedFile);

  return (
    <div className="w-full">
      <label
        className={`relative flex h-64 w-full cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed transition-all duration-300 ${
          hasFile
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 bg-white hover:border-blue-400 hover:bg-gray-50'
        }`}
      >
        <div className="flex flex-col items-center justify-center px-6 text-center">
          {hasFile ? (
            <ImageIcon className="mb-3 h-12 w-12 text-blue-500" />
          ) : (
            <Upload className="mb-3 h-12 w-12 text-gray-400" />
          )}

          <p
            className={`text-sm font-medium ${
              hasFile ? 'text-blue-600' : 'text-gray-500'
            }`}
          >
            {hasFile ? selectedFile.name : 'Click to upload or drag and drop'}
          </p>

          <p className="mt-2 text-xs text-gray-400">PNG, JPG, JPEG</p>
        </div>

        <input
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => onFileSelect(e.target.files?.[0] || null)}
        />
      </label>
    </div>
  );
};

const ResultCard = ({ label, value, icon: Icon, colorClass }) => (
  <div className="flex items-start space-x-4 rounded-xl border border-gray-100 bg-white p-4 shadow-sm">
    <div className={`rounded-lg p-2 ${colorClass}`}>
      <Icon className="h-5 w-5 text-white" />
    </div>
    <div className="flex-1">
      <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">
        {label}
      </p>
      <p className="mt-1 break-words font-medium leading-relaxed text-gray-800">
        {value || 'Not available'}
      </p>
    </div>
  </div>
);

export default function App() {
  const [file, setFile] = useState(null);
  const [textInput, setTextInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingPhase, setLoadingPhase] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!loading) return undefined;

    setLoadingPhase(0);

    const interval = setInterval(() => {
      setLoadingPhase((prev) => (prev + 1) % LOADING_PHASES.length);
    }, 1500);

    return () => clearInterval(interval);
  }, [loading]);

  const handleAnalyze = async () => {
    if (!file) {
      setError('Please select an image first.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await analyzeSituation(file, textInput);
      setResult(data);
    } catch (err) {
      setError(err?.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setFile(null);
    setTextInput('');
    setResult(null);
    setError(null);
    setLoading(false);
    setLoadingPhase(0);
  };

  const urgency = result ? normalizeUrgency(result.urgency) : 'low';
  const urgencyConfig = URGENCY_MAP[urgency];
  const BannerIcon = urgencyConfig.icon;
  const confidence = result ? normalizeConfidence(result.confidence) : 0;

  return (
    <div className="min-h-screen bg-gray-50 pb-12 font-sans text-gray-900">
      <header className="mb-8 border-b border-gray-200 bg-white px-4 py-6 shadow-sm">
        <div className="mx-auto max-w-2xl text-center">
          <h1 className="tracking-tight text-2xl font-bold text-blue-600">
            {APP_CONFIG.TITLE}
          </h1>
          <p className="mt-1 italic text-gray-500">{APP_CONFIG.SUBTITLE}</p>
        </div>
      </header>

      <main className="mx-auto max-w-2xl px-4">
        {!loading && !result && !error && (
          <div className="animate-in space-y-6 fade-in duration-500">
            <p className="text-center text-sm text-gray-600">
              {APP_CONFIG.EXPLAINER}
            </p>

            <UploadZone selectedFile={file} onFileSelect={setFile} />

            <div className="space-y-4">
              <input
                type="text"
                placeholder="What are you seeing? (Optional)"
                className="w-full rounded-xl border border-gray-200 p-4 outline-none transition-all focus:ring-2 focus:ring-blue-500"
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
              />

              <button
                onClick={handleAnalyze}
                disabled={!file || loading}
                className={`w-full rounded-xl py-4 text-lg font-bold transition-all ${
                  file
                    ? 'bg-blue-600 text-white shadow-lg hover:bg-blue-700'
                    : 'cursor-not-allowed bg-gray-200 text-gray-400'
                }`}
              >
                Analyze Situation
              </button>
            </div>
          </div>
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center space-y-4 py-20">
            <Loader2 className="h-12 w-12 animate-spin text-blue-500" />
            <p className="font-medium text-gray-500">
              {LOADING_PHASES[loadingPhase]}
            </p>
          </div>
        )}

        {error && !loading && (
          <div className="animate-in space-y-6 fade-in duration-500">
            <div className="flex items-center rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
              <AlertCircle className="mr-3 h-5 w-5" />
              <span>{error}</span>
            </div>

            <button
              onClick={reset}
              className="w-full rounded-xl bg-gray-200 py-4 font-bold"
            >
              Try Again
            </button>
          </div>
        )}

        {result && !loading && (
          <div className="animate-in space-y-6 slide-in-from-bottom duration-500">
            <button
              onClick={reset}
              className="mb-2 flex items-center text-sm font-medium text-blue-600"
            >
              <ArrowLeft className="mr-1 h-4 w-4" />
              New Analysis
            </button>

            <div
              className={`${urgencyConfig.colorClass} mb-8 rounded-2xl p-6 text-white shadow-xl transition-colors duration-500`}
            >
              <div className="mb-2 flex items-center space-x-3">
                <BannerIcon className="h-6 w-6" />
                <h2 className="text-xl font-bold uppercase tracking-wide">
                  {urgencyConfig.bannerText}
                </h2>
              </div>
              <p className={`text-lg leading-relaxed ${urgencyConfig.textClass}`}>
                {result.recommended_action || 'No recommendation available.'}
              </p>
            </div>

            <div className="mb-2 flex items-center space-x-2 px-1">
              <Info className="h-4 w-4 text-gray-400" />
              <p className="text-xs font-medium uppercase italic tracking-tight text-gray-500">
                Here’s what could happen if this situation is ignored:
              </p>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <ResultCard
                label="Situation"
                value={result.situation}
                icon={Info}
                colorClass="bg-blue-500"
              />
              <ResultCard
                label="Risk"
                value={result.risk}
                icon={AlertTriangle}
                colorClass="bg-orange-500"
              />
              <ResultCard
                label="Predicted Action"
                value={result.predicted_action}
                icon={CheckCircle2}
                colorClass="bg-green-500"
              />
              <ResultCard
                label="Urgency"
                value={urgency}
                icon={Zap}
                colorClass="bg-purple-500"
              />
            </div>

            <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
              <div className="mb-2 flex items-center justify-between">
                <p className="text-xs font-bold uppercase tracking-wider text-gray-500">
                  AI Confidence
                </p>
                <p className="text-xs font-black text-blue-600">
                  {Math.round(confidence * 100)}%
                </p>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100">
                <div
                  className="h-full bg-blue-500 transition-all duration-1000 ease-out"
                  style={{ width: `${confidence * 100}%` }}
                />
              </div>
            </div>

            {result.why_this_matters && (
              <div className="rounded-xl border border-dashed border-gray-300 bg-gray-100 p-4">
                <p className="mb-1 text-xs font-bold uppercase text-gray-500">
                  Reasoning &amp; Impact
                </p>
                <p className="text-sm italic leading-relaxed text-gray-700">
                  &quot;{result.why_this_matters}&quot;
                </p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}