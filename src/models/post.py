"""Data models for social media posts."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class Platform(str, Enum):
    """Supported social media platforms."""
    TWITTER = "twitter"
    REDDIT = "reddit"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    UNKNOWN = "unknown"


class Post(BaseModel):
    """Represents a social media post."""
    
    id: str = Field(..., description="Unique post identifier")
    platform: Platform = Field(..., description="Source platform")
    author_id: str = Field(..., description="Author user ID")
    author_username: str = Field(..., description="Author username")
    content: str = Field(..., description="Post content/text")
    timestamp: datetime = Field(..., description="Post timestamp")
    url: Optional[str] = Field(None, description="Post URL")
    
    # Engagement metrics
    likes: int = Field(default=0, description="Number of likes")
    retweets_shares: int = Field(default=0, description="Number of retweets/shares")
    replies: int = Field(default=0, description="Number of replies")
    
    # Metadata
    hashtags: List[str] = Field(default_factory=list, description="Hashtags in post")
    mentions: List[str] = Field(default_factory=list, description="Mentioned users")
    links: List[str] = Field(default_factory=list, description="Links in post")
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Platform-specific metadata"
    )
    
    # Analysis fields (populated during processing)
    embedding: Optional[List[float]] = Field(None, description="Content embedding vector")
    bot_probability: Optional[float] = Field(None, ge=0, le=1, description="Bot probability score")
    suspicious_score: Optional[float] = Field(None, ge=0, le=1, description="Suspiciousness score")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Account(BaseModel):
    """Represents a social media account."""
    
    id: str = Field(..., description="Unique account identifier")
    username: str = Field(..., description="Account username")
    platform: Platform = Field(..., description="Platform")
    
    # Profile information
    display_name: Optional[str] = Field(None, description="Display name")
    bio: Optional[str] = Field(None, description="Bio/description")
    created_at: Optional[datetime] = Field(None, description="Account creation date")
    
    # Metrics
    followers: int = Field(default=0, description="Number of followers")
    following: int = Field(default=0, description="Number of accounts following")
    posts_count: int = Field(default=0, description="Total number of posts")
    
    # Activity patterns
    posts_per_day: Optional[float] = Field(None, description="Average posts per day")
    avg_post_length: Optional[float] = Field(None, description="Average post length")
    
    # Detection results
    bot_probability: Optional[float] = Field(None, ge=0, le=1, description="Bot probability")
    suspicious_score: Optional[float] = Field(None, ge=0, le=1, description="Suspiciousness score")
    flagged: bool = Field(default=False, description="Whether account is flagged")
    flag_reasons: List[str] = Field(default_factory=list, description="Reasons for flagging")
    
    # Relationship data
    connections: List[str] = Field(
        default_factory=list, description="Connected account IDs (followers/following)"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Platform-specific metadata"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

