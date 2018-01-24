import sys
import os
import json
from PyQt4 import QtCore, QtGui, uic
import pyqtgraph as pg
import pandas as pd
import numpy as np
from collections import OrderedDict
import pprint

pp = pprint.PrettyPrinter(indent=4)
qtCreatorFile = 'jumpdrive.ui'
playerFile = 'players.json'
gameFile = 'gamedata2.json'

data_columns = [('1game_id', int),
           ('2round_id', int),
           ('3player_name', str),
           ('4card_income', int),
           ('5round_vp', int),
           ('6round_vp_total', int)]

def create_empty_dataframe(cols):
    # create the dataframe from a dict
    temp_dict = OrderedDict()
    for k, t in sorted(cols):
        temp_dict[k[1:]] = pd.Series(dtype=t)
    temp_df = pd.DataFrame(temp_dict)
    return temp_df

with open(playerFile) as json_data:
    players = json.load(json_data)
players_lst = players['players']

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class JumpDrive(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.setGeometry(100, 100, 2250, 1250)
        self.setWindowTitle('Jump Drive Point Tracker')

        pg.setConfigOptions(antialias=True)

        self.cb_p1.clear()
        self.cb_p1.addItems(players_lst)

        self._setup_game()

        self.btn_add_players.clicked.connect(self.AddPlayer)
        self.btn_remove_player.clicked.connect(self.DeletePlayer)
        self.btn_reset.clicked.connect(self.ResetGame)
        self.btn_start_game.clicked.connect(self.StartGame)
        self.btn_add_score.clicked.connect(self.AddScore)
        self.btn_undo.clicked.connect(self.UndoScore)

    def _setup_game(self):
        self.nbr_players = 1
        self.round_id = 1
        self.game_data = self._loadGameData()
        self.game_id = self.game_data['game_id'].agg('max')
        if pd.isnull(self.game_id):
            self.game_id = 1
        else:
            self.game_id += 1
        print self.game_id
        self.players_lst = OrderedDict()
        self.game_started = False
        self.winning_score = 50
        self.winner_vp = 0
        self.winner_cards = 0
        self.data_dict = OrderedDict()

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

        # Setup plotting area
        self.dataplot.clear()
        labelStyle = {'color': '#FFF', 'size': '24pt'}
        self.dataplot.setTitle("Victory Points Board", **labelStyle)
        try:
            self.legend.scene().removeItem(self.legend)
        except Exception as e:
            pass

    def _loadGameData(self):
        if os.path.isfile(os.path.join(os.getcwd(), gameFile)):
            temp_dict = OrderedDict()
            for k, t in sorted(data_columns):
                temp_dict[k[1:]] = None
            df = pd.read_json(os.path.join(os.getcwd(), gameFile), orient='records')
            df = df[list(temp_dict.keys())].sort_values(list(temp_dict.keys()))
        else:
            df = create_empty_dataframe(data_columns)
        return df

    # Add players
    def AddPlayer(self):
        self.nbr_players = self.sb_nbr_players.value()
        if self.nbr_players == 1:
            return
        self._add_to_player_grid(self.nbr_players)

    def _add_to_player_grid(self, players):
        if players == 1:
            return
        else:
            for i in range(1, players + 1):
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

    # Remove players
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

    # Reset Game
    def ResetGame(self):
        reset_widget = QtGui.QWidget()
        reset_result = QtGui.QMessageBox.question(reset_widget, 'Reset Game',
        "Do you want to reset?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
        QtGui.QMessageBox.No)
        if reset_result == QtGui.QMessageBox.Yes:
            self._setup_game()

    # Start Game
    def StartGame(self):
        self._loadPlayers()
        self._setup_plot()
        self.game_started = True

    # Add Score
    def AddScore(self):
        if not self.game_started:
            self.StartGame()
        for k, v in self.players_lst.items():
            temp_dict = OrderedDict()
            te_name = 'te_' + k
            vp_name = 'sb_' + k
            card_name = 'sb_card_' + k
            vp_widget = self.getWidgets(vp_name)[-1]
            card_widget = self.getWidgets(card_name)[-1]
            round_vp = vp_widget.value()
            round_card = card_widget.value()
            round_total_vp = self._getPlayerTotalVP(v) + round_vp
            temp_dict['game_id'] = self.game_id
            temp_dict['round_id'] = self.round_id
            temp_dict['player_name'] = v
            temp_dict['card_income'] = round_card
            temp_dict['round_vp'] = round_vp
            temp_dict['round_vp_total'] = round_total_vp
            self._updateTextEdits(widget_name=te_name, round_vp=round_vp,
            total_vp=round_total_vp)
            self.game_data = self.game_data.append(temp_dict, ignore_index=True)
            self._prepData(str(k) + str(v), round_total_vp)
        self._plot_data()
        winner = self._who_is_winning()
        if winner is not None:
            self.EndGame(winner)
        else:
            self.round_id += 1

    def UndoScore(self):
        self.round_id -= 1
        # Delete the round from the game data
        self.game_data.drop(self.game_data[(self.game_data.game_id == self.game_id)
         & (self.game_data.round_id == self.round_id)].index, inplace=True)

        # Delete round from plotting dictionary
        for k, v in self.data_dict.items():
            v.pop(str(self.round_id), None)

        # Delete last line of text edits
        for k, v in self.players_lst.items():
            te_name = 'te_' + k
            self._updateTextEdits(widget_name=te_name, undo=True)

        # Re-plot data
        self.dataplot.clear()
        self._plot_data(undo=True)

    # End Game and save final state
    def EndGame(self, winner):
        winner_name = winner['player_name'].iloc[0]
        winner_vp = winner['round_vp_total'].iloc[0]
        winner_cards = winner['card_income'].iloc[0]
        self.game_data.to_json(path_or_buf=os.path.join(os.getcwd(), gameFile),
        orient='records')
        msg_box_str = 'The winner is %s with %i victory points and %i card income. ' \
        'Would you like to start another game?' % (winner_name, winner_vp, winner_cards)
        winner_widget = QtGui.QWidget()
        winner_result = QtGui.QMessageBox.question(winner_widget, 'Winner', msg_box_str,
        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if winner_result == QtGui.QMessageBox.Yes:
            self._setup_game()

    # Plotting functions
    def _setup_plot(self):
        #self.dataplot.addLegend()
        self.legend =self.dataplot.addLegend()
        labelStyle = {'color': '#FFF', 'font-size': '24pt'}
        self.dataplot.getAxis('left').setLabel(text='Victory Points', **labelStyle)
        self.dataplot.getAxis('bottom').setLabel(text='Round', **labelStyle)
        self.dataplot.setYRange(0, 50)
        self.dataplot.setXRange(0, self.round_id)

    def _prepData(self, player_key, vp):
        if self.round_id == 1:
            self.data_dict[player_key] = {str(self.round_id): vp}
        else:
            self.data_dict[player_key].update({str(self.round_id): vp})

    def _plot_data(self, undo=False):
        if undo:
            self.dataplot.setXRange(0, self.round_id)
        else:
            self.dataplot.setXRange(0, self.round_id + 1)
        for key in sorted(self.data_dict.iterkeys()):
            points = list()
            points.append(0)
            for key2 in sorted(self.data_dict[key].iterkeys()):
                points.append(self.data_dict[key][key2])
            if undo:
                x = np.arange(0, self.round_id)
            else:
                x = np.arange(0, self.round_id + 1)
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
            if self.round_id == 1:
                self.dataplot.plot(x=x, y=y, name=key[2:], pen=color, symbol=symbol,
                symboPen=color, symbolBrush=(55, 55, 55))
            else:
                self.dataplot.plot(x=x, y=y, pen=color, symbol=symbol,
                symbolPen=color, symbolBrush=(55,55,55))
        if self.round_id == 1:
            legendLabelStyle = {'color': '#FFF', 'size': '16pt', 'bold': True}
            for item in self.legend.items:
                for single_item in item:
                    if isinstance(single_item, pg.graphicsItems.LabelItem.LabelItem):
                        single_item.setText("\t" + single_item.text, **legendLabelStyle)

    # Helper functions
    def getWidgets(self, name):
        widgets = []
        for widget in QtGui.QApplication.allWidgets():
            if widget.objectName() == name:
                widgets.append(widget)
        return widgets

    def _loadPlayers(self):
        widgets = (self.player_name_grid.itemAt(i).widget() for i in
        range(self.player_name_grid.count()))
        players = 0
        for w in widgets:
            if isinstance(w, QtGui.QComboBox):
                if str(w.currentText()) == "":
                    pass
                else:
                    self.players_lst[str(w.objectName()[-2:])] = str(w.currentText())
                    players += 1
        if players != self.nbr_players:
            self.nbr_players = players

    def _getPlayerTotalVP(self, player_name):
        max_vp = self.game_data[(self.game_data.game_id == self.game_id) &
        (self.game_data.player_name == player_name)]['round_vp_total'].agg('max')
        if pd.isnull(max_vp):
            max_vp = 0
        return max_vp

    def _updateTextEdits(self, widget_name, round_vp=0, total_vp=0, undo=False):
        te_widget = self.getWidgets(widget_name)[-1]
        if not undo:
            msg = '%i (%i)' % (total_vp, round_vp)
            te_widget.append(msg)
        else:
            txt = str(te_widget.toPlainText())
            txt = '\n'.join(txt.splitlines()[:-1])
            te_widget.setText(txt)

    def _who_is_winning(self):
        if self.round_id == 1:
            return None
        else:
            df = self.game_data[(self.game_data.game_id == self.game_id) &
            (self.game_data.round_id == self.round_id)]
            df['vp_winning'] = df['round_vp_total'].apply(
            lambda x: True if x >= self.winning_score else False)
            if len(df[(df.vp_winning == True)]) > 0:
                return df.sort_values(['round_vp_total', 'card_income'],
                ascending=[False, False]).iloc[[0]]
            return None


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = JumpDrive()
    window.show()
    sys.exit(app.exec_())
