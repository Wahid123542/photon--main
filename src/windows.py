import socket
import constants
import database
from sound_manager import SoundManager
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QLineEdit, QLabel, QWidget, QPushButton,
    QFormLayout, QMessageBox, QHBoxLayout, QGridLayout, QGraphicsDropShadowEffect,
    QListWidget, QListWidgetItem, QSizePolicy, QApplication
)
from udp_server import UDPServer
from PyQt6.QtGui import QGuiApplication, QPainter, QPen, QBrush, QColor, QFont, QPixmap, QImage, QPainterPath
from PyQt6.QtCore import Qt, QTimer, QEvent, pyqtSignal, QSize, QPoint
from util import isDevMode
from constants import *
from model import Model

def _team_score_html(value: int) -> str:
    return (
        f'<span style="font-family:\'Press Start 2P\',monospace;font-size:8px;color:white;">'
        f'TEAM SCORE</span>'
        f'&nbsp;&nbsp;'
        f'<span style="font-family:\'Audiowide\',sans-serif;font-size:18px;'
        f'font-weight:bold;color:{NEON_YELLOW};">{value}</span>'
    )

def _team_glow() -> QGraphicsDropShadowEffect:
    fx = QGraphicsDropShadowEffect()
    fx.setBlurRadius(TEAM_LABEL_GLOW_BLUR)
    fx.setOffset(0, 0)
    fx.setColor(QColor(*TEAM_LABEL_GLOW_COLOR))
    return fx

