# main.py

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

# ESTILO QSS GLOBAL - TEMA CLARO CORPORATIVO (VERSÃO 2)
CUSTOM_QSS = """
    /* Estilo Global para a Janela e Widgets Base */
    QMainWindow, QWidget {
        background-color: #F0F0F0; /* Fundo cinza claro principal */
        color: #333333; /* Cor de texto escura para legibilidade */
        font-family: Segoe UI, Arial, sans-serif;
        font-size: 10pt;
    }

    /* Estilo para QGroupBox */
    QGroupBox {
        font-weight: bold;
        border: 1px solid #CCCCCC;
        border-radius: 6px;
        margin-top: 12px;
        background-color: #FFFFFF;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px 0 5px;
        left: 10px;
        color: #333333;
    }

    /* Estilo para QPushButton (Botões de Ação) */
    QPushButton {
        background-color: #2ECC71; /* Verde mais claro e moderno */
        color: white;
        border: 1px solid #27AE60;
        padding: 8px 15px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #58D68D; /* Verde ainda mais claro no hover */
        border: 1px solid #2ECC71;
    }
    QPushButton:pressed {
        background-color: #27AE60; /* Verde mais escuro quando pressionado */
    }
    QPushButton:disabled {
        background-color: #BDBDBD;
        color: #757575;
        border-color: #AAAAAA;
    }

    /* Estilo Específico para o Botão Cancelar */
    QPushButton#btn_cancelar_operacao {
        background-color: #E74C3C; /* Vermelho mais suave */
        border-color: #C0392B;
    }
    QPushButton#btn_cancelar_operacao:hover {
        background-color: #EC7063;
        border-color: #E74C3C;
    }
    QPushButton#btn_cancelar_operacao:pressed {
        background-color: #C0392B;
    }

    /* Estilo para QComboBox e QLineEdit */
    QComboBox, QLineEdit {
        background-color: #FFFFFF;
        color: #333333;
        border: 1px solid #CCCCCC;
        padding: 4px 8px;
        border-radius: 4px;
        min-height: 20px;
    }
    QComboBox:hover, QLineEdit:focus {
        border-color: #2ECC71; /* Destaque verde no foco/hover */
    }
    
    QComboBox QAbstractItemView {
        background-color: #FFFFFF;
        color: #333333;
        border: 1px solid #CCCCCC;
        selection-background-color: #2ECC71;
        selection-color: white;
    }

    /* Estilo para QTextEdit (Console) */
    QTextEdit {
        background-color: #FFFFFF;
        color: #2C3E50;
        border: 1px solid #CCCCCC;
        border-radius: 4px;
        font-family: "Courier New", Courier, monospace;
    }
    
    /* --- NOVO: Estilo para QScrollArea e QScrollBar --- */
    QScrollArea {
        border: none; /* Remove a borda da área de scroll em si */
    }

    QScrollBar:vertical {
        border: 1px solid #CCCCCC;
        background: #F0F0F0;
        width: 15px; /* Largura da barra de scroll */
        margin: 0px 0px 0px 0px;
    }
    QScrollBar::handle:vertical {
        background: #BDBDBD; /* Cor do "puxador" da barra */
        min-height: 20px;
        border-radius: 7px;
    }
    QScrollBar::handle:vertical:hover {
        background: #A0A0A0; /* Cor ao passar o mouse */
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
    
    /* Outros Widgets */
    QLabel, QRadioButton {
        color: #333333;
        background-color: transparent;
    }
    QProgressBar {
        border: 1px solid #CCCCCC;
        border-radius: 4px;
        text-align: center;
        color: white;
        background-color: #FFFFFF;
    }
    QProgressBar::chunk {
        background-color: #2ECC71;
        border-radius: 3px;
        margin: 1px;
    }
"""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(CUSTOM_QSS)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())