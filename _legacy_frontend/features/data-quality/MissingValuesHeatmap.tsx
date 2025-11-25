import React from 'react';
import Plot from 'react-plotly.js';

interface MissingValuesHeatmapProps {
  data: any[] | null;
}

export const MissingValuesHeatmap: React.FC<MissingValuesHeatmapProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return <div className="bg-gray-800 p-6 rounded-lg"><p>No hay datos para mostrar el heatmap.</p></div>;
  }

  const columns = Object.keys(data[0]);
  const z = data.map(row => columns.map(col => (row[col] === null || row[col] === undefined ? 1 : 0)));

  return (
    <div className="bg-gray-800 p-6 rounded-lg">
      <h3 className="text-lg font-semibold mb-4">Heatmap de Valores Faltantes</h3>
      <Plot
        data={[
          {
            z: z,
            x: columns,
            y: data.map((_, i) => `Fila ${i}`),
            type: 'heatmap',
            colorscale: 'Viridis',
            showscale: false,
          },
        ]}
        layout={{
          autosize: true,
          plot_bgcolor: 'rgba(0,0,0,0)',
          paper_bgcolor: 'rgba(0,0,0,0)',
          font: {
            color: 'white',
          },
        }}
        config={{ responsive: true }}
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
};
