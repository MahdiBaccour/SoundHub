// Select the SoundHub database
const dbSoundHub = db.getSiblingDB("soundhub");

// Create indexes for users
dbSoundHub.users.createIndex(
    { user_id: 1 },
    { unique: true }
);

dbSoundHub.users.createIndex(
    { email: 1 },
    { unique: true }
);

// Create indexes for songs
dbSoundHub.songs.createIndex(
    { song_id: 1 },
    { unique: true }
);

dbSoundHub.songs.createIndex(
    { genres: 1 }
);

// Create indexes for ratings
dbSoundHub.ratings.createIndex(
    { rating_id: 1 },
    { unique: true }
);

dbSoundHub.ratings.createIndex(
    { user_id: 1 }
);

dbSoundHub.ratings.createIndex(
    { song_id: 1 }
);

print("SoundHub indexes created successfully!");