class HintOverlay(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setStyleSheet(
            "background-color: rgba(0,0,0,170);"
            "color: white;"
            "font-family: 'Audiowide', sans-serif;"
            "font-size: 13px;"
            "padding: 8px 18px;"
            "border-radius: 8px;"
        )
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)
        self.hide()

    def show_hint(self, text):
        self._timer.stop()
        self.setText(text)
        self.adjustSize()
        self.reposition()
        self.show()
        self.raise_()
        self._timer.start(3000)

    def reposition(self):
        p = self.parent()
        if p is None:
            return
        self.adjustSize()
        self.move((p.width() - self.width()) // 2, p.height() - self.height() - 24)


class UDPConfigWindow(QWidget):
    def __init__(self, window_size):
        super().__init__()
        self.setWindowTitle("Photon - Network Configuration")
        self.resize(window_size)
        self.setObjectName("ConfigWindow")
        self.setStyleSheet(STYLE_CONFIG_WINDOW)
        load_application_fonts()
        layout = QVBoxLayout(self)
        layout.addStretch()
        title = QLabel("UDP Network Setup")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(STYLE_CONFIG_TITLE)
        layout.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setVerticalSpacing(VERTICAL_SPACING)
        form.setHorizontalSpacing(HORIZONTAL_SPACING)
        self.receive_input = QLineEdit(f"{RECIEVE_INPUT}")
        self.broadcast_input = QLineEdit(f"{BROADCAST_INPUT}")
        self.receive_input.setFixedHeight(NETWORK_SECTION_HEIGHT)
        self.broadcast_input.setFixedHeight(NETWORK_SECTION_HEIGHT)
        form.addRow("Receive IP:", self.receive_input)
        form.addRow("Broadcast IP:", self.broadcast_input)
        layout.addLayout(form)
        layout.addSpacing(NETWORK_SECTION_SPACING)

        self.start_button = QPushButton("Start System")
        self.start_button.clicked.connect(self.start_system)
        layout.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        self.main_window = None

        if isDevMode():
            self.start_system()
            self.close()
            return

    def validate_ip(self, ip):
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False

    def start_system(self):
        receive_ip = self.receive_input.text().strip()
        broadcast_ip = self.broadcast_input.text().strip()
        if not receive_ip or not broadcast_ip:
            QMessageBox.warning(self, "Missing Input", "Please enter both Receive IP and Broadcast IP.")
            return
        if not self.validate_ip(receive_ip):
            QMessageBox.warning(self, "Invalid IP", "Receive IP is not valid.")
            return
        if not self.validate_ip(broadcast_ip):
            QMessageBox.warning(self, "Invalid IP", "Broadcast IP is not valid.")
            return
        try:
            udp = UDPServer(receive_ip=receive_ip, broadcast_ip=broadcast_ip)
            self.model = Model(udp)
            udp.assign_model(self.model)
        except OSError:
            QMessageBox.warning(self, "Network Error", "Unable to bind to the specified IP address.")
            return
        self.main_window = MainWindow(udp, self.model)
        self.main_window.show()
        self.close()

class MainWindow(QMainWindow):
    def __init__(self, udp_server: UDPServer, model: Model):
        self.udp = udp_server
        self.model = model
        self.db = database
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("PHOTON")
        screen = QGuiApplication.primaryScreen().availableGeometry()
        window_width = screen.width() * ASPECT_RATIO
        window_height = screen.height() * ASPECT_RATIO
        x = (screen.width() - window_width) // 2
        y = (screen.height() - window_height) // 2
        self._default_w = int(window_width)
        self._default_h = int(window_height)
        self.setGeometry(int(x), int(y), self._default_w, self._default_h)
        self.setMinimumSize(480, 320)

        central_widget = QWidget()
        central_widget.setObjectName("MainWindowWidget")
        central_widget.setStyleSheet(f"""
            #MainWindowWidget {{
                border-image: url('{BLURRED_LOGO}');
                background-position: center;
            }}
        """)
        self.setCentralWidget(central_widget)
        self._hint = HintOverlay(self.centralWidget())

        team_layout = QHBoxLayout(central_widget)
        team_layout.setContentsMargins(0, 0, 0, 0)
        team_layout.setSpacing(0)

        self.left_container = QWidget()
        left_layout = QVBoxLayout(self.left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self.red_panel = RedTeamPanel()
        self.red_panel.setLayout(QVBoxLayout())

        self.right_container = QWidget()
        right_layout = QVBoxLayout(self.right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.green_panel = GreenTeamPanel()
        self.green_panel.setLayout(QVBoxLayout())

        self.red_label = QLabel("RED TEAM")
        self.green_label = QLabel("GREEN TEAM")
        self.red_label.setStyleSheet(STYLE_TEAM_LABEL_ENTRY_RED)
        self.red_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.green_label.setStyleSheet(STYLE_TEAM_LABEL_ENTRY_GREEN)
        self.green_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        red_shadow = QGraphicsDropShadowEffect()
        red_shadow.setBlurRadius(BLUR_RADIUS)
        red_shadow.setOffset(*DROPSHADOW_OFFSET_AMOUNT)
        red_shadow.setColor(QColor(*SHADOW_COLOR))
        self.red_label.setGraphicsEffect(red_shadow)

        green_shadow = QGraphicsDropShadowEffect()
        green_shadow.setBlurRadius(BLUR_RADIUS)
        green_shadow.setOffset(*DROPSHADOW_OFFSET_AMOUNT)
        green_shadow.setColor(QColor(*SHADOW_COLOR))
        self.green_label.setGraphicsEffect(green_shadow)

        left_layout.addStretch(2)
        left_layout.addWidget(self.red_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout.addStretch(1)
        left_layout.addWidget(self.red_panel, alignment=Qt.AlignmentFlag.AlignHCenter)

        right_layout.addStretch(2)
        right_layout.addWidget(self.green_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        right_layout.addStretch(1)
        right_layout.addWidget(self.green_panel, alignment=Qt.AlignmentFlag.AlignHCenter)

        team_layout.addWidget(self.left_container, 1)
        team_layout.addWidget(self.right_container, 1)

        self.red_index_labels = []
        self.green_index_labels = []
        self.red_entries = self.create_player_grid(self.red_panel.layout(), "RED", self.red_index_labels)
        self.green_entries = self.create_player_grid(self.green_panel.layout(), "GREEN", self.green_index_labels)

        self.update_panel_sizes()

        self.new_game_button = QPushButton("New Game", self.centralWidget())
        self.new_game_button.setFixedSize(ACTION_BUTTON_WIDTH, ACTION_BUTTON_HEIGHT)
        self.new_game_button.move(0, 0)
        self.new_game_button.setStyleSheet(STYLE_ACTION_BUTTON)
        self._btn_shadow = QGraphicsDropShadowEffect()
        self._btn_shadow.setBlurRadius(BLUR_RADIUS)
        self._btn_shadow.setOffset(*DROPSHADOW_OFFSET_AMOUNT)
        self._btn_shadow.setColor(QColor(*SHADOW_COLOR))
        self.new_game_button.setGraphicsEffect(self._btn_shadow)
        self.new_game_button.raise_()
        self.new_game_button.clicked.connect(self.clear_all_grids)

        if isDevMode():
            self._populate_dev_entries()

        self.play_action_window = PlayActionWindow(self, self.udp, self.model)
        self.start_game_button = QPushButton("Start Game", self.centralWidget())
        self.start_game_button.setFixedSize(ACTION_BUTTON_WIDTH, ACTION_BUTTON_HEIGHT)
        window_height = self.height()
        window_width = self.width()
        self.start_game_button.move(int(window_width/2 - self.start_game_button.width()/2), 0)
        self.start_game_button.setStyleSheet(STYLE_ACTION_BUTTON)
        self._start_shadow = QGraphicsDropShadowEffect()
        self._start_shadow.setBlurRadius(BLUR_RADIUS)
        self._start_shadow.setOffset(*DROPSHADOW_OFFSET_AMOUNT)
        self._start_shadow.setColor(QColor(*SHADOW_COLOR))
        self.start_game_button.setGraphicsEffect(self._start_shadow)
        self.start_game_button.raise_()
        self.start_game_button.clicked.connect(self.show_play_action_window)

    def _populate_dev_entries(self):
        for i, (row, equip) in enumerate(zip(self.red_entries, DEV_RED_EQUIP_IDS)):
            row[0].setText(str(i + 1))
            row[1].setText(DEV_CODENAMES_RED[i])
            row[1].setReadOnly(False)
            row[2].setText(str(equip))
            row[2].setReadOnly(False)
            self.red_index_labels[i].setText(f"Player #{i + 1}")
        for i, (row, equip) in enumerate(zip(self.green_entries, DEV_GREEN_EQUIP_IDS)):
            row[0].setText(str(i + 16))
            row[1].setText(DEV_CODENAMES_GREEN[i])
            row[1].setReadOnly(False)
            row[2].setText(str(equip))
            row[2].setReadOnly(False)
            self.green_index_labels[i].setText(f"Player #{i + 1}")

    def update_panel_sizes(self):
        if not hasattr(self, 'red_panel'):
            return
        w = self.width()
        h = self.height()
        panel_width = int(w * PANEL_WIDTH_RATIO)
        panel_height = int(h * PANEL_HEIGHT_RATIO)
        self.red_panel.setFixedSize(panel_width, panel_height)
        self.green_panel.setFixedSize(panel_width, panel_height)

    def _reposition_buttons(self):
        if not hasattr(self, 'start_game_button'):
            return
        self.new_game_button.move(0, 0)
        self.start_game_button.move(
            int(self.width() / 2 - self.start_game_button.width() / 2), 0
        )

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(800, lambda: self._hint.show_hint("Press F11 for Fullscreen"))

    def moveEvent(self, event):
        super().moveEvent(event)
        self.setUpdatesEnabled(False)
        QTimer.singleShot(200, lambda: self.setUpdatesEnabled(True))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self.update_panel_sizes)
        QTimer.singleShot(0, self._reposition_buttons)
        self._hint.reposition()

    def create_player_grid(self, parent_layout, team_name, index_label_list):
        player_entry_grid = QGridLayout()
        player_entry_grid.setHorizontalSpacing(15)
        player_entry_grid.setVerticalSpacing(8)

        id_prompt = QLabel("Player ID")
        eq_prompt = QLabel("Equipment ID")
        codename_prompt = QLabel("Codename")
        for lbl in (id_prompt, codename_prompt, eq_prompt):
            lbl.setStyleSheet(STYLE_ENTRY_GRID_HEADER)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        player_entry_grid.addWidget(id_prompt, 0, 1)
        player_entry_grid.addWidget(codename_prompt, 0, 2)
        player_entry_grid.addWidget(eq_prompt, 0, 3)

        background = RED_TEAM_BACKGROUND if team_name == "RED" else GREEN_TEAM_BACKGROUND

        entries = []
        for row in range(1, 16):
            player_index_label = QLabel("")
            player_index_label.setStyleSheet(STYLE_PLAYER_INDEX_LABEL)
            player_index_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            player_index_label.setFixedWidth(PLAYER_INDEX_LABEL_WIDTH)
            player_entry_grid.addWidget(player_index_label, row, 0)
            index_label_list.append(player_index_label)

            id_edit = QLineEdit()
            id_edit.setFixedSize(PLAYER_ID_FIELD_WIDTH, FIELD_HEIGHT)
            id_edit.setStyleSheet(background)

            codename_edit = QLineEdit()
            codename_edit.setFixedSize(CODENAME_FIELD_WIDTH, FIELD_HEIGHT)
            codename_edit.setStyleSheet(background)
            codename_edit.setReadOnly(True)

            equipment_id_edit = QLineEdit()
            equipment_id_edit.setFixedSize(PLAYER_ID_FIELD_WIDTH, FIELD_HEIGHT)
            equipment_id_edit.setStyleSheet(background)
            equipment_id_edit.setReadOnly(True)

            player_entry_grid.addWidget(id_edit, row, 1)
            player_entry_grid.addWidget(codename_edit, row, 2)
            player_entry_grid.addWidget(equipment_id_edit, row, 3)

            row_data = [id_edit, codename_edit, equipment_id_edit]
            entries.append(row_data)

            id_edit.returnPressed.connect(lambda r=row_data, t=team_name, idx=row-1: self.on_id_enter(r, t, idx))
            id_edit.keyPressEvent = lambda event, r=row_data, t=team_name, idx=row-1: self.on_id_keypress(event, r, t, idx)
            codename_edit.returnPressed.connect(lambda r=row_data, t=team_name, idx=row-1: self.on_codename_enter(r, t, idx))
            equipment_id_edit.returnPressed.connect(lambda r=row_data, t=team_name, idx=row-1: self.on_row_submit(r, t, idx))

        parent_layout.setContentsMargins(15, 15, 15, 15)
        parent_layout.addLayout(player_entry_grid)
        return entries

    def _all_entered_player_ids(self, exclude_row_data=None):
        ids = set()
        for row in self.red_entries + self.green_entries:
            if row is exclude_row_data:
                continue
            txt = row[0].text().strip()
            if txt:
                ids.add(txt)
        return ids

    def _all_entered_equipment_ids(self, exclude_row_data=None):
        ids = set()
        for row in self.red_entries + self.green_entries:
            if row is exclude_row_data:
                continue
            txt = row[2].text().strip()
            if txt:
                ids.add(txt)
        return ids

    def get_red_team_data(self):
        red_team_data = []
        for row in self.red_entries:
            id_text = row[0].text().strip()
            codename_text = row[1].text().strip()
            equip_text = row[2].text().strip()
            if id_text and codename_text and equip_text:
                red_team_data.append((id_text, codename_text, equip_text))
        return red_team_data

    def get_green_team_data(self):
        green_team_data = []
        for row in self.green_entries:
            id_text = row[0].text().strip()
            codename_text = row[1].text().strip()
            equip_text = row[2].text().strip()
            if id_text and codename_text and equip_text:
                green_team_data.append((id_text, codename_text, equip_text))
        return green_team_data

    def on_id_enter(self, row_data, team, index):
        id_text = row_data[0].text().strip()
        index_labels = self.red_index_labels if team == "RED" else self.green_index_labels
        background = RED_TEAM_BACKGROUND if team == "RED" else GREEN_TEAM_BACKGROUND

        if not id_text:
            index_labels[index].setText("")
            row_data[1].clear()
            row_data[1].setReadOnly(True)
            row_data[1].setPlaceholderText("")
            row_data[1].setStyleSheet(background)
            return

        try:
            id_val = int(id_text)
        except ValueError:
            print(f"Error: id must be integer: {id_text}")
            return

        if id_text in self._all_entered_player_ids(exclude_row_data=row_data):
            msg = QMessageBox(self)
            msg.setStyleSheet(COOL_FONT)
            msg.setWindowTitle("Uh oh...")
            msg.setText("This player ID is already in the game. Each player can only appear once.")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()
            row_data[0].setStyleSheet(f"{background}; border: 1px solid red;")
            row_data[0].clear()
            return

        row_data[0].setStyleSheet(background)
        index_labels[index].setText(f"Player #{index+1}")
        codename = False if isDevMode() else self.db._query_codename(id_val)

        if codename:
            row_data[1].setText(codename)
            row_data[1].setReadOnly(False)
            row_data[1].setStyleSheet(background)
            row_data[1].setPlaceholderText("")
            row_data[2].setReadOnly(False)
            row_data[2].setFocus()
        else:
            row_data[1].clear()
            row_data[1].setReadOnly(False)
            row_data[1].setPlaceholderText("Enter codename for new player")
            row_data[1].setStyleSheet(f"{background}; color: gray;")
            row_data[1].setFocus()

    def on_id_keypress(self, event, row_data, team, index):
        if event.key() == Qt.Key.Key_Delete:
            id_text = row_data[0].text().strip()
            if not id_text:
                return
            is_registered = self.db._is_registered()
            success = self.db._delete_player(id_text)
            if success:
                background = RED_TEAM_BACKGROUND if team == "RED" else GREEN_TEAM_BACKGROUND
                row_data[0].clear()
                row_data[0].setStyleSheet(background)
                row_data[1].clear()
                row_data[1].setReadOnly(True)
                row_data[1].setPlaceholderText("Successfully deleted player")
                row_data[1].setStyleSheet(background)
                row_data[2].clear()
                row_data[2].setReadOnly(True)
                row_data[2].setStyleSheet(background)
                index_labels = self.red_index_labels if team=="RED" else self.green_index_labels
                index_labels[index].setText("")
            else:
                print("Failed deleting the player from database")

        QLineEdit.keyPressEvent(row_data[0], event)

    def on_codename_enter(self, row_data, team, index):
        if row_data[1].isReadOnly():
            return

        id_text = row_data[0].text().strip()
        codename = row_data[1].text().strip()
        if not id_text or not codename:
            row_data[2].setReadOnly(True)
            return

        try:
            id_val = int(id_text)
        except ValueError:
            return

        background = RED_TEAM_BACKGROUND if team == "RED" else GREEN_TEAM_BACKGROUND

        if isDevMode():
            row_data[2].setReadOnly(False)
            row_data[1].setStyleSheet(background)
            row_data[2].setFocus()
            return

        result = self.db._update_codename(id_val, codename)

        if result == NEW_CODENAME_ADDED:
            row_data[2].setReadOnly(False)
            row_data[1].setStyleSheet(background)
            row_data[1].setPlaceholderText("")
            msg = QMessageBox(self)
            msg.setStyleSheet(COOL_FONT)
            msg.setWindowTitle(f"{COOL_GUY_EMOJI}")
            msg.setText("New player added to the vault!")
            msg.setIconPixmap(constants.logo_icon())
            msg.exec()
        elif result == EXISTING_CODENAME_UPDATED:
            row_data[2].setReadOnly(False)
            row_data[1].setStyleSheet(background)
            row_data[1].setPlaceholderText("")
            msg = QMessageBox(self)
            msg.setStyleSheet(COOL_FONT)
            msg.setWindowTitle(f"{COOL_GUY_EMOJI}")
            msg.setText("Codename updated successfully!")
            msg.setIconPixmap(constants.logo_icon())
            msg.exec()
        elif result == CODENAME_ALREADY_EXISTS:
            msg = QMessageBox(self)
            msg.setStyleSheet(COOL_FONT)
            msg.setWindowTitle("Uh oh...")
            msg.setText("Codename already exists for a different player. Please ask player for a different codename.")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()
            row_data[1].setStyleSheet(f"{background}; border: 1px solid red;")
            row_data[1].setFocus()
        elif result == ERROR_OCCURRED:
            msg = QMessageBox(self)
            msg.setStyleSheet(COOL_FONT)
            msg.setWindowTitle("Error")
            msg.setText("An unexpected error occurred while saving the codename. Try restarting application.")
            msg.setIcon(QMessageBox.Icon.Critical)
        elif result == CODENAME_CHANGE_ATTEMPT_MATCHES_EXISTING:
            msg = QMessageBox(self)
            msg.setStyleSheet(COOL_FONT)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Doh!")
            msg.setText("No codename change detected.")
            msg.exec()
        else:
            msg = QMessageBox(self)
            msg.setStyleSheet(COOL_FONT)
            msg.setWindowTitle("Error")
            msg.setText("A really unexpected error occurred. Try calling IT.")
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()

        if index < MAX_NUM_PLAYER_MINUSONE:
            this_row = self.red_entries[index] if team == "RED" else self.green_entries[index]
            this_row[2].setFocus()

    def on_row_submit(self, row_data, team, index):
        id_text = row_data[0].text().strip()
        equip_text = row_data[2].text().strip()
        background = RED_TEAM_BACKGROUND if team == "RED" else GREEN_TEAM_BACKGROUND

        try:
            equip_id = int(equip_text)
        except ValueError:
            row_data[2].setStyleSheet(f"{background}; border: 1px solid red;")
            return

        if (team == "RED" and equip_id % 2 == 0) or (team == "GREEN" and equip_id % 2 == 1):
            row_data[2].setStyleSheet(f"{background}; border: 1px solid red;")
            msg = QMessageBox(self)
            msg.setStyleSheet(COOL_FONT)
            msg.setWindowTitle("Uh oh...")
            if team == "RED":
                msg.setText("Red team must have odd numbered equipment.")
            else:
                msg.setText("Green team must have even numbered equipment.")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()
            return

        if equip_text in self._all_entered_equipment_ids(exclude_row_data=row_data):
            row_data[2].setStyleSheet(f"{background}; border: 1px solid red;")
            msg = QMessageBox(self)
            msg.setStyleSheet(COOL_FONT)
            msg.setWindowTitle("Uh oh...")
            msg.setText("This equipment ID is already assigned to another player.")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()
            return

        if not id_text or not equip_text:
            print(f"[{team}] ERROR: Both fields are required for this row.")
            if not id_text:
                row_data[0].setStyleSheet(f"{background}; border: 1px solid red;")
            if not equip_text:
                row_data[2].setStyleSheet(f"{background}; border: 1px solid red;")
            return

        if not isDevMode() and self.db._queue_player(id_text, 0 if team == "RED" else 1, equip_id):
            print(f"[{team}] SUCCESS - Player: {id_text}, Equipment: {equip_id}, Player Index: {index}")

        row_data[2].setStyleSheet(background)
        self.udp.broadcast_equipment_id(equip_id)
        if index < MAX_NUM_PLAYER_MINUSONE:
            next_row = self.red_entries[index+1] if team == "RED" else self.green_entries[index+1]
            next_row[0].setFocus()

    def clear_all_grids(self):
        confirmation_message = QMessageBox(self)
        confirmation_message.setWindowTitle("Confirm Reset")
        confirmation_message.setText("Are you ready for a New Game?")
        confirmation_message.setIcon(QMessageBox.Icon.Question)
        confirmation_message.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        confirmation_result = confirmation_message.exec()
        if confirmation_result == QMessageBox.StandardButton.No:
            return
        else:
            for i in range(MAX_NUM_PLAYER):
                self.red_index_labels[i].setText("")
                self.green_index_labels[i].setText("")
                for entry in self.red_entries[i]:
                    entry.clear()
                    entry.setReadOnly(entry != self.red_entries[i][0])
                    entry.setStyleSheet(RED_TEAM_BACKGROUND)
                    entry.setPlaceholderText("")
                for entry in self.green_entries[i]:
                    entry.clear()
                    entry.setReadOnly(entry != self.green_entries[i][0])
                    entry.setStyleSheet(GREEN_TEAM_BACKGROUND)
                    entry.setPlaceholderText("")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F11:
            if self.windowState() & Qt.WindowState.WindowFullScreen:
                self.showNormal()
            else:
                self.showFullScreen()
                QTimer.singleShot(400, lambda: self._hint.show_hint("Press Esc to exit Fullscreen"))
        elif event.key() == Qt.Key.Key_Escape:
            if self.windowState() & Qt.WindowState.WindowFullScreen:
                self.showNormal()
        elif event.key() == Qt.Key.Key_F12:
            self.clear_all_grids()
        elif event.key() == Qt.Key.Key_F5:
            self.play_action_window.show()
        else:
            super().keyPressEvent(event)

    def show_play_action_window(self):
        self.play_action_window.refresh_players()
        self.play_action_window.show()

class PlayActionWindow(QMainWindow):
    def __init__(self, main_window, udp_server:UDPServer, model:Model):
        super().__init__()
        self.main_window = main_window
        self.udp = udp_server
        self.model = model

        self.sound = SoundManager()
        self.start_track_played = False
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("PHOTON: Play Action")

        screen = QGuiApplication.primaryScreen().availableGeometry()
        window_width = screen.width() * ASPECT_RATIO
        window_height = screen.height() * ASPECT_RATIO
        x = (screen.width() - window_width) // 2
        y = (screen.height() - window_height) // 2
        self._default_w = int(window_width)
        self._default_h = int(window_height)
        self.setGeometry(int(x), int(y), self._default_w, self._default_h)
        self.setMinimumSize(480, 320)

        central_widget = QWidget()
        central_widget.setObjectName("PlayActionCentralWidget")
        central_widget.setStyleSheet(f"""
            #PlayActionCentralWidget {{
                border-image: url('{BLURRED_LOGO}');
                background-position: center;
            }}
        """)
        self.setCentralWidget(central_widget)
        self._hint = HintOverlay(self.centralWidget())

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        left_column = QVBoxLayout()
        left_column.setContentsMargins(0, 0, 0, 0)
        left_column.setSpacing(15)

        # --- Red panel ---
        self.red_panel = RedTeamPanel()
        self.red_panel.setLayout(QVBoxLayout())
        red_layout = self.red_panel.layout()
        red_layout.setContentsMargins(15, 15, 15, 15)
        red_layout.setSpacing(8)

        self.red_label = QLabel("RED TEAM")
        self.red_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.red_label.setStyleSheet(STYLE_TEAM_LABEL_PLAY_RED)
        self.red_label.setGraphicsEffect(_team_glow())
        red_layout.addWidget(self.red_label)

        self.red_team_score_label = QLabel()
        self.red_team_score_label.setTextFormat(Qt.TextFormat.RichText)
        self.red_team_score_label.setText(_team_score_html(0))
        self.red_team_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.red_team_score_label.setStyleSheet(STYLE_TEAM_SCORE_LABEL_RED)
        self.red_team_score_label.setGraphicsEffect(_team_glow())
        red_layout.addWidget(self.red_team_score_label)

        # Red column headers (permanent, above the player rows)
        red_header_grid = QGridLayout()
        red_header_grid.setHorizontalSpacing(10)
        red_header_grid.setVerticalSpacing(0)
        for col, text in enumerate(["Codename", "Score"]):
            lbl = QLabel(text)
            lbl.setStyleSheet(STYLE_GRID_HEADER)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            red_header_grid.addWidget(lbl, 0, col)
        red_layout.addLayout(red_header_grid)

        self.red_grid = QGridLayout()
        self.red_grid.setHorizontalSpacing(10)
        self.red_grid.setVerticalSpacing(4)
        red_layout.addLayout(self.red_grid, 1)

        # --- Green panel ---
        self.green_panel = GreenTeamPanel()
        self.green_panel.setLayout(QVBoxLayout())
        green_layout = self.green_panel.layout()
        green_layout.setContentsMargins(15, 15, 15, 15)
        green_layout.setSpacing(8)

        self.green_label = QLabel("GREEN TEAM")
        self.green_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.green_label.setStyleSheet(STYLE_TEAM_LABEL_PLAY_GREEN)
        self.green_label.setGraphicsEffect(_team_glow())
        green_layout.addWidget(self.green_label)

        self.green_team_score_label = QLabel()
        self.green_team_score_label.setTextFormat(Qt.TextFormat.RichText)
        self.green_team_score_label.setText(_team_score_html(0))
        self.green_team_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.green_team_score_label.setStyleSheet(STYLE_TEAM_SCORE_LABEL_GREEN)
        self.green_team_score_label.setGraphicsEffect(_team_glow())
        green_layout.addWidget(self.green_team_score_label)

        # Green column headers (permanent, above the player rows)
        green_header_grid = QGridLayout()
        green_header_grid.setHorizontalSpacing(10)
        green_header_grid.setVerticalSpacing(0)
        for col, text in enumerate(["Codename", "Score"]):
            lbl = QLabel(text)
            lbl.setStyleSheet(STYLE_GRID_HEADER)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            green_header_grid.addWidget(lbl, 0, col)
        green_layout.addLayout(green_header_grid)

        self.green_grid = QGridLayout()
        self.green_grid.setHorizontalSpacing(10)
        self.green_grid.setVerticalSpacing(4)
        green_layout.addLayout(self.green_grid, 1)

        # Hit feed container
        hit_feed_container = QWidget()
        hit_feed_container.setObjectName("HitFeedContainer")
        hit_feed_container.setStyleSheet(f"#HitFeedContainer {{ {STYLE_SEMI_TRANSPARENT_CONTAINER} }}")
        hit_feed_layout = QVBoxLayout(hit_feed_container)
        hit_feed_layout.setContentsMargins(10, 10, 10, 10)

        hit_feed_label = QLabel("Current Game Action")
        hit_feed_label.setStyleSheet(STYLE_SECTION_LABEL)
        hit_feed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hit_feed_layout.addWidget(hit_feed_label)

        self.hit_list = QListWidget()
        self.hit_list.setStyleSheet(STYLE_HIT_FEED_LIST)
        self.hit_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.hit_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        hit_feed_layout.addWidget(self.hit_list)

        # Timer container
        self.timer_container = QWidget()
        self.timer_container.setObjectName("TimerContainer")
        self.timer_container.setStyleSheet(f"#TimerContainer {{ {STYLE_SEMI_TRANSPARENT_CONTAINER} }}")
        timer_layout = QVBoxLayout(self.timer_container)
        timer_layout.setContentsMargins(10, 10, 10, 12)
        timer_layout.setSpacing(4)

        # Stretch pushes text/timer to the bottom, logo floats at top
        timer_layout.addStretch(1)
        timer_layout.addSpacing(-16)

        self.phase_label = QLabel("Players get ready!")
        self.phase_label.setStyleSheet(STYLE_PHASE_LABEL_WHITE)
        self.phase_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.phase_label.setWordWrap(True)
        self.phase_label.setMinimumWidth(0)
        self.phase_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        timer_layout.addWidget(self.phase_label)

        self.time_display = QLabel("0:00")
        self.time_display.setStyleSheet(STYLE_TIMER_DISPLAY)
        self.time_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_layout.addWidget(self.time_display)

        self.end_hint_label = QLabel("Press any key to close scoreboard")
        self.end_hint_label.setStyleSheet(STYLE_SECTION_LABEL)
        self.end_hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.end_hint_label.setWordWrap(True)
        self.end_hint_label.setVisible(False)
        timer_layout.addWidget(self.end_hint_label)

        # Floating Photon logo pinned to top of timer container
        self.photon_logo_label = QLabel(self.timer_container)
        self.photon_logo_label.setObjectName("PhotonLogoOverlay")
        self.photon_logo_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.photon_logo_label.setStyleSheet("background: transparent; border: none;")
        self._load_photon_logo()

        left_column.addWidget(hit_feed_container, 6)
        left_column.addWidget(self.timer_container, 5)

        main_layout.addLayout(left_column, 1)
        main_layout.addWidget(self.red_panel, 2)
        main_layout.addWidget(self.green_panel, 2)

        # Data structures for score updates
        self.score_labels = {}
        self.player_scores = {}
        self.icon_labels = {}
        self.red_row_list = []
        self.green_row_list = []
        self._score_glow_timers = {}
        self.red_team_score = 0
        self.green_team_score = 0
        self.flash_visible = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.remaining_seconds = 0
        self.timer_state = "ready"

        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self._toggle_flash)

        self._phase_glow_tick = 0
        self._phase_glow_effect = QGraphicsDropShadowEffect()
        self._phase_glow_effect.setColor(QColor(*PHASE_GLOW_COLOR))
        self._phase_glow_effect.setOffset(0, 0)
        self._phase_glow_effect.setBlurRadius(PHASE_GLOW_BLUR_MIN)
        self.phase_label.setGraphicsEffect(self._phase_glow_effect)
        self.phase_glow_timer = QTimer()
        self.phase_glow_timer.timeout.connect(self._tick_phase_glow)

        self._move_restore_timer = QTimer(self)
        self._move_restore_timer.setSingleShot(True)
        self._move_restore_timer.timeout.connect(self._restore_glow)

    def _restore_glow(self):
        self.setUpdatesEnabled(True)
        if self.isVisible():
            self.phase_glow_timer.start(PHASE_GLOW_TICK_MS)

    def moveEvent(self, event):
        super().moveEvent(event)
        self.phase_glow_timer.stop()
        for t, c in list(self._score_glow_timers.values()):
            c[0] = True
            t.stop()
        self._score_glow_timers.clear()
        self.setUpdatesEnabled(False)
        self._move_restore_timer.start(200)

    def _load_photon_logo(self):
        # Try float-logo.png first, fall back to logo.jpg
        logo_path = IMAGES_DIR / "float-logo.png"
        if not logo_path.exists():
            logo_path = IMAGES_DIR / "logo.jpg"
        pixmap = QPixmap(str(logo_path))
        if pixmap.isNull():
            self.photon_logo_label.hide()
            return
        # Crop bottom 28% to remove the "Ultimate Game on Planet Earth" banner
        crop_h = int(pixmap.height() * 0.72)
        pixmap = pixmap.copy(0, 0, pixmap.width(), crop_h)
        # Make white/near-white pixels transparent via raw bytearray (BGRA byte order)
        image = pixmap.toImage().convertToFormat(QImage.Format.Format_ARGB32)
        ptr = image.bits()
        ptr.setsize(image.sizeInBytes())
        ba = bytearray(ptr)
        for i in range(0, len(ba), 4):
            if ba[i + 2] > 215 and ba[i + 1] > 215 and ba[i] > 215:
                ba[i + 3] = 0
        image = QImage(bytes(ba), image.width(), image.height(), QImage.Format.Format_ARGB32)
        self._photon_logo_pixmap = QPixmap.fromImage(image)
        self._reposition_logo()

    def _reposition_logo(self):
        if not hasattr(self, '_photon_logo_pixmap') or self._photon_logo_pixmap.isNull():
            return
        container = self.timer_container
        phase_y = self.phase_label.mapTo(container, QPoint(0, 0)).y()
        if phase_y <= 0:
            phase_y = int(container.height() * (1 - LOGO_MAX_HEIGHT_RATIO))
        # logo bottom sits at the midpoint between container top and phase_label top
        logo_bottom = phase_y // 2
        available_h = max(1, logo_bottom)
        max_w = max(1, container.width() - 20)
        if max_w <= 0 or available_h <= 0:
            return
        scaled = self._photon_logo_pixmap.scaled(
            max_w, available_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.photon_logo_label.setPixmap(scaled)
        self.photon_logo_label.resize(scaled.size())
        x = (container.width() - scaled.width()) // 2 + 2
        y = logo_bottom - scaled.height()
        self.photon_logo_label.move(x, max(0, y))
        self.photon_logo_label.raise_()

    def _set_phase_style(self, style, glow_color):
        self.phase_label.setStyleSheet(style)
        self._phase_glow_effect.setColor(QColor(*glow_color))

    def _resize_hit_items(self):
        count = self.hit_list.count()
        if count == 0:
            return
        vh = self.hit_list.viewport().height()
        item_h = max(1, vh // HIT_FEED_MAX_ITEMS)
        for i in range(count):
            self.hit_list.item(i).setSizeHint(QSize(0, item_h))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self._reposition_logo)
        QTimer.singleShot(0, self._resize_hit_items)
        self._hint.reposition()

    def add_hit(self, text):
        item = QListWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        self.hit_list.addItem(item)
        while self.hit_list.count() > HIT_FEED_MAX_ITEMS:
            self.hit_list.takeItem(0)
        self._resize_hit_items()
        self.hit_list.setCurrentRow(self.hit_list.count() - 1)
        self.hit_list.scrollToBottom()

    def start_countdown(self):
        self.timer_state = "ready"
        self.phase_label.setText("Players get ready!")
        self._set_phase_style(STYLE_PHASE_LABEL_WHITE, PHASE_GLOW_COLOR_WHITE)
        self.end_hint_label.setVisible(False)
        self.remaining_seconds = DEV_COUNTDOWN_READY_SECONDS if isDevMode() else COUNTDOWN_READY_SECONDS
        self.start_track_played = False
        self.update_timer_display()
        self.timer.start(TIMER_INTERVAL_MS)
        self.flash_timer.start(FLASH_INTERVAL_MS)

    def start_game(self):
        self.udp.announce_game_start()
        self.udp.start_readloop()

    def update(self):
        self.update_countdown()
        self.update_leaderboard()

    def update_leaderboard(self):
        print("[Window] update_leaderboard called")
        print(f"[Window] messageq size: {len(self.model.messageq)}")
        print(f"[Window] scorediffq size: {len(self.model.scorediffq)}")
        print("updating leaderboard...")

        while(equip_id := self.model.pop_based_equip_id()) is not False:
            self.grant_baseicon(equip_id)

        while(message := self.model.pop_live_message()) is not False:
            self.add_hit(message)

        while(res := self.model.pop_score_diff()) is not False:
            equip_id, diff = res
            self.reflect_score_change(equip_id, diff)

    def update_countdown(self):
        self.remaining_seconds -= 1
        self.update_timer_display()

        if self.timer_state == "ready" and self.remaining_seconds == MUSIC_START_THRESHOLD and not self.start_track_played:
            self.sound.play_random_start_track()
            self.start_track_played = True

        if self.remaining_seconds <= 0:
            if self.timer_state == "ready":
                self.start_game()
                self.timer_state = "game"
                self.phase_label.setText("Game on!")
                self._set_phase_style(STYLE_PHASE_LABEL, PHASE_GLOW_COLOR)
                self.remaining_seconds = DEV_GAME_DURATION_SECONDS if isDevMode() else GAME_DURATION_SECONDS
                self.update_timer_display()
            elif self.timer_state == "game":
                self.timer.stop()
                self.flash_timer.stop()
                self._reset_flash()
                self.timer_state = "game_over"
                self.phase_label.setText("Game Over")
                self._set_phase_style(STYLE_PHASE_LABEL_RED, PHASE_GLOW_COLOR_RED)
                self.time_display.setText("0:00")
                self.end_hint_label.setVisible(True)
                self.udp.announce_game_end()
                self.grabKeyboard()
            else:
                self.timer.stop()

    def update_timer_display(self):
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        self.time_display.setText(f"{minutes}:{seconds:02d}")

    def showEvent(self, event):
        self.phase_glow_timer.start(PHASE_GLOW_TICK_MS)
        self.refresh_players()
        self.start_countdown()
        super().showEvent(event)
        QTimer.singleShot(800, lambda: self._hint.show_hint("Press F11 for Fullscreen"))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F11:
            if self.windowState() & Qt.WindowState.WindowFullScreen:
                self.showNormal()
            else:
                self.showFullScreen()
                QTimer.singleShot(400, lambda: self._hint.show_hint("Press Esc to exit Fullscreen"))
            return
        if event.key() == Qt.Key.Key_Escape:
            if self.windowState() & Qt.WindowState.WindowFullScreen:
                self.showNormal()
                return
        if self.timer_state == "game_over":
            self.releaseKeyboard()
            self.close()

    def closeEvent(self, event):
        self.releaseKeyboard()
        self.timer.stop()
        self.flash_timer.stop()
        self.phase_glow_timer.stop()
        for t, c in self._score_glow_timers.values():
            c[0] = True
            t.stop()
        self._score_glow_timers.clear()
        self.sound.stop()
        print(f"[closeEvent] timer_state={self.timer_state}")
        if self.timer_state == "game":
            self.udp.announce_game_end()
        self.hit_list.clear()
        if self.timer_state in ("game_over", "game"):
            self.main_window.show()
            self.main_window.raise_()
        super().closeEvent(event)

    def close_play_action_window(self):
        self.flash_timer.stop()
        self.sound.stop()
        self.hit_list.clear()
        self.hide()

    def refresh_players(self):
        for t, c in self._score_glow_timers.values():
            c[0] = True
            t.stop()
        self._score_glow_timers.clear()
        self._clear_grid(self.red_grid)
        self._clear_grid(self.green_grid)
        for i in range(MAX_NUM_PLAYER):
            self.red_grid.setRowStretch(i, 0)
            self.green_grid.setRowStretch(i, 0)
        self.score_labels.clear()
        self.player_scores.clear()
        self.icon_labels.clear()
        self.red_row_list.clear()
        self.green_row_list.clear()
        self.model.equip_to_team.clear()

        red_data = self.main_window.get_red_team_data()
        for row, (player_id, codename, equip_id) in enumerate(red_data, start=0):
            name_cell, score_label, name_label = self._add_player_row(self.red_grid, row, player_id, codename, equip_id, "red")
            self.red_row_list.append({'equip_id': int(equip_id), 'name_cell': name_cell, 'score_label': score_label, 'name_label': name_label})
            self.model.equip_to_codename[int(equip_id)] = codename
            self.model.equip_to_team[int(equip_id)] = Model.RED

        green_data = self.main_window.get_green_team_data()
        for row, (player_id, codename, equip_id) in enumerate(green_data, start=0):
            name_cell, score_label, name_label = self._add_player_row(self.green_grid, row, player_id, codename, equip_id, "green")
            self.green_row_list.append({'equip_id': int(equip_id), 'name_cell': name_cell, 'score_label': score_label, 'name_label': name_label})
            self.model.equip_to_codename[int(equip_id)] = codename
            self.model.equip_to_team[int(equip_id)] = Model.GREEN

    def _clear_grid(self, grid):
        while grid.count():
            item = grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _add_player_row(self, grid, row, _player_id, codename, equip_id, team):
        alt = row % 2 == 0
        player_style = STYLE_PLAYER_LABEL_ALT if alt else STYLE_PLAYER_LABEL
        score_style = STYLE_SCORE_LABEL_ALT if alt else STYLE_SCORE_LABEL

        def _neon_glow(color=PLAYER_LABEL_GLOW_COLOR):
            fx = QGraphicsDropShadowEffect()
            fx.setBlurRadius(PLAYER_LABEL_GLOW_BLUR)
            fx.setOffset(*PLAYER_LABEL_SHADOW_OFFSET)
            fx.setColor(QColor(*color))
            return fx

        name_cell = QWidget()
        name_hbox = QHBoxLayout(name_cell)
        name_hbox.setContentsMargins(2, 1, 2, 1)
        name_hbox.setSpacing(4)

        icon = QLabel()
        icon.setFixedWidth(BASEICON_SIZE)
        icon.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        name_hbox.addWidget(icon)

        name_glow_color = PLAYER_LABEL_GLOW_COLOR_RED if team == "red" else PLAYER_LABEL_GLOW_COLOR_GREEN
        name_label = QLabel(codename)
        name_label.setStyleSheet(player_style)
        name_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        name_label.setGraphicsEffect(_neon_glow(name_glow_color))
        name_hbox.addWidget(name_label, 1)

        _expand = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        name_cell.setSizePolicy(_expand)
        grid.addWidget(name_cell, row, 0)

        score_label = QLabel("0")
        score_label.setStyleSheet(score_style)
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_label.setSizePolicy(_expand)
        grid.addWidget(score_label, row, 1)
        grid.setRowStretch(row, 1)

        equip_id_int = int(equip_id)
        self.score_labels[equip_id_int] = (team, score_label)
        self.player_scores[equip_id_int] = 0
        self.icon_labels[equip_id_int] = icon
        return name_cell, score_label, name_label

    def grant_baseicon(self, equip_id):
        if equip_id not in self.icon_labels:
            print(f"Warning: baseicon request received for unknown equipment ID {equip_id}")
            return
        label = self.icon_labels[equip_id]
        pixmap = QPixmap(str(IMAGES_DIR / "baseicon.jpg"))
        if pixmap.isNull():
            label.clear()
            return
        scaled = pixmap.scaled(
            BASEICON_SIZE,
            BASEICON_SIZE,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        label.setPixmap(scaled)
        print(f"baseicon is now reflected to {equip_id}")

    def _resort_grid(self, grid, row_list):
        row_list.sort(key=lambda r: self.player_scores.get(r['equip_id'], 0), reverse=True)
        for r in row_list:
            grid.removeWidget(r['name_cell'])
            grid.removeWidget(r['score_label'])
        for new_row, r in enumerate(row_list):
            alt = new_row % 2 == 0
            r['name_label'].setStyleSheet(STYLE_PLAYER_LABEL_ALT if alt else STYLE_PLAYER_LABEL)
            r['score_label'].setStyleSheet(STYLE_SCORE_LABEL_ALT if alt else STYLE_SCORE_LABEL)
            grid.addWidget(r['name_cell'], new_row, 0)
            grid.addWidget(r['score_label'], new_row, 1)

    def _start_score_glow(self, equip_id):
        if equip_id in self._score_glow_timers:
            old_timer, old_cancelled = self._score_glow_timers.pop(equip_id)
            old_cancelled[0] = True
            old_timer.stop()
        if equip_id not in self.score_labels:
            return
        _, label = self.score_labels[equip_id]

        effect = QGraphicsDropShadowEffect()
        effect.setColor(QColor(*SCORE_GLOW_COLOR))
        effect.setOffset(0, 0)
        effect.setBlurRadius(SCORE_GLOW_BLUR_MAX)
        label.setGraphicsEffect(effect)

        ticks_total = SCORE_GLOW_DURATION_MS // SCORE_GLOW_TICK_MS
        cycle_len = max(1, ticks_total // SCORE_GLOW_CYCLES)
        half_cycle = max(1, cycle_len // 2)
        tick = [0]
        cancelled = [False]

        def _tick():
            if cancelled[0]:
                return
            tick[0] += 1
            if tick[0] >= ticks_total:
                timer.stop()
                label.setGraphicsEffect(None)
                self._score_glow_timers.pop(equip_id, None)
                return
            pos = tick[0] % cycle_len
            t = pos / half_cycle if pos < half_cycle else (cycle_len - pos) / half_cycle
            effect.setBlurRadius(int(SCORE_GLOW_BLUR_MIN + t * (SCORE_GLOW_BLUR_MAX - SCORE_GLOW_BLUR_MIN)))

        timer = QTimer()
        timer.timeout.connect(_tick)
        timer.start(SCORE_GLOW_TICK_MS)
        self._score_glow_timers[equip_id] = (timer, cancelled)

    def reflect_score_change(self, equip_id, diff):
        if equip_id not in self.score_labels:
            print(f"Warning: Score received for unknown equipment ID {equip_id}")
            return

        team, label = self.score_labels[equip_id]
        self.player_scores[equip_id] += diff
        label.setText(str(self.player_scores[equip_id]))
        self._update_team_scores()
        self._start_score_glow(equip_id)
        row_list = self.red_row_list if team == "red" else self.green_row_list
        self._resort_grid(self.red_grid if team == "red" else self.green_grid, row_list)

    def reset_scores(self):
        for equip_id in self.player_scores:
            self.player_scores[equip_id] = 0
            if equip_id in self.score_labels:
                self.score_labels[equip_id][1].setText("0")
        self.red_team_score = 0
        self.green_team_score = 0
        self.red_team_score_label.setText(_team_score_html(0))
        self.green_team_score_label.setText(_team_score_html(0))

    def _update_team_scores(self):
        red_total = sum(
            score for equip_id, score in self.player_scores.items()
            if self.score_labels.get(equip_id, (None,))[0] == "red"
        )
        green_total = sum(
            score for equip_id, score in self.player_scores.items()
            if self.score_labels.get(equip_id, (None,))[0] == "green"
        )
        self.red_team_score = red_total
        self.green_team_score = green_total
        self.red_team_score_label.setText(_team_score_html(red_total))
        self.green_team_score_label.setText(_team_score_html(green_total))

    def _reset_flash(self):
        self.red_team_score_label.setStyleSheet(STYLE_TEAM_SCORE_LABEL_RED)
        self.green_team_score_label.setStyleSheet(STYLE_TEAM_SCORE_LABEL_GREEN)

    def _toggle_flash(self):
        if self.timer_state != "game" or self.red_team_score == self.green_team_score:
            self._reset_flash()
            return

        self.flash_visible = not self.flash_visible
        leading_red = self.red_team_score > self.green_team_score

        red_style = STYLE_TEAM_SCORE_LABEL_FLASH_RED if (leading_red and self.flash_visible) else STYLE_TEAM_SCORE_LABEL_RED
        green_style = STYLE_TEAM_SCORE_LABEL_FLASH_GREEN if (not leading_red and self.flash_visible) else STYLE_TEAM_SCORE_LABEL_GREEN

        self.red_team_score_label.setStyleSheet(red_style)
        self.green_team_score_label.setStyleSheet(green_style)

    def _tick_phase_glow(self):
        if not self.updatesEnabled() or not self.isVisible():
            return
        cycle_ticks = max(1, PHASE_GLOW_CYCLE_MS // PHASE_GLOW_TICK_MS)
        self._phase_glow_tick = (self._phase_glow_tick + 1) % cycle_ticks
        half = max(1, cycle_ticks // 2)
        pos = self._phase_glow_tick
        t = pos / half if pos < half else (cycle_ticks - pos) / half
        blur = int(PHASE_GLOW_BLUR_MIN + t * (PHASE_GLOW_BLUR_MAX - PHASE_GLOW_BLUR_MIN))
        self._phase_glow_effect.setBlurRadius(blur)

def _safe_rounded_rect(painter, rect, radius):
    r = min(radius, rect.width() // 2, rect.height() // 2)
    path = QPainterPath()
    if r > 0:
        path.addRoundedRect(float(rect.x()), float(rect.y()),
                            float(rect.width()), float(rect.height()), float(r), float(r))
    else:
        path.addRect(float(rect.x()), float(rect.y()),
                     float(rect.width()), float(rect.height()))
    painter.drawPath(path)

class RedTeamPanel(QWidget):
    def paintEvent(self, event):
        r = self.rect()
        if r.width() < 1 or r.height() < 1:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(*COLOR_PANEL_BG_RED)))
        _safe_rounded_rect(painter, r, PANEL_BORDER_RADIUS)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        for pen_width, alpha in PANEL_GLOW_LAYERS:
            inset = pen_width // 2
            adjusted = r.adjusted(inset, inset, -inset, -inset)
            if adjusted.width() < 1 or adjusted.height() < 1:
                continue
            pen = QPen(QColor(*COLOR_PANEL_GLOW_RED, alpha))
            pen.setWidth(pen_width)
            painter.setPen(pen)
            _safe_rounded_rect(painter, adjusted, PANEL_BORDER_RADIUS)

        cs = PANEL_CORNER_MARK_SIZE
        cr = PANEL_BORDER_RADIUS
        w, h = r.width() - 1, r.height() - 1
        corner_pen = QPen(QColor(*COLOR_CORNER_MARK_RED, 255))
        corner_pen.setWidth(PANEL_CORNER_MARK_WIDTH)
        painter.setPen(corner_pen)
        painter.drawLine(cr, 1, cr + cs, 1)
        painter.drawLine(1, cr, 1, cr + cs)
        painter.drawLine(w - cr, 1, w - cr - cs, 1)
        painter.drawLine(w - 1, cr, w - 1, cr + cs)
        painter.drawLine(cr, h - 1, cr + cs, h - 1)
        painter.drawLine(1, h - cr, 1, h - cr - cs)
        painter.drawLine(w - cr, h - 1, w - cr - cs, h - 1)
        painter.drawLine(w - 1, h - cr, w - 1, h - cr - cs)

class GreenTeamPanel(QWidget):
    def paintEvent(self, event):
        r = self.rect()
        if r.width() < 1 or r.height() < 1:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(*COLOR_PANEL_BG_GREEN)))
        _safe_rounded_rect(painter, r, PANEL_BORDER_RADIUS)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        for pen_width, alpha in PANEL_GLOW_LAYERS:
            inset = pen_width // 2
            adjusted = r.adjusted(inset, inset, -inset, -inset)
            if adjusted.width() < 1 or adjusted.height() < 1:
                continue
            pen = QPen(QColor(*COLOR_PANEL_GLOW_GREEN, alpha))
            pen.setWidth(pen_width)
            painter.setPen(pen)
            _safe_rounded_rect(painter, adjusted, PANEL_BORDER_RADIUS)

        cs = PANEL_CORNER_MARK_SIZE
        cr = PANEL_BORDER_RADIUS
        w, h = r.width() - 1, r.height() - 1
        corner_pen = QPen(QColor(*COLOR_CORNER_MARK_GREEN, 255))
        corner_pen.setWidth(PANEL_CORNER_MARK_WIDTH)
        painter.setPen(corner_pen)
        painter.drawLine(cr, 1, cr + cs, 1)
        painter.drawLine(1, cr, 1, cr + cs)
        painter.drawLine(w - cr, 1, w - cr - cs, 1)
        painter.drawLine(w - 1, cr, w - 1, cr + cs)
        painter.drawLine(cr, h - 1, cr + cs, h - 1)
        painter.drawLine(1, h - cr, 1, h - cr - cs)
        painter.drawLine(w - cr, h - 1, w - cr - cs, h - 1)
        painter.drawLine(w - 1, h - cr, w - 1, h - cr - cs)