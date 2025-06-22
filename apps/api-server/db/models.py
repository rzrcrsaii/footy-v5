"""
Footy-Brain v5 Database Models
SQLModel mappings for database tables with TimescaleDB hypertable support.
"""

from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
import uuid

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Text, DECIMAL, JSON
from sqlalchemy.dialects.postgresql import UUID


# =============================================================================
# DIMENSION MODELS
# =============================================================================

class Country(SQLModel, table=True):
    """Country dimension table."""
    
    id: int = Field(primary_key=True)
    name: str = Field(max_length=100)
    code: Optional[str] = Field(max_length=3)
    flag: Optional[str] = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    leagues: List["League"] = Relationship(back_populates="country")
    teams: List["Team"] = Relationship(back_populates="country")
    venues: List["Venue"] = Relationship(back_populates="country")


class League(SQLModel, table=True):
    """League dimension table."""
    
    id: int = Field(primary_key=True)
    name: str = Field(max_length=200)
    type: Optional[str] = Field(max_length=50)  # League, Cup, etc.
    logo: Optional[str] = Field(max_length=255)
    country_id: Optional[int] = Field(foreign_key="country.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    country: Optional[Country] = Relationship(back_populates="leagues")
    fixtures: List["Fixture"] = Relationship(back_populates="league")
    standings: List["Standing"] = Relationship(back_populates="league")


class Season(SQLModel, table=True):
    """Season dimension table."""
    
    id: int = Field(primary_key=True)
    year: int = Field(unique=True)
    start_date: Optional[date]
    end_date: Optional[date]
    current: bool = Field(default=False)
    coverage: Optional[dict] = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Team(SQLModel, table=True):
    """Team dimension table."""
    
    id: int = Field(primary_key=True)
    name: str = Field(max_length=200)
    code: Optional[str] = Field(max_length=10)
    country_id: Optional[int] = Field(foreign_key="country.id")
    founded: Optional[int]
    national: bool = Field(default=False)
    logo: Optional[str] = Field(max_length=255)
    venue_id: Optional[int] = Field(foreign_key="venue.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    country: Optional[Country] = Relationship(back_populates="teams")
    venue: Optional["Venue"] = Relationship(back_populates="teams")
    home_fixtures: List["Fixture"] = Relationship(
        back_populates="home_team",
        sa_relationship_kwargs={"foreign_keys": "Fixture.home_team_id"}
    )
    away_fixtures: List["Fixture"] = Relationship(
        back_populates="away_team",
        sa_relationship_kwargs={"foreign_keys": "Fixture.away_team_id"}
    )


class Venue(SQLModel, table=True):
    """Venue dimension table."""
    
    id: int = Field(primary_key=True)
    name: str = Field(max_length=200)
    address: Optional[str] = Field(max_length=500)
    city: Optional[str] = Field(max_length=100)
    country_id: Optional[int] = Field(foreign_key="country.id")
    capacity: Optional[int]
    surface: Optional[str] = Field(max_length=50)
    image: Optional[str] = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    country: Optional[Country] = Relationship(back_populates="venues")
    teams: List[Team] = Relationship(back_populates="venue")
    fixtures: List["Fixture"] = Relationship(back_populates="venue")


class Player(SQLModel, table=True):
    """Player dimension table."""
    
    id: int = Field(primary_key=True)
    name: str = Field(max_length=200)
    firstname: Optional[str] = Field(max_length=100)
    lastname: Optional[str] = Field(max_length=100)
    age: Optional[int]
    birth_date: Optional[date]
    birth_place: Optional[str] = Field(max_length=200)
    birth_country: Optional[str] = Field(max_length=100)
    nationality: Optional[str] = Field(max_length=100)
    height: Optional[str] = Field(max_length=10)
    weight: Optional[str] = Field(max_length=10)
    injured: bool = Field(default=False)
    photo: Optional[str] = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Bookmaker(SQLModel, table=True):
    """Bookmaker dimension table."""
    
    id: int = Field(primary_key=True)
    name: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BetDefMarket(SQLModel, table=True):
    """Bet market definition table."""
    __tablename__ = "bet_def_market"
    
    id: int = Field(primary_key=True)
    name: str = Field(max_length=100)
    description: Optional[str] = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BetDefValue(SQLModel, table=True):
    """Bet value definition table."""
    __tablename__ = "bet_def_value"
    
    id: int = Field(primary_key=True)
    market_id: int = Field(foreign_key="bet_def_market.id")
    value: str = Field(max_length=50)
    description: Optional[str] = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# FACT MODELS
# =============================================================================

class Fixture(SQLModel, table=True):
    """Fixture fact table."""
    
    id: int = Field(primary_key=True)
    referee: Optional[str] = Field(max_length=200)
    timezone: Optional[str] = Field(max_length=50)
    date: datetime
    timestamp: Optional[int]
    
    # Venue
    venue_id: Optional[int] = Field(foreign_key="venue.id")
    
    # Status
    status_short: str = Field(max_length=10)
    status_long: Optional[str] = Field(max_length=50)
    status_elapsed: Optional[int]
    status_extra: Optional[int]
    
    # League and season
    league_id: int = Field(foreign_key="league.id")
    season_year: int
    round: Optional[str] = Field(max_length=100)
    
    # Teams
    home_team_id: int = Field(foreign_key="team.id")
    away_team_id: int = Field(foreign_key="team.id")
    
    # Scores
    home_goals: int = Field(default=0)
    away_goals: int = Field(default=0)
    home_goals_ht: int = Field(default=0)
    away_goals_ht: int = Field(default=0)
    home_goals_et: int = Field(default=0)
    away_goals_et: int = Field(default=0)
    home_goals_pen: int = Field(default=0)
    away_goals_pen: int = Field(default=0)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    venue: Optional[Venue] = Relationship(back_populates="fixtures")
    league: League = Relationship(back_populates="fixtures")
    home_team: Team = Relationship(
        back_populates="home_fixtures",
        sa_relationship_kwargs={"foreign_keys": "Fixture.home_team_id"}
    )
    away_team: Team = Relationship(
        back_populates="away_fixtures",
        sa_relationship_kwargs={"foreign_keys": "Fixture.away_team_id"}
    )


# =============================================================================
# TIMESCALEDB HYPERTABLE MODELS
# =============================================================================

class LiveOddsTick(SQLModel, table=True):
    """Live odds tick hypertable."""
    __tablename__ = "live_odds_tick"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column=Column(UUID(as_uuid=True))
    )
    fixture_id: int = Field(foreign_key="fixture.id")
    bookmaker_id: int = Field(foreign_key="bookmaker.id")
    bet_market_id: int = Field(foreign_key="bet_def_market.id")
    bet_value: str = Field(max_length=50)
    
    # Odds data
    odd_value: Decimal = Field(sa_column=Column(DECIMAL(10, 2)))
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    match_minute: Optional[int]
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LiveEventTick(SQLModel, table=True):
    """Live event tick hypertable."""
    __tablename__ = "live_event_tick"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column=Column(UUID(as_uuid=True))
    )
    fixture_id: int = Field(foreign_key="fixture.id")
    
    # Event details
    event_type: str = Field(max_length=50)
    event_detail: Optional[str] = Field(max_length=100)
    event_comments: Optional[str] = Field(sa_column=Column(Text))
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    match_minute: Optional[int]
    match_minute_extra: Optional[int]
    
    # Team and player
    team_id: Optional[int] = Field(foreign_key="team.id")
    player_id: Optional[int] = Field(foreign_key="player.id")
    assist_player_id: Optional[int] = Field(foreign_key="player.id")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LiveStatsTick(SQLModel, table=True):
    """Live stats tick hypertable."""
    __tablename__ = "live_stats_tick"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column=Column(UUID(as_uuid=True))
    )
    fixture_id: int = Field(foreign_key="fixture.id")
    team_id: int = Field(foreign_key="team.id")
    
    # Match statistics
    shots_on_goal: int = Field(default=0)
    shots_off_goal: int = Field(default=0)
    total_shots: int = Field(default=0)
    blocked_shots: int = Field(default=0)
    shots_inside_box: int = Field(default=0)
    shots_outside_box: int = Field(default=0)
    fouls: int = Field(default=0)
    corner_kicks: int = Field(default=0)
    offsides: int = Field(default=0)
    ball_possession: int = Field(default=0)  # percentage
    yellow_cards: int = Field(default=0)
    red_cards: int = Field(default=0)
    goalkeeper_saves: int = Field(default=0)
    total_passes: int = Field(default=0)
    passes_accurate: int = Field(default=0)
    passes_percentage: int = Field(default=0)
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    match_minute: Optional[int]
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# OTHER FACT MODELS
# =============================================================================

