# constants.py
# Centralized UI / Asset constants
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap


# =========================================================
# Base Paths
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
FONTS_DIR = ASSETS_DIR / "fonts"
SFX_DIR = ASSETS_DIR / "sound"
CONFIG_DIR = BASE_DIR / "config"

# =========================================================
# Image File Paths
# =========================================================
LOGO = Path(IMAGES_DIR / "logo.jpg").as_posix()
def logo_icon():
    """Return the cached logo pixmap (created on first call)."""
    if not hasattr(logo_icon, "_cached"):
        logo_icon._cached = QPixmap(LOGO).scaled(
            240, 184,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
    return logo_icon._cached
BLURRED_LOGO = Path(IMAGES_DIR / "blurredlogo.jpg").as_posix()

DBINIT_PATH = CONFIG_DIR / "database.ini"
DBINIT_SEC = "postgresql"


# =========================================================
# Network
# =========================================================

SOCKET_BROADCAST = "7500"
SOCKET_RECEIVE = "7501"
RECIEVE_INPUT = "0.0.0.0"
BROADCAST_INPUT = "127.0.0.1"

CODE_GAMESTART = "202"
CODE_GAMEEND = "221"

CODE_BASESCORE_RED = "53"
CODE_BASESCORE_GREEN = "43"

# =========================================================
# Database
# =========================================================
NEW_CODENAME_ADDED = 0
EXISTING_CODENAME_UPDATED = 1
CODENAME_ALREADY_EXISTS = 2
ERROR_OCCURRED = 3
CODENAME_CHANGE_ATTEMPT_MATCHES_EXISTING = 4
COOL_GUY_EMOJI = f"\U0001F60E"

# =========================================================
# Gameplay
# =========================================================

MAX_NUM_PLAYER = 15
MAX_NUM_PLAYER_MINUSONE = 14
NUM_TEAM = 2

SCORE_BASE = 100
PENALTY_BASE = 0

SCORE_TAKEDOWN = 10
PENALTY_TAKEDOWN = -10

BASE_EQUIP_ID = 100

DEV_CODENAMES_RED = [
    "Viper", "Cobra", "Blaze", "Inferno", "Ember",
    "Scorch", "Crimson", "Fury", "Havoc", "Reaper",
    "Torch", "Flame", "Magma", "Cinder", "Ash",
]
DEV_CODENAMES_GREEN = [
    "Ghost", "Cipher", "Frost", "Storm", "Titan",
    "Echo", "Wraith", "Nova", "Specter", "Atlas",
    "Phantom", "Shadow", "Mirage", "Rogue", "Stealth",
]
DEV_CODENAMES = DEV_CODENAMES_RED
DEV_RED_EQUIP_IDS  = [1,  3,  5,  7,  9,  11, 13, 15, 17, 19, 21, 23, 25, 27, 29]
DEV_GREEN_EQUIP_IDS = [2,  4,  6,  8,  10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]

# =========================================================
# Colors (Hex / RGB)
# =========================================================

SEMI_TRANSPARENT_BLACK = "rgba(0, 0, 0, 180)"
RED = "rgba(100, 0, 0, 150)"
GREEN = "rgba(0, 100, 0, 150)"
DARK_GREY = "#555555"
DEEP_RED = "#b30000"
LIGHT_RED = "#e60000"
COLOR_SCORE_FLASH = "#ffee00"
COLOR_EQUIP_LABEL = "#00c8ff"
BLUR_RADIUS = 15
DROPSHADOW_OFFSET_AMOUNT = (0, 5)
SHADOW_COLOR = (0, 0, 0, 160)
CONTENT_MARGINS = (0, 0, 0, 0)

# Neon palette
NEON_CYAN = "#00ffff"
NEON_RED_BRIGHT = "#ff3333"
NEON_GREEN_BRIGHT = "#00ff55"
NEON_BLUE = "#0088ff"
NEON_YELLOW = "#ffee00"

BLURRED_LOGO_BACKGROUND = f"""
                border-image: url('{BLURRED_LOGO}');
                background-position: center;
        """

# =========================================================
# Fonts
# =========================================================
AUDIOWIDE_FONT_PATH = str(FONTS_DIR / "Audiowide-Regular.ttf")
AUDIOWIDE_FONT_FAMILY = "'Audiowide', 'Orbitron', sans-serif"
PRESS_START_2P_FONT_PATH = str(FONTS_DIR / "PressStart2P-Regular.ttf")
PRESS_START_2P_FONT_FAMILY = "'Press Start 2P', 'Courier New', monospace"

def load_application_fonts():
    from PyQt6.QtGui import QFontDatabase
    if Path(AUDIOWIDE_FONT_PATH).exists():
        QFontDatabase.addApplicationFont(AUDIOWIDE_FONT_PATH)
    if Path(PRESS_START_2P_FONT_PATH).exists():
        QFontDatabase.addApplicationFont(PRESS_START_2P_FONT_PATH)

# =========================================================
# Window / Layout
# =========================================================
VERTICAL_SPACING = 12
COOL_FONT = f"font-family: 'Orbitron', 'Courier New'; font-size: 13px; font-weight: bold; background-color: #000a14; color: {NEON_CYAN};"
# Entry-screen input fields: transparent floating text, no box
RED_TEAM_BACKGROUND = f"font-family: 'Courier New', monospace; font-size: 12px; font-weight: bold; color: white; background-color: transparent; border: none; border-bottom: 1px solid rgba(255, 60, 60, 55); selection-background-color: rgba(180, 30, 30, 160);"
GREEN_TEAM_BACKGROUND = f"font-family: 'Courier New', monospace; font-size: 12px; font-weight: bold; color: white; background-color: transparent; border: none; border-bottom: 1px solid rgba(50, 220, 100, 55); selection-background-color: rgba(30, 150, 60, 160);"
HORIZONTAL_SPACING = 20
NETWORK_SECTION_HEIGHT = 30
NETWORK_SECTION_SPACING = 20
ASPECT_RATIO = 4/5
BUTTON_DIMENSIONS = 60
X_ORIGIN = "(QGuiApplication.primaryScreen().availableGeometry().width() - eval(WINDOW_WIDTH)) // 2"
Y_ORIGIN = "(QGuiApplication.primaryScreen().availableGeometry().height() - eval(WINDOW_HEIGHT)) // 2"
WINDOW_WIDTH = "QGuiApplication.primaryScreen().availableGeometry().width() * ASPECT_RATIO"
WINDOW_HEIGHT = "QGuiApplication.primaryScreen().availableGeometry().height() * ASPECT_RATIO"
WINDOW_STAYS_ON_TOP = True
def window_stays_on_top(self, enable):
    if enable:
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
    else:
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
    self.show()

# =========================================================
# UI Styles
# =========================================================
STYLE_CONFIG_WINDOW = f"""
    #ConfigWindow {{
        background-color: #000a14;
    }}
    QLabel {{
        color: {NEON_CYAN};
        font-family: 'Orbitron', 'Courier New', monospace;
        font-size: 14px;
        letter-spacing: 1px;
    }}
    QLineEdit {{
        background-color: rgba(0, 15, 35, 220);
        border: 1px solid {NEON_CYAN};
        border-radius: 3px;
        padding: 8px;
        color: {NEON_CYAN};
        font-family: 'Orbitron', 'Courier New', monospace;
        font-size: 13px;
        min-width: 220px;
    }}
    QLineEdit:focus {{
        border: 2px solid {NEON_BLUE};
    }}
    QPushButton {{
        background-color: rgba(180, 0, 0, 200);
        border: 2px solid {NEON_RED_BRIGHT};
        padding: 10px 25px;
        border-radius: 3px;
        font-weight: bold;
        font-size: 15px;
        font-family: 'Orbitron', 'Courier New', monospace;
        color: white;
        letter-spacing: 2px;
    }}
    QPushButton:hover {{
        background-color: rgba(220, 0, 0, 230);
        border: 2px solid white;
        color: {NEON_YELLOW};
    }}
"""
STYLE_CONFIG_TITLE = f"font-size: 24px; font-weight: bold; color: {NEON_CYAN}; font-family: 'Orbitron', 'Courier New'; letter-spacing: 3px;"
STYLE_ACTION_BUTTON = f"""
    background-color: rgba(0, 30, 80, 200);
    border: 2px solid {NEON_BLUE};
    border-radius: 4px;
    padding: 5px;
    font-weight: bold;
    font-size: 13px;
    font-family: 'Orbitron', 'Courier New', sans-serif;
    color: {NEON_CYAN};
    letter-spacing: 1px;
"""
STYLE_TEAM_LABEL_ENTRY_RED = f"""
    color: white;
    font-weight: bold;
    font-size: 32px;
    font-family: 'Orbitron', 'Courier New', sans-serif;
    background-color: rgba(150, 0, 0, 200);
    border: 3px solid {NEON_RED_BRIGHT};
    border-radius: 3px;
    padding: 8px 20px;
    margin: 8px;
    letter-spacing: 5px;
"""
STYLE_TEAM_LABEL_ENTRY_GREEN = f"""
    color: white;
    font-weight: bold;
    font-size: 32px;
    font-family: 'Orbitron', 'Courier New', sans-serif;
    background-color: rgba(0, 110, 0, 200);
    border: 3px solid {NEON_GREEN_BRIGHT};
    border-radius: 3px;
    padding: 8px 20px;
    margin: 8px;
    letter-spacing: 5px;
"""
STYLE_TEAM_LABEL_PLAY_RED = f"""
    color: white;
    font-size: 12px;
    font-family: {PRESS_START_2P_FONT_FAMILY};
    background-color: rgba(150, 0, 0, 200);
    border-bottom: 2px solid {NEON_RED_BRIGHT};
    padding: 10px 15px;
"""
STYLE_TEAM_LABEL_PLAY_GREEN = f"""
    color: white;
    font-size: 12px;
    font-family: {PRESS_START_2P_FONT_FAMILY};
    background-color: rgba(0, 110, 0, 200);
    border-bottom: 2px solid {NEON_GREEN_BRIGHT};
    padding: 10px 15px;
"""
STYLE_SEMI_TRANSPARENT_CONTAINER = f"background-color: rgba(0, 6, 20, 210); border: 2px solid {NEON_CYAN}; border-radius: 3px;"
STYLE_TEAM_SCORE_LABEL = f"color: {NEON_CYAN}; font-weight: bold; font-size: 16px; font-family: 'Orbitron', 'Courier New'; letter-spacing: 1px; padding: 5px;"
STYLE_TEAM_SCORE_LABEL_FLASH = f"color: {NEON_YELLOW}; font-weight: bold; font-size: 18px; font-family: 'Orbitron', 'Courier New'; letter-spacing: 1px; padding: 5px;"
# Team-specific total bar styles used in PlayActionWindow score labels
STYLE_TEAM_SCORE_LABEL_RED = f"""
    background-color: rgba(160, 0, 0, 210);
    border-top: 2px solid {NEON_RED_BRIGHT};
    border-bottom: 2px solid {NEON_RED_BRIGHT};
    padding: 6px 10px;
"""
STYLE_TEAM_SCORE_LABEL_GREEN = f"""
    background-color: rgba(0, 120, 0, 210);
    border-top: 2px solid {NEON_GREEN_BRIGHT};
    border-bottom: 2px solid {NEON_GREEN_BRIGHT};
    padding: 6px 10px;
"""
STYLE_TEAM_SCORE_LABEL_FLASH_RED = f"""
    background-color: rgba(210, 30, 0, 230);
    border-top: 2px solid {NEON_YELLOW};
    border-bottom: 2px solid {NEON_YELLOW};
    padding: 6px 10px;
"""
STYLE_TEAM_SCORE_LABEL_FLASH_GREEN = f"""
    background-color: rgba(0, 160, 30, 230);
    border-top: 2px solid {NEON_YELLOW};
    border-bottom: 2px solid {NEON_YELLOW};
    padding: 6px 10px;
"""
STYLE_SECTION_LABEL = f"color: {NEON_CYAN}; font-weight: bold; font-size: 18px; font-family: 'Orbitron', 'Courier New'; letter-spacing: 2px;"
STYLE_TIMER_DISPLAY = f"color: {NEON_YELLOW}; font-size: 52px; font-weight: bold; font-family: 'Orbitron', 'Courier New'; letter-spacing: 6px;"
# Neon blue used on all player-list text
NEON_BLUE_TEXT = "#00c8ff"
# Glow effect constants for player-list labels (QGraphicsDropShadowEffect)
TEAM_LABEL_GLOW_COLOR = (255, 255, 255, 210)
TEAM_LABEL_GLOW_BLUR = 22
PLAYER_LABEL_GLOW_COLOR = (0, 180, 255, 200)
PLAYER_LABEL_GLOW_COLOR_RED = (255, 50, 50, 200)
PLAYER_LABEL_GLOW_COLOR_GREEN = (40, 255, 100, 200)
PLAYER_LABEL_GLOW_BLUR = 16
PLAYER_LABEL_SHADOW_OFFSET = (0, 2)
SCORE_GLOW_COLOR = (255, 230, 0, 255)
SCORE_GLOW_BLUR_MAX = 38
SCORE_GLOW_BLUR_MIN = 4
SCORE_GLOW_TICK_MS = 40
SCORE_GLOW_DURATION_MS = 2000
SCORE_GLOW_CYCLES = 1
# Play-window column headers — Audiowide, smaller so they don't crowd
STYLE_GRID_HEADER = f"color: {NEON_BLUE_TEXT}; font-weight: bold; font-size: 11px; font-family: {AUDIOWIDE_FONT_FAMILY}; background-color: rgba(0, 40, 80, 200); padding: 4px 2px; letter-spacing: 1px;"
# Entry-window column headers keep Orbitron
STYLE_ENTRY_GRID_HEADER = f"color: white; font-weight: bold; font-size: 11px; font-family: 'Orbitron', 'Courier New'; letter-spacing: 1px; background-color: rgba(0, 40, 80, 200); padding: 3px 2px;"
# Player row labels — Audiowide 14px neon blue (glow added in code via QGraphicsDropShadowEffect)
STYLE_PLAYER_LABEL = f"color: {NEON_BLUE_TEXT}; font-size: 16px; font-family: {AUDIOWIDE_FONT_FAMILY};"
STYLE_PLAYER_LABEL_ALT = f"color: {NEON_BLUE_TEXT}; font-size: 16px; font-family: {AUDIOWIDE_FONT_FAMILY}; background-color: rgba(255, 255, 255, 6);"
STYLE_EQUIP_LABEL = f"color: {NEON_BLUE_TEXT}; font-size: 16px; font-weight: bold; font-family: {AUDIOWIDE_FONT_FAMILY};"
STYLE_EQUIP_LABEL_ALT = f"color: {NEON_BLUE_TEXT}; font-size: 16px; font-weight: bold; font-family: {AUDIOWIDE_FONT_FAMILY}; background-color: rgba(255, 255, 255, 6);"
STYLE_SCORE_LABEL = f"color: {NEON_YELLOW}; font-size: 16px; font-weight: bold; font-family: {AUDIOWIDE_FONT_FAMILY};"
STYLE_SCORE_LABEL_ALT = f"color: {NEON_YELLOW}; font-size: 16px; font-weight: bold; font-family: {AUDIOWIDE_FONT_FAMILY}; background-color: rgba(255, 255, 255, 6);"
STYLE_PLAYER_INDEX_LABEL = f"color: {NEON_CYAN}; font-weight: bold; font-family: 'Courier New'; font-size: 11px;"
STYLE_BASE_CODENAME_LABEL = f"color: {NEON_YELLOW}; font-size: 11px; font-family: {AUDIOWIDE_FONT_FAMILY};"
HIT_FEED_MAX_ITEMS = 10
STYLE_HIT_FEED_LIST = f"""
    QListWidget {{
        background-color: rgba(0, 6, 20, 160);
        color: {NEON_CYAN};
        font-size: 12px;
        font-family: 'Courier New', monospace;
        border: none;
        border-radius: 2px;
    }}
    QListWidget::item {{
        padding: 3px 5px;
        border-bottom: 1px solid rgba(0, 255, 255, 20);
    }}
    QListWidget::item:selected {{
        background-color: rgba(0, 50, 80, 200);
    }}
"""

# =========================================================
# Panel Paint Constants
# =========================================================
# Near-black fill with a subtle team tint — dark like the reference image panels
COLOR_PANEL_BG_RED = (12, 0, 0, 235)
COLOR_PANEL_BG_GREEN = (0, 14, 0, 235)
COLOR_PANEL_GLOW_RED = (255, 40, 40)
COLOR_PANEL_GLOW_GREEN = (40, 255, 100)
# Layers: outer glow fades in → innermost is a solid bright border line
PANEL_GLOW_LAYERS = [(8, 8), (5, 22), (3, 65), (2, 255)]
PANEL_BORDER_RADIUS = 3
PANEL_CORNER_MARK_SIZE = 22
PANEL_CORNER_MARK_WIDTH = 3
COLOR_CORNER_MARK_RED = (255, 130, 100)
COLOR_CORNER_MARK_GREEN = (120, 255, 190)

# =========================================================
# Layout Sizes
# =========================================================
PANEL_WIDTH_RATIO = 0.48
PANEL_HEIGHT_RATIO = 0.6
ACTION_BUTTON_WIDTH = 120
ACTION_BUTTON_HEIGHT = 60
PLAYER_ID_FIELD_WIDTH = 100
FIELD_HEIGHT = 28
CODENAME_FIELD_WIDTH = 140
PLAYER_INDEX_LABEL_WIDTH = 70
BASEICON_SIZE = 32
BASEICON_COL_WIDTH = 46
LOGO_MAX_WIDTH_RATIO = 0.55
LOGO_MAX_HEIGHT_RATIO = 0.48
LOGO_BOTTOM_GAP = 8
PHASE_GLOW_COLOR = (0, 200, 255, 255)
PHASE_GLOW_COLOR_RED = (255, 30, 30, 255)
PHASE_GLOW_COLOR_WHITE = (255, 255, 255, 220)
PHASE_GLOW_BLUR_MAX = 28
PHASE_GLOW_BLUR_MIN = 4
PHASE_GLOW_TICK_MS = 40
PHASE_GLOW_CYCLE_MS = 1400
STYLE_PHASE_LABEL = f"color: #00c8ff; font-size: 16px; font-family: {PRESS_START_2P_FONT_FAMILY}; letter-spacing: 2px;"
STYLE_PHASE_LABEL_RED = f"color: #ff2020; font-size: 16px; font-family: {PRESS_START_2P_FONT_FAMILY}; letter-spacing: 2px;"
STYLE_PHASE_LABEL_WHITE = f"color: white; font-size: 16px; font-family: {PRESS_START_2P_FONT_FAMILY}; letter-spacing: 2px;"

# =========================================================
# Timing
# =========================================================
FLASH_INTERVAL_MS = 500
TIMER_INTERVAL_MS = 1000
MUSIC_START_THRESHOLD = 17
COUNTDOWN_READY_SECONDS = 30
GAME_DURATION_SECONDS = 360
DEV_COUNTDOWN_READY_SECONDS = 5
DEV_GAME_DURATION_SECONDS = 5

APP_NAME = "Photon Main"
