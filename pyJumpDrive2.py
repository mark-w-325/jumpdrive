#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *


class JumpDrive(QWidget):
    
    def __init__(self):
        super(JumpDrive, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        myfont = QFont("Sans", 16, QFont.Bold)
        title = QLabel('Jump Drive')
        title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        title.setFont(myfont)
        
        main_grid = QGridLayout()
        main_grid.setSpacing(10)
        main_grid.setAlignment(Qt.AlignLeft)
        
        main_grid.addWidget(title, 0, 0, Qt.AlignTop | Qt.AlignCenter)
        
        
        nbr_players_grid = QHBoxLayout()
        nbr_players_grid.addStretch(1)
        
        nbr_player_lbl = QLabel('Number of Players')
        
        nbr_player_sb = QSpinBox()
        nbr_player_sb.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        nbr_players_grid.addWidget(nbr_player_lbl, 0, Qt.AlignTop | Qt.AlignLeft)
        nbr_players_grid.addWidget(nbr_player_sb, 0)
        
        main_grid.addLayout(nbr_players_grid, 1, 0, Qt.AlignLeft | Qt.AlignLeft)

        self.setLayout(main_grid)
        
        self.setGeometry(300, 300, 1200, 800)
        self.setWindowTitle('Jump Drive Point Tracker')
        self.show()

def main():
    
    app = QApplication(sys.argv)
    ex = JumpDrive()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()