import sys
import json
from PyQt4 import QtCore, QtGui, uic

qtCreatorFile = "jumpdrive.ui"
playerFile = "players.json"
with open(playerFile) as json_data:
    players = json.load(json_data)
players_lst = players['players']

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.cb_p1.clear()
        self.cb_p1.addItems(players_lst)
        self.nbr_players = 1
        self.btn_add_player.clicked.connect(self.AddPlayer)
        self.btn_remove_player.clicked.connect(self.DeletePlayer)

    def _add_to_player_grid(self, players):
        p_col = players + 1
        cb = QtGui.QComboBox()
        cb.addItems(players_lst)
        cb.setObjectName("cb_p" + str(p_col))
        cb.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        self.grid_player.addWidget(cb, 0, p_col)

    def _add_to_round_grid(self, players):
        p_col = players + 1
        le = QtGui.QLineEdit()
        le.setObjectName("le_p" + str(p_col))
        le.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.grid_rounds.addWidget(le, 0, p_col)

    def _add_to_spins_grid(self, players):
        p_col = players + 1
        sb = QtGui.QSpinBox()
        sb.setObjectName("sb_p" + str(p_col))
        self.grid_spins.addWidget(sb, 0, p_col)

    def AddPlayer(self):
        self.nbr_players = self.sb_nbr_players.value()
        for i in range(1, self.nbr_players):
            self._add_to_player_grid(i)
            self._add_to_round_grid(i)
            self._add_to_spins_grid(i)

        cb_boxes = self.findChildren(QtGui.QComboBox)
        for cb in cb_boxes:
            print cb.objectName(), cb.pos()
        print self.cb_p2.value()

    def DeletePlayer(self):
        if self.nbr_players == 1:
            return
        if self.nbr_players == 2:
            while self.grid_player.count():
                item = self.grid_player.takeAt(0)
                if item.widget().objectName() == 'cb_p2':
                    item.widget().deleteLater()
            while self.grid_rounds.count():
                item = self.grid_rounds.takeAt(0)
                if item.widget().objectName() == 'le_p2':
                    item.widget().deleteLater()
            while self.grid_spins.count():
                item = self.grid_spins.takeAt(0)
                if item.widget().objectName() == 'sb_p2':
                    item.widget().deleteLater()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
