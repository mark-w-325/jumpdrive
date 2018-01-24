import sys
import json
from PyQt4 import QtCore, QtGui, uic
import pyqtgraph as pg
import numpy as np
import pprint

pp = pprint.PrettyPrinter(indent=4)

qtCreatorFile = "jumpdrive.ui"
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

        self.setGeometry(100, 100, 2250, 1250)
        self.setWindowTitle('Jump Drive Point Tracker')

        self.cb_p1.clear()
        self.cb_p1.addItems(players_lst)
        
        pg.setConfigOptions(antialias=True)

        self._setup_game()

        self.btn_add_players.clicked.connect(self.AddPlayer)
        self.btn_remove_player.clicked.connect(self.DeletePlayer)
        self.btn_reset.clicked.connect(self.ResetGame)
        self.btn_start_game.clicked.connect(self.StartGame)
        self.btn_add_score.clicked.connect(self.AddScore)
        self.btn_undo.clicked.connect(self.UndoScore)

    def _setup_game(self):
        # Main Game variables
        self.nbr_players = 1
        self.round = 1
        self.game_data = self.loadGameData()
        self.game_id = int(max(self.game_data['games'], key=int))
        if self.game_id >= 1 and len(self.game_data['games'][str(self.game_id)]) > 0:
            self.game_id += 1
        self.game_started = False
        self.winning_score = 50
        self.winner_vp = 0
        self.winner_name = None
        self.winner_cards = 0
        self.data_dict = dict()

        # Reset Number of Players spinbox
        self.sb_nbr_players.setValue(self.nbr_players)

        # Hide other player boxes
        self.cb_p1.clear()
        self.cb_p1.addItems(players_lst)
        self.sb_p1.setValue(0)
        self.sb_card_p1.setValue(0)

        self.cb_p2.clear()
        self.cb_p2.addItems(players_lst)
        self.cb_p2.hide()
        self.sb_p2.setValue(0)
        self.sb_card_p2.setValue(0)

        self.cb_p3.clear()
        self.cb_p3.addItems(players_lst)
        self.cb_p3.hide()
        self.sb_p3.setValue(0)
        self.sb_card_p3.setValue(0)

        self.cb_p4.clear()
        self.cb_p4.addItems(players_lst)
        self.cb_p4.hide()
        self.sb_p3.setValue(0)
        self.sb_card_p3.setValue(0)

        self.te_p1.clear()
        self.te_p2.hide()
        self.te_p2.clear()
        self.te_p3.clear()
        self.te_p3.hide()
        self.te_p4.hide()
        self.te_p4.clear()

        self.sb_p2.hide()
        self.sb_p3.hide()
        self.sb_p4.hide()

        self.sb_card_p2.hide()
        self.sb_card_p3.hide()
        self.sb_card_p4.hide()

        self.dataplot.clear()
        labelStyle = {'color': '#FFF', 'size': '24pt'}
        self.dataplot.setTitle("Victory Points Board", **labelStyle)
        try:
            self.legend.scene().removeItem(self.legend)
        except Exception as e:
            pass
    
    def _setup_plot(self):
        #self.dataplot.addLegend()
        self.legend =self.dataplot.addLegend()
        labelStyle = {'color': '#FFF', 'font-size': '24pt'}
        self.dataplot.getAxis('left').setLabel(text='Victory Points', **labelStyle)
        self.dataplot.getAxis('bottom').setLabel(text='Round', **labelStyle)
        self.dataplot.setYRange(0, 50)
        self.dataplot.setXRange(0, self.round)
        
    def _plot_data(self, undo=False):
        if undo:
            self.dataplot.setXRange(0, self.round)
        else:
            self.dataplot.setXRange(0, self.round + 1)
        for k, v in self.game_data['games'][str(self.game_id)]['players'].items():
            for k2, v2 in v['rounds'].items():
                dict_key = k + v['player_name']
                if self.round == 1:
                    self.data_dict[dict_key] = {k2: v2['round_vp_total']}
                else:
                    self.data_dict[dict_key].update({k2: v2['round_vp_total']})
        for key in sorted(self.data_dict.iterkeys()):
            points = list()
            points.append(0)
            for key2 in sorted(self.data_dict[key].iterkeys()):
                points.append(self.data_dict[key][key2])
            if undo:
                x = np.arange(0, self.round)
            else:
                x = np.arange(0, self.round + 1)
            y = np.array(points)
            if key[:2] == 'p1':
                color = 'r'
                symbol = 'o'
            elif key[:2] == 'p2':
                color = 'g'
                symbol = 's'
            elif key[:2] == 'p3':
                color = 'b'
                symbol = 'd'
            elif key[:2] == 'p4':
                color = 'y'
                symbol = 't1'
            if self.round == 1:
                self.dataplot.plot(x=x, y=y, name=key[2:], pen=color, symbol=symbol, symbolPen=color, symbolBrush=(55,55,55))
                #self.legend.addItem(self.dataplot.plot(x=x, y=y, pen=color), key[2:])
            else:
                self.dataplot.plot(x=x, y=y, pen=color, symbol=symbol, symbolPen=color, symbolBrush=(55,55,55))
        if self.round == 1:
            legendLabelStyle = {'color': '#FFF', 'size': '16pt', 'bold': True}
            for item in self.legend.items:
                for single_item in item:
                    if isinstance(single_item, pg.graphicsItems.LabelItem.LabelItem):
                        single_item.setText("\t" + single_item.text, **legendLabelStyle)
        
    def _add_to_player_grid(self, players):
        if players == 1:
            return
        else:
            players += 1
            for i in range(1, players):
                if i > 1:
                    cb_name = "cb_p" + str(i)
                    le_name = "te_p" + str(i)
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

    def DeletePlayer(self):
        if self.nbr_players == 1:
            return
        else:
            nbr_players = self.nbr_players
            cb_name = 'cb_p' + str(nbr_players)
            le_name = 'te_p' + str(nbr_players)
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
            self.sb_nbr_players.setValue(self.nbr_players)

    def StartGame(self):
        players = self.loadPlayers()
        if self.game_id == 1:
            self.game_data['games'][str(self.game_id)].update(players)
        else:
            self.game_data['games'][str(self.game_id)] = players
        self._setup_plot()
        self.game_started = True

    def AddScore(self):
        vp_dict = dict()
        if not self.game_started:
            self.StartGame()
        for i in range(1, self.nbr_players + 1):
            player = "p" + str(i)
            vp = self.getVPIncome(player)
            cards = self.getCardIncome(player)
            player_data = self.update_player(self.game_data['games'][str(self.game_id)]['players'], player, self.round, rnd_vp=vp, rnd_cards=cards)
            self.game_data['games'][str(self.game_id)]['players'] = player_data[0]
            vp_dict[player] = player_data[1]
        self._update_line_edits()
        self._who_is_winning(vp_dict)
        self._plot_data()
        if self.winner_vp >= self.winning_score:
            self.EndGame()
        else:
            self.round += 1

    def UndoScore(self):
        round = self.round - 1
        for i in range(1, self.nbr_players + 1):
            player = "p" + str(i)
            self.game_data['games'][str(self.game_id)]['players'][player]['rounds'].pop(str(round), None)
        for k, v in self.data_dict.items():
            v.pop(str(round), None)
        self._update_line_edits(True)
        self.winner_vp = 0
        self.winner_name = None
        self.winner_cards = 0
        self.round = round
        self.dataplot.clear()
        self._plot_data(undo=True)

    def ResetGame(self):
        reset_widget = QtGui.QWidget()
        reset_result = QtGui.QMessageBox.question(reset_widget, 'Reset Game', "Do you want to reset?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reset_result == QtGui.QMessageBox.Yes:
            self.game_data['games'].pop(str(self.game_id), None)
            self._setup_game()

    def EndGame(self):
        self.game_data['games'][str(self.game_id)]["winner"] = self.winner_name
        self.game_data['games'][str(self.game_id)]["winner_score"] = self.winner_vp
        self.game_data['games'][str(self.game_id)]["rounds"] = self.round
        with open(gameFile, 'w') as fp:
                json.dump(self.game_data, fp, indent=4)
        msg_box_str = 'The winner is %s with %i victory points and %i card income. Would you like to start another game?' % (self.winner_name, self.winner_vp, self.winner_cards)
        winner_widget = QtGui.QWidget()
        winner_result = QtGui.QMessageBox.question(winner_widget, 'Winner', msg_box_str, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if winner_result == QtGui.QMessageBox.Yes:
            self._setup_game()

    def getWidgets(self, name):
        widgets = []
        for widget in QtGui.QApplication.allWidgets():
            if widget.objectName() == name:
                widgets.append(widget)
        return widgets

    def loadPlayers(self):
        widgets = (self.player_name_grid.itemAt(i).widget() for i in range(self.player_name_grid.count()))
        return_dict = dict.fromkeys(["players"], {})
        players = 0
        for w in widgets:
            if isinstance(w, QtGui.QComboBox):
                if str(w.currentText()) == "":
                    pass
                else:
                    return_dict["players"].update({str(w.objectName())[-2:]: {"player_name": str(w.currentText()), "rounds": {}}})
                    players += 1
        if players != self.nbr_players:
            self.nbr_players = players
        return return_dict

    def loadGameData(self):
        with open(gameFile) as json_data:
            games = json.load(json_data)
        return games

    def getVPIncome(self, player):
        widgets = (self.player_vp_grid.itemAt(i).widget() for i in range(self.player_vp_grid.count()))
        for w in widgets:
            if isinstance(w, QtGui.QSpinBox):
                if str(w.objectName()[-2:]) == player:
                    return w.value()

    def getCardIncome(self, player):
        widgets = (self.player_card_grid.itemAt(i).widget() for i in range(self.player_card_grid.count()))
        for w in widgets:
            if isinstance(w, QtGui.QSpinBox):
                if str(w.objectName()[-2:]) == player:
                    return w.value()

    def getPlayerTotalVP(self, data, rnd_vp=0):
        if self.round == 1:
            total = rnd_vp
        else:
            for k, v in data.items():
                if int(k) == (self.round - 1):
                    total = v['round_vp_total']
            total += rnd_vp
        return total

    def update_player(self, data, player, rnd=1, rnd_vp=0, rnd_cards=0):
        total_vp = rnd_vp
        #if rnd == 1:
            #total_vp = self.getPlayerTotalVP(data[player]['rounds'], rnd_vp)
            #data[player].update({'rounds': {str(rnd): {'card_income': rnd_cards, 'round_vp': rnd_vp, 'round_vp_total': total_vp}}})
        #else:
            #total_vp = self.getPlayerTotalVP(data[player]['rounds'], rnd_vp)
            #data[player]['rounds'][str(rnd)] = {'card_income': rnd_cards, 'round_vp': rnd_vp, 'round_vp_total': total_vp}
        total_vp = self.getPlayerTotalVP(data[player]['rounds'], rnd_vp)
        data[player]['rounds'][str(rnd)] = {'card_income': rnd_cards, 'round_vp': rnd_vp, 'round_vp_total': total_vp}
        return [data, {'player_name': data[player]['player_name'], 'vp': total_vp, 'cards': rnd_cards, 'rnd_vp': rnd_vp}]

    def _who_is_winning(self, data):
        for k, v in data.items():
            if v['vp'] >= self.winner_vp:
                if v['cards'] >= self.winner_cards:
                    self.winner_vp = v['vp']
                    self.winner_name = v['player_name']
                    self.winner_cards = v['cards']

    def _update_line_edits(self, undo=False):
        # TODO: Remove previous rounds score from boxes
        if not undo:
            for k, v in self.game_data['games'][str(self.game_id)]['players'].items():
                player = k
                round = v['rounds'][str(self.round)]
                total_vp = v['rounds'][str(self.round)]['round_vp_total']
                vp = v['rounds'][str(self.round)]['round_vp']
                msg = "%i (%i)" % (total_vp, vp)
                le_widget = self.getWidgets('te_' + player)
                le_widget[-1].append(msg)
                #if int(k) == self.round:
                    #msg = "%i (%i)" % (v['round_vp_total'], v['round_vp'])
                    #le_widget[-1].append(msg)
        elif undo:
            for k, v in self.game_data['games'][str(self.game_id)]['players'].items():
                player = k
                le_widget = self.getWidgets('te_' + player)
                txt = str(le_widget[-1].toPlainText())
                txt = '\n'.join(txt.splitlines()[:-1])
                le_widget[-1].setText(txt)
                
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
