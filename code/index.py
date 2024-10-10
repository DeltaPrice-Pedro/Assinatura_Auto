from src.window_ass import Ui_MainWindow
from PySide6.QtWidgets import (QMainWindow, QApplication, QLabel, QWidget)
from PySide6.QtGui import QMovie, QIcon, QPixmap
from docxtpl import DocxTemplate, InlineImage
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox
from spire.doc import Document, ImageType
from docx.shared import Mm
import time
import os
import sys

def resource_path(relative_path):
    base_path = getattr(
        sys,
        '_MEIPASS',
        os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class Arquivo:
    def __init__(self, caminho: str) -> None:
        self.caminho = DocxTemplate(caminho)
        pass

    def renderizar(self, ref: dict, path: str):
        self.caminho.render(ref)
        self.caminho.save(path)

    def enquadro(self, img:str):
        return InlineImage(self.caminho, img, width=Mm(100))

class Assinatura:
    def __init__(self) -> None:
        self.base_ass = Arquivo(resource_path('src\\base_assinaturas.docx'))
        self.base_texto = Arquivo(resource_path('src\\base_texto.docx'))

        self.ENDR_EMAIL = '@deltaprice.com.br'

        self.NOME_ARQ = 'assin_word.docx'
        self.NOME_PNG = 'page.png'

        self.KEY_NOME = 'nome'
        self.KEY_SETOR = 'setor'
        self.KEY_IMG = 'img'
        pass

    def preencher_modelo(self, nome_func: str, setor: str):
        ref = {
            self.KEY_NOME: nome_func,
            self.KEY_SETOR: setor + self.ENDR_EMAIL
        }

        self.base_ass.renderizar(ref, self.NOME_ARQ)

    def gerar_png(self):
        # Create a Document object
        document = Document(self.NOME_ARQ)
        # Convert a specific page to bitmap image
        imageStream = document.SaveImageToStreams(0, ImageType.Bitmap)
    
        # Save the bitmap to a PNG file
        with open(self.NOME_PNG,'wb') as imageFile:
            imageFile.write(imageStream.ToArray())
        document.Close()

        os.remove(self.NOME_ARQ)

    def add_img(self, nome_arq: str):
        my_image = self.base_texto.enquadro(self.NOME_PNG)
        
        ref = {self.KEY_IMG: my_image}
        self.base_texto.renderizar(ref, nome_arq+'.docx')
        os.remove(self.NOME_PNG)

class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon((QIcon(resource_path('src\\img\\ass-icon.ico'))))
        self.logo_hori.setPixmap(QPixmap(resource_path(
            'src\\img\\ass-hori.png')))

        self.pushButton.clicked.connect(
            self.executar)

        self.lineEdit.setPlaceholderText('Preencha aqui')

        self.comboBox.setPlaceholderText('Selecione a opção')
        self.comboBox.addItems(
            ['Processos', 'Financeiro', 'Fiscal', 'Contabilidade', 'Trabalhista']
            )

    def executar(self):
        # try:
            if self.lineEdit.text() == '':
                raise Exception('Favor insirir seu nome!')
            elif self.comboBox.currentText() == '':
                raise Exception('Favor selecione seu setor!')
            
            ass = Assinatura()

            ass.preencher_modelo(
                self.lineEdit.text(), self.comboBox.currentText().lower())

            ass.gerar_png()
            nome_arq = self.onde_salvar()

            ass.add_img(nome_arq)

            messagebox.showinfo(title='Aviso', message='Abrindo o arquivo gerado!')

            os.startfile(nome_arq+'.docx')
            
        # except Exception as error:
        #     messagebox.showerror(title='Aviso', message= str(error))

    def onde_salvar(self):
        file = asksaveasfilename(title='Favor selecionar a pasta onde será salvo', filetypes=((".docx","*.docx"),))

        if file == '':
            resp = messagebox.askyesno(title='Deseja cancelar a operação?', filetypes=((".docx","*.docx"),))
            if resp == True:
                raise 'Operação cancelada!'
            else:
                return self.onde_salvar()

        return file

if __name__ == '__main__':
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()