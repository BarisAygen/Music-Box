import React, { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import 'chart.js/auto';
import axios from 'axios';

export const Statistics = () => {
  const [topRatedTracks, setTopRatedTracks] = useState([]);
  const [generalTopRatedTracks, setGeneralTopRatedTracks] = useState([]);
  const [topRatedTracksByGenre, setTopRatedTracksByGenre] = useState([]);
  const [genres, setGenres] = useState([]);
  const [selectedGenre, setSelectedGenre] = useState('');

  const fetchGenres = async () => {
    try {
      const userToken = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:5000/genres', {
        headers: { Authorization: `Bearer ${userToken}` },
      });
      setGenres(response.data);
    } catch (error) {
      console.error('Error fetching genres:', error);
    }
  };
  
  const fetchTopRatedTracks = async () => {
    try {
      const userToken = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:5000/user_top_rated_tracks', {
        headers: { Authorization: `Bearer ${userToken}` },
      });
      setTopRatedTracks(response.data.results);
    } catch (error) {
      console.error('Error fetching top rated tracks:', error);
    }
  };

  const fetchGeneralTopRatedTracks = async () => {
    try {
      const userToken = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:5000/top_rated_tracks', {
        headers: { Authorization: `Bearer ${userToken}` },
      });
      setGeneralTopRatedTracks(response.data);
    } catch (error) {
      console.error('Error fetching general top rated tracks:', error);
    }
  };

  const fetchTopRatedTracksByGenre = async (genre) => {
    try {
      const userToken = localStorage.getItem('access_token');
      const response = await axios.get(`http://localhost:5000/top_rated_tracks_by_genre?genre=${genre}`, {
        headers: { Authorization: `Bearer ${userToken}` },
      });
      setTopRatedTracksByGenre(response.data);
    } catch (error) {
      console.error('Error fetching top rated tracks by genre:', error);
    }
  };

  useEffect(() => {
    fetchGenres();
    fetchTopRatedTracks();
    fetchGeneralTopRatedTracks();
    fetchTopRatedTracksByGenre('YourGenreHere');
  }, []);

  useEffect(() => {
    if (selectedGenre) {
      fetchTopRatedTracksByGenre(selectedGenre);
    }
  }, [selectedGenre]);

  const handleGenreChange = (event) => {
    setSelectedGenre(event.target.value);
  };
  
  const userTopRatedChartData = {
    labels: topRatedTracks?.length ? topRatedTracks.map(track => track.track_name) : [],
    datasets: [
      {
        label: 'Rating',
        data: topRatedTracks?.length ? topRatedTracks.map(track => track.rating) : [],
        backgroundColor: '#FFA732',
        borderColor: '#333',
        borderWidth: 1,
      },
    ],
  };

  const generalTopRatedChartData = {
    labels: generalTopRatedTracks.map(track => track.track_name),
    datasets: [
      {
        label: 'Average Rating',
        data: generalTopRatedTracks.map(track => track.average_rating),
        backgroundColor: '#00ADB5',
        borderColor: '#333',
        borderWidth: 1,
      },
    ],
  };

  const topRatedByGenreChartData = {
    labels: topRatedTracksByGenre.map(track => track.track_name),
    datasets: [
      {
        label: 'Top Rated by Genre',
        data: topRatedTracksByGenre.map(track => track.average_rating),
        backgroundColor: '#82B1FF',
        borderColor: '#333',
        borderWidth: 1,
      },
    ],
  };
  
  const chartOptions = {
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <div style={{ width: '50%', margin: '0 auto' }}>
      <h1>Your Top Rated Tracks</h1>
      <Bar data={userTopRatedChartData} options={chartOptions} />
      <h1>General Top Rated Tracks</h1>
      <Bar data={generalTopRatedChartData} options={chartOptions} />
      <h1>Top Rated Tracks by Genre</h1>
      <select onChange={handleGenreChange} value={selectedGenre} className='genre-dropdown'>
        <option value="">Select Genre</option>
        {genres.map(genre => (
          <option key={genre} value={genre}>{genre}</option>
        ))}
      </select>
      <Bar data={topRatedByGenreChartData} options={chartOptions} />
    </div>
  );
};