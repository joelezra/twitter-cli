"""Data models for twitter-cli.

Defines Tweet, Author, Metrics, and TweetMedia as simple dataclasses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Author:
    id: str
    name: str
    screen_name: str
    profile_image_url: str = ""
    verified: bool = False


@dataclass
class Metrics:
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    quotes: int = 0
    views: int = 0
    bookmarks: int = 0


@dataclass
class TweetMedia:
    type: str  # "photo" | "video" | "animated_gif"
    url: str
    width: Optional[int] = None
    height: Optional[int] = None


@dataclass
class Tweet:
    id: str
    text: str
    author: Author
    metrics: Metrics
    created_at: str
    media: List[TweetMedia] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)
    is_retweet: bool = False
    lang: str = ""
    retweeted_by: Optional[str] = None
    quoted_tweet: Optional[Tweet] = None
    score: Optional[float] = None
    article_title: Optional[str] = None
    article_text: Optional[str] = None
    is_subscriber_only: bool = False


@dataclass
class BookmarkFolder:
    id: str
    name: str


@dataclass
class Trend:
    name: str
    url: str = ""
    description: str = ""
    domain_context: str = ""  # e.g. "Trending in Technology", category
    tweet_count: int = 0
    grouped_trends: List[str] = field(default_factory=list)
    cluster_id: str = ""  # numeric id used in /i/trending/<id> URLs


@dataclass
class DMParticipant:
    user_id: str
    screen_name: str = ""
    name: str = ""


@dataclass
class DMMessage:
    id: str
    conversation_id: str
    sender_id: str
    text: str
    created_at: str  # ms epoch as string
    media_urls: List[str] = field(default_factory=list)
    reply_to_id: Optional[str] = None


@dataclass
class DMConversation:
    id: str
    name: str = ""  # group name (empty for 1:1)
    type: str = "ONE_TO_ONE"  # or "GROUP_DM"
    participants: List[DMParticipant] = field(default_factory=list)
    last_read_event_id: str = ""
    max_entry_id: str = ""  # most recent message id
    preview: str = ""  # most recent message text snippet
    unread: bool = False


@dataclass
class UserProfile:
    id: str
    name: str
    screen_name: str
    bio: str = ""
    location: str = ""
    url: str = ""
    followers_count: int = 0
    following_count: int = 0
    tweets_count: int = 0
    likes_count: int = 0
    verified: bool = False
    profile_image_url: str = ""
    created_at: str = ""
