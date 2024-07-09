from PyQt5.QtWidgets import QStackedWidget, QWidget, QGraphicsOpacityEffect
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QParallelAnimationGroup, QAbstractAnimation, Qt


class SlidingStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_direction = Qt.Horizontal
        self.m_speed = 500
        self.m_animationType = QEasingCurve.OutCubic
        self.m_now = 0
        self.m_next = 0
        self.m_wrap = False
        self.m_pnow = QPoint(0, 0)
        self.m_active = False
        self.m_animationGroup = QParallelAnimationGroup()

    def setDirection(self, direction):
        """
        设为Qt.Horizontal或Qt.Vertical
        Qt.Horizontal:水平
        Qt.Vertical:垂直
        :param direction:
        :return:
        """
        self.m_direction = direction

    def setSpeed(self, speed):
        self.m_speed = speed

    def setAnimation(self, animationType):
        self.m_animationType = animationType

    def setWrap(self, wrap):
        self.m_wrap = wrap

    def setCurrentWidget(self, w):
        self.slideInWgt(w)

    def slideInIdx(self, idx):
        if idx > self.count() - 1:
            idx = idx % self.count()
        elif idx < 0:
            idx = (idx + self.count()) % self.count()
        self.slideInWgt(self.widget(idx))

    def slideInWgt(self, newwidget):
        if self.m_active:
            self.m_animationGroup.stop()
            self.animationDoneSlot()
        self.m_active = True
        _now = self.currentIndex()
        _next = self.indexOf(newwidget)
        if _now == _next:
            self.m_active = False
            return

        if self.m_direction == Qt.Horizontal:
            offset = QPoint(self.frameRect().width(), 0)
        else:
            offset = -QPoint(0, self.frameRect().height())  # 使用高度作为垂直偏移

        self.widget(_next).setGeometry(self.frameRect())
        if _now < _next and self.m_direction == Qt.Horizontal:
            offset = -offset
        pnext = self.widget(_next).pos()
        pnow = self.widget(_now).pos()
        self.m_pnow = pnow

        self.widget(_next).move(pnext - offset)
        self.widget(_next).show()
        self.widget(_next).raise_()

        self.m_animationGroup = QParallelAnimationGroup(finished=self.animationDoneSlot)

        for index, start, end in zip((_now, _next), (pnow, pnext - offset), (pnow + offset, pnext)):
            animation = QPropertyAnimation(self.widget(index), b"pos")
            animation.setDuration(self.m_speed)
            animation.setEasingCurve(self.m_animationType)
            animation.setStartValue(start)
            animation.setEndValue(end)
            self.m_animationGroup.addAnimation(animation)

        self.m_next = _next
        self.m_now = _now
        self.m_active = True
        self.m_animationGroup.start(QAbstractAnimation.DeleteWhenStopped)

    def animationDoneSlot(self):
        self.setCurrentIndex(self.m_next)
        for i in range(self.count()):
            if i != self.m_next:
                self.widget(i).hide()
        self.widget(self.m_next).move(self.m_pnow)
        self.m_active = False

