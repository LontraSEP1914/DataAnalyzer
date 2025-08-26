# gui/main_window.py

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QComboBox, QMessageBox,
    QGroupBox, QGridLayout, QProgressBar, QTextEdit, QScrollArea, 
    QLineEdit, QListWidget, QAbstractItemView, QRadioButton
)
from PyQt6.QtCore import Qt, QDateTime, pyqtSignal, QObject, QThread
from functools import partial

# Importar funções do nosso módulo core
try:
    from core.excel_parser import carregar_dados_excel
    from core.data_comparator import comparar_dataframes, _aplicar_filtro_df
    from core.report_generator import gerar_relatorio_excel
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from core.excel_parser import carregar_dados_excel
    from core.data_comparator import comparar_dataframes, _aplicar_filtro_df
    from core.report_generator import gerar_relatorio_excel

class MappingPairWidget(QWidget):
    remove_pair_requested = pyqtSignal(QWidget)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.combo_a = QComboBox()
        self.combo_b = QComboBox()
        self.btn_remove = QPushButton("X")
        self.btn_remove.setFixedWidth(30)
        self.btn_remove.clicked.connect(self._request_remove)
        self.layout.addWidget(QLabel("A:"))
        self.layout.addWidget(self.combo_a, 1)
        self.layout.addWidget(QLabel("vs B:"))
        self.layout.addWidget(self.combo_b, 1)
        self.layout.addWidget(self.btn_remove)

    def _request_remove(self):
        self.remove_pair_requested.emit(self)

    def get_selected_pair(self):
        col_a = self.combo_a.currentText()
        col_b = self.combo_b.currentText()
        if col_a and col_b: return (col_a, col_b)
        return None

    def populate_combos(self, cols_a, cols_b, default_a=None, default_b=None):
        current_a = self.combo_a.currentText() if not default_a else default_a
        current_b = self.combo_b.currentText() if not default_b else default_b
        self.combo_a.clear(); self.combo_a.addItems([""] + cols_a)
        if current_a in [""] + cols_a: self.combo_a.setCurrentText(current_a)
        self.combo_b.clear(); self.combo_b.addItems([""] + cols_b)
        if current_b in [""] + cols_b: self.combo_b.setCurrentText(current_b)

