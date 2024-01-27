import React, { useState } from 'react';
import axios from 'axios';

export const Upload = () => {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post('http://localhost:5000/batch_upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    if (response.status === 201) {

    }
  };

  return (
    <>
      <div className='upload-container'>
        <h1>Song Upload Page</h1>
        <div>
          <h2>File Upload</h2>
          <input type="file" onChange={handleFileChange} />
          <button onClick={handleUpload}>Upload</button>
        </div>
      </div>
    </>
  );
};