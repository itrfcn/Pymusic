-- 用户表
CREATE TABLE tabl_user (
    id          INT AUTO_INCREMENT
        PRIMARY KEY,
    username    VARCHAR(50)                         NOT NULL,
    password    VARCHAR(100)                        NOT NULL,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NULL,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT username
        UNIQUE (username)
);

-- 播放历史表
CREATE TABLE play_history (
    id        INT AUTO_INCREMENT
        PRIMARY KEY,
    user_id   INT                                NOT NULL,
    song_id   BIGINT                             NOT NULL,
    play_time DATETIME DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT idx_user_song
        UNIQUE (user_id, song_id)
);

CREATE INDEX idx_song_id
    ON play_history (song_id);

CREATE INDEX idx_user_id
    ON play_history (user_id);

CREATE INDEX idx_user_time
    ON play_history (user_id ASC, play_time DESC);

-- 播放列表表
CREATE TABLE playlist (
    id          INT AUTO_INCREMENT
        PRIMARY KEY,
    user_id     INT                                 NOT NULL,
    name        VARCHAR(100)                        NOT NULL,
    cover_url   LONGTEXT                            NULL,
    description TEXT                                NULL,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NULL,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_playlist
        UNIQUE (user_id, name),
    CONSTRAINT playlist_ibfk_1
        FOREIGN KEY (user_id) REFERENCES tabl_user (id)
);

CREATE INDEX idx_playlist_user_id
    ON playlist (user_id);

-- 播放列表歌曲表
CREATE TABLE playlist_song (
    id          INT AUTO_INCREMENT
        PRIMARY KEY,
    playlist_id INT                                 NOT NULL,
    song_id     BIGINT                              NOT NULL,
    add_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT unique_playlist_song
        UNIQUE (playlist_id, song_id),
    CONSTRAINT playlist_song_ibfk_1
        FOREIGN KEY (playlist_id) REFERENCES playlist (id)
            ON DELETE CASCADE
);

CREATE INDEX idx_playlist_song_playlist_id
    ON playlist_song (playlist_id);

CREATE INDEX idx_playlist_song_song_id
    ON playlist_song (song_id);