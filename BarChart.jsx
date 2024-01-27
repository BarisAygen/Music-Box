import React from 'react';
import { Bar } from 'react-chartjs-2';

const BarChart = ({ data }) => {
  const chartData = {
    labels: Object.keys(data),
    datasets: [
      {
        label: 'Number of Songs',
        data: Object.values(data),
        backgroundColor: '#EEEEEE',
        borderColor: '#FFD1DA',
        borderWidth: 1,
      }
    ]
  };

  return <Bar data={chartData} />;
};

export default BarChart;