class PrematchOdds(SQLModel, table=True):
    """Prematch odds snapshots."""
    __tablename__ = "prematch_odds"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column=Column(UUID(as_uuid=True))
    )
    fixture_id: int = Field(foreign_key="fixture.id")
    bookmaker_id: int = Field(foreign_key="bookmaker.id")
    bet_market_id: int = Field(foreign_key="bet_def_market.id")
    bet_value: str = Field(max_length=50)
    
    # Odds data
    odd_value: Decimal = Field(sa_column=Column(DECIMAL(10, 2)))
    
    # Timing
    snapshot_time: datetime = Field(default_factory=datetime.utcnow)
    hours_before_match: Optional[int]
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Standing(SQLModel, table=True):
    """League standings table."""
    
    id: int = Field(primary_key=True)
    league_id: int = Field(foreign_key="league.id")
    season_year: int
    team_id: int = Field(foreign_key="team.id")
    
    # Position
    rank: int
    points: int = Field(default=0)
    
    # Matches
    matches_played: int = Field(default=0)
    wins: int = Field(default=0)
    draws: int = Field(default=0)
    losses: int = Field(default=0)
    
    # Goals
    goals_for: int = Field(default=0)
    goals_against: int = Field(default=0)
    goal_difference: int = Field(default=0)
    
    # Form and status
    form: Optional[str] = Field(max_length=5)  # e.g., "WWDLL"
    status: Optional[str] = Field(max_length=50)
    description: Optional[str] = Field(sa_column=Column(Text))
    
    # Metadata
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    league: League = Relationship(back_populates="standings")


# =============================================================================
# SYSTEM MODELS
# =============================================================================

class SystemConfig(SQLModel, table=True):
    """System configuration table."""
    __tablename__ = "system_config"
    
    id: int = Field(primary_key=True)
    key: str = Field(max_length=100, unique=True)
    value: Optional[str] = Field(sa_column=Column(Text))
    description: Optional[str] = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(SQLModel, table=True):
    """Audit log table."""
    __tablename__ = "audit_log"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column=Column(UUID(as_uuid=True))
    )
    table_name: str = Field(max_length=100)
    record_id: str = Field(max_length=100)
    operation: str = Field(max_length=10)  # INSERT, UPDATE, DELETE
    old_values: Optional[dict] = Field(sa_column=Column(JSON))
    new_values: Optional[dict] = Field(sa_column=Column(JSON))
    changed_by: Optional[str] = Field(max_length=100)
    changed_at: datetime = Field(default_factory=datetime.utcnow)