class ConfrontoWorker(QObject):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(int, str)

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.is_cancelled = False

    def run(self):
        """O método que executa o trabalho pesado, agora com toda a lógica."""
        try:
            total_steps = 5
            # Desempacotar a configuração
            caminho_a = self.config['caminho_a']
            caminho_b = self.config['caminho_b']
            colunas_chave_a = self.config['colunas_chave_a']
            colunas_chave_b = self.config['colunas_chave_b']
            pares_mapeados = self.config['pares_mapeados']
            tipo_join = self.config['tipo_join']
            filtro_a_info = self.config['filtro_a']
            filtro_b_info = self.config['filtro_b']
            
            # Etapa 1: Carregar Arquivo A
            self.progress.emit(1, f"Carregando Arquivo A...")
            if self.is_cancelled: return
            df_a_original = carregar_dados_excel(caminho_a) # Carrega todas as colunas inicialmente
            if df_a_original is None: raise RuntimeError("Falha ao carregar Arquivo A.")
            
            # Etapa 2: Aplicar Filtro em A
            self.progress.emit(2, f"Aplicando filtro no Arquivo A...")
            df_a = _aplicar_filtro_df(df_a_original, filtro_a_info) if filtro_a_info else df_a_original
            self.log_message(f"Dados de A preparados ({len(df_a)} linhas).")
            
            # Etapa 3: Carregar Arquivo B
            if self.is_cancelled: return
            self.progress.emit(3, f"Carregando Arquivo B...")
            df_b_original = carregar_dados_excel(caminho_b)
            if df_b_original is None: raise RuntimeError("Falha ao carregar Arquivo B.")
            
            # Etapa 4: Aplicar Filtro em B
            self.progress.emit(4, f"Aplicando filtro no Arquivo B...")
            df_b = _aplicar_filtro_df(df_b_original, filtro_b_info) if filtro_b_info else df_b_original
            self.log_message(f"Dados de B preparados ({len(df_b)} linhas).")

            # Etapa 5: Comparar DataFrames
            if self.is_cancelled: return
            self.progress.emit(5, "Realizando a comparação dos dados...")
            resultados = comparar_dataframes(
                df_lado_a=df_a, df_lado_b=df_b,
                colunas_chave_a=colunas_chave_a, colunas_chave_b=colunas_chave_b,
                pares_mapeados=pares_mapeados, tipo_join=tipo_join
            )
            if resultados is None:
                raise RuntimeError("Erro desconhecido durante a comparação dos dados.")
            
            self.progress.emit(total_steps, "Processamento concluído. Pronto para gerar relatório.")
            self.finished.emit(resultados)

        except Exception as e:
            import traceback
            error_msg = f"Erro na thread de processamento: {e}\n{traceback.format_exc()}"
            self.error.emit(error_msg)

    def request_cancel(self):
        self.is_cancelled = True
        self.log_message("Worker recebeu solicitação de cancelamento.")

    def log_message(self, message):
        # Apenas para debug interno do worker
        print(f"[Worker Log] {message}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataAnalyzer - Confronto e Cruzamento de Dados")
        self.setGeometry(100, 100, 950, 950)
        self.setMinimumSize(850, 700)
        self.df_a_carregado, self.df_b_carregado = None, None
        self.arquivo_a_path, self.arquivo_b_path = None, None
        self.df_a_cols, self.df_b_cols = [], []
        self.mapping_pair_widgets_list = []
        self.thread, self.worker = None, None
        self._init_ui()
        self.log_message("Aplicação inicializada.")
        self._add_mapping_pair_ui()
    
    def _create_filter_group(self, side_label):
        group_box = QGroupBox(f"Filtro Lado {side_label}")
        group_box.setCheckable(True); group_box.setChecked(False)
        layout = QGridLayout(group_box)
        label_coluna, combo_coluna = QLabel("Coluna:"), QComboBox()
        label_operador, combo_operador = QLabel("Operador:"), QComboBox()
        combo_operador.addItems(['=', '!=', '>', '<', '>=', '<=', 'contém', 'não contém', 'começa com', 'termina com', 'é nulo', 'não é nulo'])
        label_valor, edit_valor = QLabel("Valor:"), QLineEdit()

        def toggle_valor_edit():
            is_null_op = combo_operador.currentText() in ['é nulo', 'não é nulo']
            edit_valor.setEnabled(not is_null_op); 
            if is_null_op: edit_valor.clear()
        combo_operador.currentTextChanged.connect(toggle_valor_edit)
        
        layout.addWidget(label_coluna, 0, 0); layout.addWidget(combo_coluna, 0, 1)
        layout.addWidget(label_operador, 1, 0); layout.addWidget(combo_operador, 1, 1)
        layout.addWidget(label_valor, 2, 0); layout.addWidget(edit_valor, 2, 1)
        
        widgets = [label_coluna, combo_coluna, label_operador, combo_operador, label_valor, edit_valor]
        def on_group_toggled(checked):
            for widget in widgets: widget.setEnabled(checked)
            if checked: toggle_valor_edit()
        group_box.toggled.connect(on_group_toggled)
        on_group_toggled(False)
        return group_box, combo_coluna, combo_operador, edit_valor

    def _init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        # 1. A ScrollArea agora é o widget central da janela.
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True) # Permite que o conteúdo se expanda.
        self.setCentralWidget(scroll_area)

        # 2. Criamos um widget de conteúdo que irá conter nosso layout.
        content_widget = QWidget()
        scroll_area.setWidget(content_widget) # Coloca o widget dentro da scroll area.
        main_layout = QVBoxLayout(content_widget)

        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # MODO DE OPERAÇÃO
        group_box_modo = QGroupBox("Modo de Operação")
        modo_layout = QHBoxLayout(group_box_modo)
        self.radio_modo_confronto = QRadioButton("Confronto de Dados (Comparar Valores)")
        self.radio_modo_confronto.setChecked(True)
        self.radio_modo_cruzamento = QRadioButton("Cruzamento Simples (Apenas Unir)")
        self.radio_modo_confronto.toggled.connect(self._atualizar_ui_modo)
        modo_layout.addWidget(self.radio_modo_confronto)
        modo_layout.addWidget(self.radio_modo_cruzamento)
        main_layout.addWidget(group_box_modo)

        top_section_layout = QHBoxLayout()
        # Lado A
        group_box_a = QGroupBox("Arquivo e Chave Lado A")
        lado_a_layout = QVBoxLayout(group_box_a)
        self.btn_selecionar_a = QPushButton("Selecionar Arquivo A")
        self.btn_selecionar_a.clicked.connect(lambda: self._selecionar_arquivo('A'))
        self.label_arquivo_a = QLabel("Nenhum arquivo selecionado")
        self.list_chaves_a = QListWidget()
        self.list_chaves_a.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        lado_a_layout.addWidget(self.btn_selecionar_a)
        lado_a_layout.addWidget(self.label_arquivo_a)
        lado_a_layout.addWidget(QLabel("Coluna(s) Chave A:"))
        lado_a_layout.addWidget(self.list_chaves_a)
        top_section_layout.addWidget(group_box_a)
        
        # Lado B
        group_box_b = QGroupBox("Arquivo e Chave Lado B")
        lado_b_layout = QVBoxLayout(group_box_b)
        self.btn_selecionar_b = QPushButton("Selecionar Arquivo B")
        self.btn_selecionar_b.clicked.connect(lambda: self._selecionar_arquivo('B'))
        self.label_arquivo_b = QLabel("Nenhum arquivo selecionado")
        self.list_chaves_b = QListWidget()
        self.list_chaves_b.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        lado_b_layout.addWidget(self.btn_selecionar_b)
        lado_b_layout.addWidget(self.label_arquivo_b)
        lado_b_layout.addWidget(QLabel("Coluna(s) Chave B:"))
        lado_b_layout.addWidget(self.list_chaves_b)
        top_section_layout.addWidget(group_box_b)
        main_layout.addLayout(top_section_layout)

        # MAPEAMENTO DE COLUNAS
        self.group_box_mapping = QGroupBox("Mapeamento de Colunas de Valor para Comparação")
        mapping_outer_layout = QVBoxLayout(self.group_box_mapping)
        self.btn_add_pair = QPushButton("Adicionar Par de Comparação")
        self.btn_add_pair.clicked.connect(self._add_mapping_pair_ui)
        self.scroll_area_mappings = QScrollArea(); self.scroll_area_mappings.setWidgetResizable(True)
        self.container_mappings_widget = QWidget()
        self.dynamic_mappings_layout = QVBoxLayout(self.container_mappings_widget)
        self.dynamic_mappings_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area_mappings.setWidget(self.container_mappings_widget)
        mapping_outer_layout.addWidget(self.btn_add_pair, alignment=Qt.AlignmentFlag.AlignLeft)
        mapping_outer_layout.addWidget(self.scroll_area_mappings)
        main_layout.addWidget(self.group_box_mapping)
        
        # FILTROS
        filtros_main_layout = QHBoxLayout()
        gb_filtro_a, self.combo_coluna_filtro_a, self.combo_operador_filtro_a, self.edit_valor_filtro_a = self._create_filter_group("A")
        gb_filtro_b, self.combo_coluna_filtro_b, self.combo_operador_filtro_b, self.edit_valor_filtro_b = self._create_filter_group("B")
        filtros_main_layout.addWidget(gb_filtro_a); filtros_main_layout.addWidget(gb_filtro_b)
        main_layout.addLayout(filtros_main_layout)

        # OPÇÕES GERAIS
        group_box_opcoes = QGroupBox("Opções Gerais de Comparação")
        opcoes_layout = QHBoxLayout(group_box_opcoes)
        self.combo_tipo_join = QComboBox()
        self.combo_tipo_join.addItems(['inner', 'left', 'right', 'outer'])
        opcoes_layout.addWidget(QLabel("Tipo de Junção (Join):"))
        opcoes_layout.addWidget(self.combo_tipo_join); opcoes_layout.addStretch(1)
        main_layout.addWidget(group_box_opcoes)
        
        # PROGRESSO E CONSOLE
        self.progress_bar = QProgressBar(); self.progress_bar.setRange(0, 5)
        self.console_output = QTextEdit(); self.console_output.setReadOnly(True)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(QLabel("Console de Saída:"))
        main_layout.addWidget(self.console_output, 1)
        
        # BOTÕES DE AÇÃO
        action_buttons_layout = QHBoxLayout()
        self.btn_iniciar_confronto = QPushButton("Iniciar Confronto e Gerar Relatório")
        self.btn_cancelar_operacao = QPushButton("Cancelar Operação")
        self.btn_cancelar_operacao.setObjectName("btn_cancelar_operacao")
        self.btn_iniciar_confronto.clicked.connect(self._iniciar_confronto)
        self.btn_cancelar_operacao.clicked.connect(self._solicitar_cancelamento)
        action_buttons_layout.addStretch(1)
        action_buttons_layout.addWidget(self.btn_iniciar_confronto)
        action_buttons_layout.addWidget(self.btn_cancelar_operacao)
        action_buttons_layout.addStretch(1)
        main_layout.addLayout(action_buttons_layout)

        self._atualizar_ui_modo()

    def _atualizar_ui_modo(self):
        is_cruzamento = self.radio_modo_cruzamento.isChecked()
        self.group_box_mapping.setVisible(not is_cruzamento)
        self.btn_iniciar_confronto.setText("Iniciar Cruzamento e Gerar Relatório" if is_cruzamento else "Iniciar Confronto e Gerar Relatório")

    def _update_all_column_widgets(self, lado: str):
        cols = self.df_a_cols if lado == 'A' else self.df_b_cols
        list_chaves = self.list_chaves_a if lado == 'A' else self.list_chaves_b
        combo_filtro = self.combo_coluna_filtro_a if lado == 'A' else self.combo_coluna_filtro_b
        
        selected_chaves = [item.text() for item in list_chaves.selectedItems()]
        list_chaves.clear(); list_chaves.addItems(cols)
        for item_text in selected_chaves:
            items = list_chaves.findItems(item_text, Qt.MatchFlag.MatchExactly)
            if items: items[0].setSelected(True)
        
        current_filtro = combo_filtro.currentText()
        combo_filtro.clear(); combo_filtro.addItems([""] + cols)
        if current_filtro in cols: combo_filtro.setCurrentText(current_filtro)
        self._update_all_mapping_combos()

    def _selecionar_arquivo(self, lado):
        caminho, _ = QFileDialog.getOpenFileName(self, f"Selecionar Arquivo {lado}", "", "*.xlsx *.xls *.csv")
        if not caminho: return
        
        self.log_message(f"Carregando arquivo para o Lado {lado}: {os.path.basename(caminho)}")
        df = carregar_dados_excel(caminho)
        if df is None or df.empty:
            msg = "Falha ao ler o arquivo ou o arquivo está vazio."
            self.log_message(msg, is_error=True)
            QMessageBox.warning(self, "Erro de Leitura", msg)
            return
        
        cols = [str(col) for col in df.columns]
        if lado == 'A':
            self.df_a_carregado, self.df_a_cols, self.arquivo_a_path = df, cols, caminho
            self.label_arquivo_a.setText(f"Arquivo A: {os.path.basename(caminho)}")
        else:
            self.df_b_carregado, self.df_b_cols, self.arquivo_b_path = df, cols, caminho
            self.label_arquivo_b.setText(f"Arquivo B: {os.path.basename(caminho)}")
        
        self._update_all_column_widgets(lado)
        self.log_message(f"Arquivo {os.path.basename(caminho)} carregado com {len(cols)} colunas.")
    
    def _iniciar_confronto(self):
        self.console_output.clear()
        self.log_message("Iniciando validações...")

        # Validações da UI
        if not all([self.arquivo_a_path, self.arquivo_b_path]):
            return self.show_error_and_log("Selecione os arquivos para Lado A e Lado B.")
        colunas_chave_a = [item.text() for item in self.list_chaves_a.selectedItems()]
        colunas_chave_b = [item.text() for item in self.list_chaves_b.selectedItems()]
        if not all([colunas_chave_a, colunas_chave_b]):
            return self.show_error_and_log("Selecione pelo menos uma coluna chave para cada lado.")
        if len(colunas_chave_a) != len(colunas_chave_b):
            return self.show_error_and_log("O número de colunas chave para Lado A e B deve ser igual.")

        is_cruzamento_mode = self.radio_modo_cruzamento.isChecked()
        pares_mapeados = []
        if not is_cruzamento_mode:
            pares_mapeados = [p.get_selected_pair() for p in self.mapping_pair_widgets_list if p.get_selected_pair()]
            if not pares_mapeados:
                return self.show_error_and_log("Modo Confronto: adicione pelo menos um par de colunas de valor.")
            # Validação adicional para não usar chave como valor
            chaves_set = set(colunas_chave_a + colunas_chave_b)
            valores_set = {p[0] for p in pares_mapeados} | {p[1] for p in pares_mapeados}
            if not chaves_set.isdisjoint(valores_set):
                return self.show_error_and_log("Coluna chave não pode ser usada como coluna de valor.")

        # Coletar filtros
        def get_filter_info(gb, combo_col, combo_op, edit_val):
            if not gb.isChecked(): return None
            col, op, val = combo_col.currentText(), combo_op.currentText(), edit_val.text().strip()
            if not col: self.show_error_and_log("Filtro ativado mas sem coluna selecionada."); return "INVALID"
            if op not in ['é nulo', 'não é nulo'] and not val:
                self.show_error_and_log("Filtro requer um valor para o operador selecionado."); return "INVALID"
            return {'coluna': col, 'operador': op, 'valor': val}

        filtro_a = get_filter_info(self.combo_coluna_filtro_a.parentWidget(), self.combo_coluna_filtro_a, self.combo_operador_filtro_a, self.edit_valor_filtro_a)
        filtro_b = get_filter_info(self.combo_coluna_filtro_b.parentWidget(), self.combo_coluna_filtro_b, self.combo_operador_filtro_b, self.edit_valor_filtro_b)
        if "INVALID" in [filtro_a, filtro_b]: return

        # Configuração e início da Thread
        config = {
            "caminho_a": self.arquivo_a_path, "caminho_b": self.arquivo_b_path,
            "colunas_chave_a": colunas_chave_a, "colunas_chave_b": colunas_chave_b,
            "pares_mapeados": pares_mapeados, "tipo_join": self.combo_tipo_join.currentText(),
            "filtro_a": filtro_a, "filtro_b": filtro_b
        }
        
        self.set_ui_for_processing(True)
        self.thread = QThread()
        self.worker = ConfrontoWorker(config)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_confronto_finished)
        self.worker.error.connect(self._on_confronto_error)
        self.worker.progress.connect(self._on_progress_update)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        self.log_message("Validações concluídas. Iniciando processamento em background...")

    def _on_confronto_finished(self, resultados):
        self.log_message("Processamento concluído. Solicitando local para salvar o relatório.")
        is_cruzamento = not bool(resultados.get('resumo_por_par'))
        filename = "Resultado_Cruzamento.xlsx" if is_cruzamento else "Relatorio_Confronto.xlsx"
        caminho_salvar, _ = QFileDialog.getSaveFileName(self, "Salvar Relatório", filename, "*.xlsx")
        
        if caminho_salvar:
            if not caminho_salvar.lower().endswith(".xlsx"): caminho_salvar += ".xlsx"
            self.log_message(f"Gerando relatório em: {caminho_salvar}...")
            if gerar_relatorio_excel(resultados, caminho_salvar):
                QMessageBox.information(self, "Sucesso", f"Relatório gerado com sucesso!\n{caminho_salvar}")
                self.log_message("Relatório gerado com sucesso!")
            else:
                self.show_error_and_log("Falha ao gerar o arquivo de relatório Excel.")
        else:
            self.log_message("Geração de relatório cancelada pelo usuário.")
        
        self.set_ui_for_processing(False)

    def _on_confronto_error(self, error_message):
        self.show_error_and_log(f"Ocorreu um erro crítico:\n{error_message}", show_box=False)
        QMessageBox.critical(self, "Erro na Operação", f"Ocorreu um erro crítico durante o processamento.\nVerifique o console para mais detalhes.")
        self.set_ui_for_processing(False)

    def _on_progress_update(self, value, message):
        self.progress_bar.setValue(value)
        self.log_message(message)
    
    def _solicitar_cancelamento(self):
        if self.worker:
            self.log_message("CANCELAMENTO SOLICITADO!", is_error=True)
            self.worker.request_cancel()
            self.btn_cancelar_operacao.setText("Cancelando...")

    def set_ui_for_processing(self, is_processing):
        self.btn_iniciar_confronto.setEnabled(not is_processing)
        self.btn_cancelar_operacao.setEnabled(is_processing)
        if not is_processing:
            self.progress_bar.setValue(0)
            self.btn_cancelar_operacao.setText("Cancelar Operação")

    def show_error_and_log(self, message, show_box=True):
        self.log_message(message, is_error=True)
        if show_box: QMessageBox.warning(self, "Aviso", message)

    def log_message(self, message: str, is_error: bool = False):
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        prefix = "[ERRO]" if is_error else "[INFO]"
        color = "red" if is_error else "#EAECEE" if self.console_output.styleSheet() else "black"
        self.console_output.append(f'<font color="{color}">[{timestamp}] {prefix} {message}</font>')

    # Métodos de gerenciamento dos pares de mapeamento (sem alterações)
    def _add_mapping_pair_ui(self, col_a=None, col_b=None):
        pair_widget = MappingPairWidget()
        pair_widget.populate_combos(self.df_a_cols, self.df_b_cols, col_a, col_b)
        pair_widget.remove_pair_requested.connect(self._remove_mapping_pair_ui)
        self.dynamic_mappings_layout.addWidget(pair_widget)
        self.mapping_pair_widgets_list.append(pair_widget)

    def _remove_mapping_pair_ui(self, pair_widget):
        if pair_widget in self.mapping_pair_widgets_list:
            self.dynamic_mappings_layout.removeWidget(pair_widget)
            pair_widget.deleteLater()
            self.mapping_pair_widgets_list.remove(pair_widget)

    def _update_all_mapping_combos(self):
        for widget in self.mapping_pair_widgets_list:
            widget.populate_combos(self.df_a_cols, self.df_b_cols)