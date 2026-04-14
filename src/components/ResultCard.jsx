import React from 'react';

const Card = ({ title, value, colorClass }) => (
  <div className={`p-4 rounded-xl shadow-sm border ${colorClass} bg-white`}>
    <p className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">{title}</p>
    <p className="text-lg font-semibold text-gray-800">{value}</p>
  </div>
);

export default function ResultCard({ data }) {
  return (
    <div className="space-y-4">
      {/* Intervention Banner */}
      <div className="bg-red-600 text-white p-6 rounded-xl shadow-lg mb-6 text-center animate-pulse">
        <h2 className="text-2xl font-bold uppercase tracking-tight">Immediate Action Required</h2>
        <p className="opacity-90">Follow the recommended steps below.</p>
      </div>

      {/* Grid of Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card title="Situation" value={data.situation} colorClass="border-blue-100" />
        <Card title="Predicted Action" value={data.predicted_action} colorClass="border-gray-100" />
        <Card title="Risk" value={data.risk} colorClass="border-red-100" />
        <Card title="Recommended Action" value={data.recommended_action} colorClass="border-green-100" />
        <Card title="Urgency" value={data.urgency} colorClass="border-orange-100" />
        <Card title="Confidence" value={`${(data.confidence * 100).toFixed(0)}%`} colorClass="border-purple-100" />
      </div>
    </div>
  );
}