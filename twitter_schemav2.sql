SET NOCOUNT ON
GO

USE master
GO
if exists (select * from sysdatabases where name='TwitterProject')
		drop database TwitterProject
GO

CREATE DATABASE TwitterProject;
GO

use TwitterProject
GO

DROP TABLE HASHTAGS;
DROP TABLE TWEETS;
DROP TABLE USERS;
DROP TABLE SEARCHES;
DROP TABLE RESEARCHERS;


-- 
CREATE TABLE RESEARCHERS (
    researcher_id  BIGINT,
    full_name      NVARCHAR(100) NOT NULL,
    sex            NCHAR(1) NOT NULL,
    profile        NVARCHAR(400),
    date_of_birth  DATE NOT NULL,
    PRIMARY KEY(researcher_id)
);

-- actualizarlas

-- INSERT INTO RESEARCHERS VALUES (1, 'Marcos Quintero Ornelas', 'M',
 --                 'Databases course Student', '2000-11-06' );
--
CREATE TABLE SEARCHES (
    search_id     BIGINT,
    description   NVARCHAR(400),
    researcher_id BIGINT,
    PRIMARY KEY(search_id),
    FOREIGN KEY(researcher_id) references RESEARCHERS(researcher_id)
);

-- insert researcher first and then a search

-- actualizarlas
-- INSERT INTO SEARCHES VALUES(1, 'Search tweets containing COVID', 1);


-- DATE FORMAT = yyyy-mm-dd hh:mm:ss

-- De los Tweets almacenamos la información del usuario,
-- ustedes definen que datos quieren guardar, mínimo el handle, bio, timezone, location, etc.
CREATE TABLE USERS (
    userid            BIGINT,
    handle            NVARCHAR(60),
    name              NVARCHAR(100),
    bio               NVARCHAR(400),
    location          NVARCHAR(200),
    verified          BIT,
    --  number of Tweets the account has posted
    statuses_count    BIGINT,
    followers_count   BIGINT,
    -- The number of users this account is following (AKA their “followings”).
    friends_count	  BIGINT,
    -- 	The number of Tweets this user has liked in the account’s lifetime
    favourites_count  BIGINT,
    -- the date the account was created as string NOT as a Date
    created_at        DATE,
    PRIMARY KEY(userid)
);

-- Places

CREATE TABLE PLACES (
    place_id          NVARCHAR(100),
    short_name        NVARCHAR(70),
    full_name         NVARCHAR(150),

    
    -- coordinates
    coordinates       NVARCHAR(300),
    coordinates_type  NVARCHAR(40),
    place_type        NVARCHAR(30),
    country           NVARCHAR(50),
    country_code      NVARCHAR(50),

    PRIMARY KEY(place_id)

);



CREATE TABLE TWEETS (
    tweet_id           BIGINT,
    tweet_text         NVARCHAR(600),
    userid             BIGINT,
    favorite_count     BIGINT,
    retweet_count      BIGINT,
    quote_count        BIGINT,
    reply_count        BIGINT,
    
    search_id          BIGINT,

    -- if tweet is a retweet, retweet_id will have the tweet_id of the original tweet, else NULL
    retweet_id         BIGINT,
    -- if tweet is a quote, quote_id will have the tweet_id of the original tweet, else NULL
    quote_id           BIGINT,
    -- if tweet is a reply, reply_id will have the tweet_id of the original tweet, else NULL
    reply_id           BIGINT,

    lang               NVARCHAR(50),
    possibly_sensitive BIT,
    created_at         DATE,
    coordinates        NVARCHAR(300),
    coordinates_type   NVARCHAR(60),
    place_id           NVARCHAR(100),

    PRIMARY KEY(tweet_id),
    FOREIGN KEY(userid) references USERS(userid),
    FOREIGN KEY(search_id) references SEARCHES(search_id),
    FOREIGN KEY(retweet_id) references TWEETS(tweet_id),
    FOREIGN KEY(quote_id) references TWEETS(tweet_id),
    FOREIGN KEY(reply_id) references TWEETS(tweet_id),
    FOREIGN KEY(place_id) references PLACES(place_id)
);

CREATE TABLE HASHTAGS (
    tweet_id    BIGINT,
    hashtag     NVARCHAR(280),
    PRIMARY KEY(tweet_id, hashtag),
    FOREIGN KEY(tweet_id) references TWEETS(tweet_id)
);

-- Mentions

CREATE TABLE MENTIONS (
    tweet_id    BIGINT,
    -- assume mentioned_user_id is not necessary nor relevant
    handle      NVARCHAR(60),
    name        NVARCHAR(150),
     
    PRIMARY KEY(tweet_id, handle),
    FOREIGN KEY(tweet_id) references TWEETS(tweet_id)
);


