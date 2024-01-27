import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import { Search } from './Search';
import { useSelector } from 'react-redux';

jest.mock('axios');
jest.mock('react-redux', () => ({
  useSelector: jest.fn(),
  useDispatch: () => jest.fn()
}));

describe('Search Component', () => {
  beforeEach(() => {
    useSelector.mockImplementation(callback => {
      return callback({
        allTracks: [{ track_id: 1, track_name: 'Test Track', artist_names: 'Test Artist', album_names: 'Test Album', average_rating: 3, user_rating: 4 }],
        likedTracks: [{ track_id: 1 }]
      });
    });

    axios.get.mockResolvedValue({ data: { friends: [{ email: 'friend@example.com' }] } });
    axios.post.mockResolvedValue({});
  });

  it('renders without crashing', () => {
    const { getByPlaceholderText } = render(<Search />);
    expect(getByPlaceholderText('Search')).toBeInTheDocument();
  });

  it('searches for tracks', async () => {
    const { getByPlaceholderText, getByText } = render(<Search />);
    fireEvent.change(getByPlaceholderText('Search'), { target: { value: 'Test' } });
    await waitFor(() => {
      expect(getByText('Test Track')).toBeInTheDocument();
    });
  });

});
