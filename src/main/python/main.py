from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from PyQt5.QtWidgets import QWidget, QLayout, QLayoutItem, QStyle, QSizePolicy, QMainWindow, QPushButton, QScrollArea, QFrame, QVBoxLayout, QToolButton

import os
import sys
import typing


class FlowLayout(QLayout):
    def __init__(self, parent: QWidget=None, margin: int=-1, hSpacing: int=-1, vSpacing: int=-1):
        super().__init__(parent)

        self.itemList = list()
        self.m_hSpace = hSpacing
        self.m_vSpace = vSpacing

        self.setContentsMargins(margin, margin, margin, margin)

    def __del__(self):
        # copied for consistency, not sure this is needed or ever called
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item: QLayoutItem):
        self.itemList.append(item)

    def horizontalSpacing(self) -> int:
        if self.m_hSpace >= 0:
            return self.m_hSpace
        else:
            return self.smartSpacing(QStyle.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self) -> int:
        if self.m_vSpace >= 0:
            return self.m_vSpace
        else:
            return self.smartSpacing(QStyle.PM_LayoutVerticalSpacing)

    def count(self) -> int:
        return len(self.itemList)

    def itemAt(self, index: int) -> typing.Union[QLayoutItem, None]:
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        else:
            return None

    def takeAt(self, index: int) -> typing.Union[QLayoutItem, None]:
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        else:
            return None

    def expandingDirections(self) -> Qt.Orientations:
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect: QRect) -> None:
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def smartSpacing(self, pm: QStyle.PixelMetric) -> int:
        parent = self.parent()
        if not parent:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()

    def doLayout(self, rect: QRect, testOnly: bool) -> int:
        left, top, right, bottom = self.getContentsMargins()
        effectiveRect = rect.adjusted(+left, +top, -right, -bottom)
        x = effectiveRect.x()
        y = effectiveRect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.horizontalSpacing()
            if spaceX == -1:
                spaceX = wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
            spaceY = self.verticalSpacing()
            if spaceY == -1:
                spaceY = wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)

            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > effectiveRect.right() and lineHeight > 0:
                x = effectiveRect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
    
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y() + bottom

    def addLayout(self, layout: QLayout, stretch: int=0):
        # "equivalent" of `QBoxLayout.addLayout()`
        # we want to add sub-layouts (e.g. a `QVBoxLayout` holding a label above a widget)
        # there is some dispute as to how to do this/whether it is supported by `FlowLayout`
        # see my https://forum.qt.io/topic/104653/how-to-do-a-no-break-qhboxlayout
        # there is a suggestion that we should not add a sub-layout but rather enclose it in a `QWidget`
        # but since it seems to be working as I've done it below I'm elaving it at that for now...

        # suprisingly to me, we do not need to add the layout via `addChildLayout()`, that seems to make no difference
        # self.addChildLayout(layout)
        # all that seems to be reuqired is to add it onto the list via `addItem()`
        self.addItem(layout)

    def addStretch(self, stretch: int=0):
        # "equivalent" of `QBoxLayout.addStretch()`
        # we can't do stretches, we just arbitrarily put in a "spacer" to give a bit of a gap
        w = stretch * 20
        spacerItem = QtWidgets.QSpacerItem(w, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.addItem(spacerItem)


class MyScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.layout = FlowLayout()
        for file_name in os.listdir('img/'):
            champ_name = file_name[:-4]
            tb = QToolButton()
            tb.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            tb.setText(champ_name)
            tb.setFixedSize(QSize(108,124))
            tb.setIconSize(QSize(100,100))
            icon = QIcon(f"img\{file_name}")

            pixmap = icon.pixmap(max(icon.availableSizes()))
            image = pixmap.toImage()
            grayscale = image.convertToFormat(QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(grayscale)
            
            tb.setIcon(QIcon(pixmap))
            self.layout.addWidget(tb)
        
        scroll = QWidget()
        scroll.setLayout(self.layout)
        self.setWidget(scroll)


if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = QWidget()
    window_layout = QVBoxLayout()
    #window_layout.addWidget(QPushButton("fuck"))  # add filter/search bar here maybe?
    window_layout.addWidget(MyScrollArea())
    window.setLayout(window_layout)



    window.resize(510, 800)
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)