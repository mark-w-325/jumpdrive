import sys
import json
from PyQt4 import QtCore, QtGui, uic

qtCreatorFile = "jumpdrive2.ui"
playerFile = "players.json"
gameFile = "gamedata.json"

with open(playerFile) as json_data:
    players = json.load(json_data)
players_lst = players['players']

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.nbr_players = 1
        self.game_id = 1
        self.game_data = self.loadGameData()
        
        self.cb_p1.clear()
        self.cb_p1.addItems(players_lst)
        
        self.cb_p2.clear()
        self.cb_p2.addItems(players_lst)
        self.cb_p2.hide()
        
        self.cb_p3.clear()
        self.cb_p3.addItems(players_lst)
        self.cb_p3.hide()
        
        self.cb_p4.clear()
        self.cb_p4.addItems(players_lst)
        self.cb_p4.hide()
        
        self.le_p2.hide()
        self.le_p3.hide()
        self.le_p4.hide()
        self.sb_p2.hide()
        self.sb_p3.hide()
        self.sb_p4.hide()
        self.sb_card_p2.hide()
        self.sb_card_p3.hide()
        self.sb_card_p4.hide()
        
        self.btn_add_players.clicked.connect(self.AddPlayer)
        self.btn_remove_player.clicked.connect(self.DeletePlayer)
        self.btn_start_game.clicked.connect(self.StartGame)

    def _add_to_player_grid(self, players):
        if players == 1:
            return
        else:
            players += 1
            for i in range(1, players):
                if i > 1:
                    cb_name = "cb_p" + str(i)
                    le_name = "le_p" + str(i)
                    sb_vp_name = "sb_p" + str(i)
                    sb_card_name = "sb_card_p" + str(i)
                    cb_widget = self.getWidgets(cb_name)
                    le_widget = self.getWidgets(le_name)
                    sb_vp_widget = self.getWidgets(sb_vp_name)
                    sb_card_widget = self.getWidgets(sb_card_name)
                    cb_widget[-1].show()
                    le_widget[-1].show()
                    sb_vp_widget[-1].show()
                    sb_card_widget[-1].show()

    def AddPlayer(self):
        self.nbr_players = self.sb_nbr_players.value()
        if self.nbr_players == 1:
            return
        self._add_to_player_grid(self.nbr_players)
        self.nbr_players = self.player_name_grid.count()

        # cb_boxes = self.findChildren(QtGui.QComboBox)
        # for cb in cb_boxes:
            # print cb.objectName(), cb.pos()

    def DeletePlayer(self):
        if self.nbr_players == 1:
            return
        else:
            nbr_players = self.nbr_players
            cb_name = 'cb_p' + str(nbr_players)
            le_name = 'le_p' + str(nbr_players)
            sb_vp_name = 'sb_p' + str(nbr_players)
            sb_card_name = 'sb_card_p' + str(nbr_players)
            cb_widget = self.getWidgets(cb_name)
            le_widget = self.getWidgets(le_name)
            sb_vp_widget = self.getWidgets(sb_vp_name)
            sb_card_widget = self.getWidgets(sb_card_name)
            cb_widget[-1].hide()
            le_widget[-1].hide()
            sb_vp_widget[-1].hide()
            sb_card_widget[-1].hide()
            self.nbr_players -= 1
            
    def StartGame(self):
        max_game_id = int(max(self.game_data['games'], key=int))
        if max_game_id == self.game_id:
            current_game_dict = self.game_data
            print current_game_dict
            players = self.getPlayers()
            current_game_dict['games'][str(self.game_id)].update(players)
            print current_game_dict
        else:
            self.game_id = max_game_id + 1
            max_game_id = self.game_id
            pass
        pass
    
    def getWidgets(self, name, cls=False):
        widgets = []
        for widget in QtGui.QApplication.allWidgets():
            if widget.objectName() == name:
                widgets.append(widget)
        return widgets

    def getPlayers(self):
        widgets = (self.player_name_grid.itemAt(i).widget() for i in range(self.player_name_grid.count()))
        return_dict = dict.fromkeys(["players"], {})
        for w in widgets:
            if isinstance(w, QtGui.QComboBox):
                if str(w.currentText()) == "":
                    pass
                else:
                    return_dict["players"].update({str(w.objectName())[-2:]: {"player_name": str(w.currentText())}})
        return return_dict
        
    def loadGameData(self):
        with open(gameFile) as json_data:
            games = json.load(json_data)
        return games
            


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
