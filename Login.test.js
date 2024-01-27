import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import { Login } from './Login'; // Update the import path as necessary

// Mocking Axios and custom hooks
jest.mock('axios');
jest.mock('./services/musicboxApi', () => ({
  useLazyGetUserLikedTracksQuery: jest.fn(() => [jest.fn()]),
  useLazyGetAllTracksQuery: jest.fn(() => [jest.fn()]),
  useLazyGetGeneralTopRatedTracksQuery: jest.fn(() => [jest.fn()]),
  useLazyGetTopRatedTracksQuery: jest.fn(() => [jest.fn()]),
  useLazyGetUserNameQuery: jest.fn(() => [jest.fn()])
}));

describe('Login Component', () => {
  it('renders the login form', () => {
    const { getByPlaceholderText, getByText } = render(<Login onFormSwitch={() => {}} />);
    expect(getByPlaceholderText('ilkan@gmail.com')).toBeInTheDocument();
    expect(getByText('Login')).toBeInTheDocument();
  });

  it('allows entering email and password', () => {
    const { getByPlaceholderText } = render(<Login onFormSwitch={() => {}} />);
    const emailInput = getByPlaceholderText('ilkan@gmail.com');
    const passwordInput = getByPlaceholderText('Password');

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });

    expect(emailInput.value).toBe('test@example.com');
    expect(passwordInput.value).toBe('password123');
  });

  it('submits the form and performs API call on successful login', async () => {
    axios.post.mockResolvedValue({ status: 200, data: { access_token: 'token', refresh_token: 'refresh_token' } });

    const onFormSwitchMock = jest.fn();
    const { getByPlaceholderText, getByText } = render(<Login onFormSwitch={onFormSwitchMock} />);
    fireEvent.change(getByPlaceholderText('ilkan@gmail.com'), { target: { value: 'test@example.com' } });
    fireEvent.change(getByPlaceholderText('Password'), { target: { value: 'password123' } });
    fireEvent.click(getByText('Login'));

    await waitFor(() => expect(axios.post).toHaveBeenCalledWith("http://localhost:5000/login", {
      email: 'test@example.com',
      password: 'password123'
    }));

    // Check if onFormSwitch was called with 'home'
    await waitFor(() => expect(onFormSwitchMock).toHaveBeenCalledWith('home'));
  });

  // Additional tests for error handling, etc., can be added here
});
