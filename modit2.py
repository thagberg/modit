import ctypes, os, sys

from cefpython3 import cefpython
from PyQt4 import QtGui
from PyQt4 import QtCore

def GetApplicationPath(file=None):
    import re, os, platform
    # If file is None return current directory without trailing slash.
    if file is None:
        file = ""
    # Only when relative path.
    if not file.startswith("/") and not file.startswith("\\") and (
            not re.search(r"^[\w-]+:", file)):
        if hasattr(sys, "frozen"):
            path = os.path.dirname(sys.executable)
        elif "__file__" in globals():
            path = os.path.dirname(os.path.realpath(__file__))
        else:
            path = os.getcwd()
        path = path + os.sep + file
        if platform.system() == "Windows":
            path = re.sub(r"[/\\]+", re.escape(os.sep), path)
        path = re.sub(r"[/\\]+$", "", path)
        return path
    return str(file)

class MainWindow(QtGui.QMainWindow):
    mainFrame = None

    def __init__(self):
        super(MainWindow, self).__init__(None)
        self.mainFrame = MainFrame(self)
        self.setCentralWidget(self.mainFrame)
        self.resize(1280, 1024)
        self.setWindowTitle('Modit Editor')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def focusInEvent(self, event):
        # cefpython.WindowUtils.OnSetFocus(
        #        int(self.centralWidget().winId()), 0, 0, 0)
        pass

    def closeEvent(self, event):
        self.mainFrame.browser.CloseBrowser()

class MainFrame(QtGui.QX11EmbedContainer):
    browser = None
    plug = None

    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent)
        
        # create X11 window
        gtkPlugPtr = cefpython.WindowUtils.gtk_plug_new(int(self.winId()))

        windowInfo = cefpython.WindowInfo()
        windowInfo.SetAsChild(gtkPlugPtr)
        self.browser = cefpython.CreateBrowserSync(windowInfo,
                                                   browserSettings={},
                                                   navigateUrl="file://"+GetApplicationPath("resources/editor.html"))
        
        cefpython.WindowUtils.gtk_widget_show(gtkPlugPtr)
        self.show()

class CefApplication(QtGui.QApplication):
    timer = None

    def __init__(self, args):
        super(CefApplication, self).__init__(args)
        self.createTimer()

    def createTimer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.onTimer)
        self.timer.start(10)

    def onTimer(self):
        # The proper way of doing message loop should be:
        # 1. In createTimer() call self.timer.start(0)
        # 2. In onTimer() call MessageLoopWork() only when
        #    QtGui.QApplication.instance()->hasPendingEvents()
        #    returns False.
        # But there is a bug in Qt, hasPendingEvents() returns
        # always true.
        # (The behavior described above was tested on Windows
        #  with pyqt 4.8, maybe this is not true anymore,
        #  test it TODO)
        cefpython.MessageLoopWork()

    def stopTimer(self):
        # Stop the timer after Qt message loop ended, calls to
        # MessageLoopWork() should not happen anymore.
        self.timer.stop()

if __name__ == '__main__':

    # Application settings
    settings = {
        "debug": True, # cefpython debug messages in console and in log_file
        "log_severity": cefpython.LOGSEVERITY_INFO, # LOGSEVERITY_VERBOSE
        "log_file": GetApplicationPath("debug.log"), # Set to "" to disable.
        "release_dcheck_enabled": True, # Enable only when debugging.
        # This directories must be set on Linux
        "locales_dir_path": cefpython.GetModuleDirectory()+"/locales",
        "resources_dir_path": cefpython.GetModuleDirectory(),
        "browser_subprocess_path": "%s/%s" % (
            cefpython.GetModuleDirectory(), "subprocess"),
        # This option is required for the GetCookieManager callback
        # to work. It affects renderer processes, when this option
        # is set to True. It will force a separate renderer process
        # for each browser created using CreateBrowserSync.
        "unique_request_context_per_browser": True,
        "remote_debugging_port": 9223
    }

    # Command line switches
    switches = {
    }

    cefpython.Initialize(settings, switches)

    app = CefApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()
    app.stopTimer()

    del mainWindow
    del app

    cefpython.Shutdown()
