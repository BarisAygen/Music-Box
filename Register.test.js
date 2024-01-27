import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import { Register } from './Register';

jest.mock('axios');

describe('Register', () => {
  it('submits the form', async () => {
    axios.post.mockResolvedValue({ status: 201 });

    const onFormSwitch = jest.fn();
    const { getByLabelText, getByText } = render(<Register onFormSwitch={onFormSwitch} />);

    fireEvent.change(getByLabelText(/name/i), { target: { value: 'John' } });
    fireEvent.change(getByLabelText(/email/i), { target: { value: 'john@example.com' } });
    fireEvent.change(getByLabelText(/pass/i), { target: { value: 'password' } });

    fireEvent.click(getByText(/submit/i));

    await waitFor(() => expect(axios.post).toHaveBeenCalledWith('http://localhost:5000/signup', {
      name: 'John',
      email: 'john@example.com',
      pass: 'password',
    }));

    expect(onFormSwitch).toHaveBeenCalledWith('login');
  });
});