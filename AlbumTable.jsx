import React from 'react';

const AlbumTable = ({ albums }) => {

  return (
    <div>
      <h2>Albums Table</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ backgroundColor: '#00ADB5' }}>
            <th style={{ border: '0.06rem solid #EEEEEE', padding: '0.5rem' }}>Album Name</th>
            <th style={{ border: '0.06rem solid #EEEEEE', padding: '0.5rem' }}>Artist</th>
            <th style={{ border: '0.06rem solid #EEEEEE', padding: '0.5rem' }}>Year</th>
            <th style={{ border: '0.06rem solid #EEEEEE', padding: '0.5rem' }}>Genre</th>
          </tr>
        </thead>
        <tbody>
          {albums.map((album, index) => (
            <tr key={index} style={{ borderBottom: '0.06rem solid #FFD1DA' }}>
              <td style={{ padding: '0.5rem' }}>{album.name}</td>
              <td style={{ padding: '0.5rem' }}>{album.artist}</td>
              <td style={{ padding: '0.5rem' }}>{album.year}</td>
              <td style={{ padding: '80.5rempx' }}>{album.genre}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AlbumTable;