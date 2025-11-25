import React from 'react';

interface QualityScoreCardProps {
  score: number | null;
}

export const QualityScoreCard: React.FC<QualityScoreCardProps> = ({ score }) => {
  const getScoreColor = () => {
    if (score === null) return 'bg-gray-600';
    if (score >= 85) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg text-center">
      <h3 className="text-lg font-semibold mb-2">Puntuación de Calidad de Datos</h3>
      <div className={`w-32 h-32 rounded-full mx-auto flex items-center justify-center text-4xl font-bold text-white ${getScoreColor()}`}>
        {score !== null ? `${score}` : 'N/A'}
      </div>
    </div>
  );
};
