import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTrash, faChevronLeft, faChevronRight } from "@fortawesome/free-solid-svg-icons";

export const Profile = () => {
    const [fetchedEmail, setFetchedEmail] = useState('');
    const [fetchedName, setFetchedName] = useState('');
    const [friends, setFriends] = useState([]);
    const [showFriends, setShowFriends] = useState(false);
    const [file, setFile] = useState(null);
    const [showUpload, setShowUpload] = useState(false);
    const [profilePictureUrl, setProfilePictureUrl] = useState('');
    const [currentPage, setCurrentPage] = useState(0);
    const friendsPerPage = 6;
    const indexOfLastFriend = (currentPage + 1) * friendsPerPage;
    const indexOfFirstFriend = indexOfLastFriend - friendsPerPage;
    const currentFriends = friends.slice(indexOfFirstFriend, indexOfLastFriend);
    const [friendsProfilePictures, setFriendsProfilePictures] = useState({});
    const [artistName, setArtistName] = useState('');

    const handlePrevClick = () => {
        setCurrentPage(currentPage => Math.max(0, currentPage - 1));
    };

    const handleNextClick = () => {
        setCurrentPage(currentPage => Math.min(Math.ceil(friends.length / friendsPerPage) - 1, currentPage + 1));
    };

    useEffect(() => {
        const userToken = localStorage.getItem('access_token');
        const fetchEmail = async () => {
            try {
                const response = await axios.get("http://localhost:5000/get_my_email", {
                    headers: {
                        Authorization: `Bearer ${userToken}`,
                    },
                });

                if (response.status === 200) {
                    setFetchedEmail(response.data.email);
                }
            }
            catch (error) {
                console.log(error);
            }
        };
        fetchEmail();

        const fetchName = async () => {
            try {
                const response = await axios.get("http://localhost:5000/get_my_name", {
                    headers: {
                        Authorization: `Bearer ${userToken}`,
                    },
                });

                if (response.status === 200) {
                    setFetchedName(response.data.Name);
                }
            }
            catch (error) {
                console.log(error);
            }
        };
        fetchName();

        const fetchFriendsProfilePictures = async () => {
            for (const friend of friends) {
                try {
                    const response = await axios.get(`http://localhost:5000/get_profile_picture/${friend.email}`, {
                        headers: {
                            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
                        },
                        responseType: 'blob',
                    });

                    if (response.status === 200) {
                        setFriendsProfilePictures(prev => ({
                            ...prev,
                            [friend.email]: URL.createObjectURL(response.data)
                        }));
                    }
                } catch (error) {
                    console.error(`Error fetching profile picture for ${friend.email}:`, error);
                }
            }
        };

        const fetchProfilePicture = async () => {
            const userToken = localStorage.getItem('access_token');
            try {
                const response = await axios.get("http://localhost:5000/get_my_profile_picture", {
                    headers: {
                        Authorization: `Bearer ${userToken}`,
                    },
                    responseType: 'blob',
                });

                if (response.status === 200) {
                    setProfilePictureUrl(URL.createObjectURL(response.data));
                }
            } catch (error) {
                console.error('Error fetching profile picture:', error);
            }
        };

        fetchProfilePicture();
    
        if (friends.length > 0) {
            fetchFriendsProfilePictures();
        }
    }, [friends]);

    const fetchFriends = async () => {
        if (showFriends) {
            setShowFriends(false);
            return;
        }
        const userToken = localStorage.getItem('access_token');
        try {
            const response = await axios.get("http://localhost:5000/get_friends", {
                headers: {
                    Authorization: `Bearer ${userToken}`,
                },
            });

            if (response.status === 200) {
                setFriends(response.data.friends.map(friend => ({
                    ...friend,
                    profile_picture: friend.profile_picture ? `data:image/jpeg;base64,${friend.profile_picture}` : 'default_profile_pic_url'
                })));
                setShowFriends(true);
            }
        }
        catch (error) {
            console.error('Error fetching friends:', error);
        }
    };

    const handleExportRatings = async () => {
        const userToken = localStorage.getItem('access_token');
        try {
            const response = await axios.post("http://localhost:5000/export_ratings", 
                { artist_name: artistName },
                {
                    headers: {
                        Authorization: `Bearer ${userToken}`,
                        'Accept': 'text/csv',
                    },
                    responseType: 'blob',
                }
            );
            const file = new Blob([response.data], { type: 'text/csv' });
            const fileURL = URL.createObjectURL(file);
            const link = document.createElement('a');
            link.href = fileURL;
            const fileName = `downloaded ratings.csv`;
            link.setAttribute('download', fileName);
            document.body.appendChild(link);
            link.click();
        } catch (error) {
            console.error('Error during CSV export', error);
        }
    };

    const handleRemoveFriend = async (friendEmail) => {
        const userToken = localStorage.getItem('access_token');
        try {
            const response = await axios.post("http://localhost:5000/remove_friend", 
                { friend_email: friendEmail },
                {
                    headers: {
                        Authorization: `Bearer ${userToken}`,
                        'Content-Type': 'application/json',
                    },
                }
            );

            if (response.status === 200) {
                setFriends(friends.filter(friend => friend.email !== friendEmail));
            }
        }
        catch (error) {
            console.error('Error during removing friend:');
        }
    };

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) {
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const userToken = localStorage.getItem('access_token');
            const response = await axios.post("http://localhost:5000/upload_profile_picture", formData, {
                headers: {
                    Authorization: `Bearer ${userToken}`,
                    'Content-Type': 'multipart/form-data',
                },
            });

            if (response.status === 200) {
                setFile(null);
            }
        } 
        catch (error) {
            console.error('Error uploading file:', error);
        }
    };

    return (
        <>
            <div className="profile-container">
                <h2>Profile</h2>
                <div className="profile-photo" onClick={() => setShowUpload(!showUpload)}>
                {profilePictureUrl ? (
                        <img src={profilePictureUrl} alt="Profile" />
                    ) : (
                        <p>Upload Picture</p>
                    )}
                </div>
                {showUpload && (
                    <div>
                        <input type="file" onChange={handleFileChange} />
                        <button className="profile-upload-button" onClick={handleUpload}>Upload</button>
                    </div>
                )}
                <div className="profile-details">
                    <p>Email: {fetchedEmail}</p>
                    <p>Name: {fetchedName}</p>
                    <button className="profile-button" onClick={fetchFriends}>Friends</button>
                    <div>
                        <input className='export-ratings-input'
                            type="text" 
                            placeholder="Enter Artist Name" 
                            value={artistName} 
                            onChange={(e) => setArtistName(e.target.value)} 
                        />
                        <button className="profile-button" onClick={handleExportRatings}>Export</button>
                    </div>
                </div>
                {showFriends && (
                    <div className="friends-list">
                        <h3>Friends:</h3>
                        <ul>
                        {currentFriends.map(friend => (
                            <li key={friend.id} className="friend-item">
                                <div className="friend-profile-photo">
                                    <img src={friend.profile_picture} alt={`${friend.name}'s Profile`} />
                                </div>
                                {friend.name} ({friend.email})
                                <FontAwesomeIcon 
                                    icon={faTrash} 
                                    className="delete-icon" 
                                    onClick={() => handleRemoveFriend(friend.email)}
                                />
                            </li>
                        ))}
                        </ul>
                        <div className="pagination">
                            <FontAwesomeIcon 
                                icon={faChevronLeft} 
                                className={`arrow ${currentPage === 0 ? 'disabled' : ''}`}
                                onClick={handlePrevClick}
                            />
                            <FontAwesomeIcon 
                                icon={faChevronRight} 
                                className={`arrow ${currentPage === Math.ceil(friends.length / friendsPerPage) - 1 ? 'disabled' : ''}`}
                                onClick={handleNextClick}
                            />
                        </div>
                    </div>
                )}
            </div>
        </>
    );
};