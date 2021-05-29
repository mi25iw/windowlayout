import psutil

import win32con

import win32gui

import win32process


class Window:

    ORDER_FRONT = "front"
    ORDER_BACK = "back"
    ORDER_ALWAYS_FRONT = "always_front"

    @classmethod
    def get_foreground(cls):
        return cls(win32gui.GetForegroundWindow())

    @classmethod
    def get_all(cls):
        windows = []
        win32gui.EnumWindows(
            lambda x, w: w.append(cls(x)),
            windows,
        )
        return windows

    @classmethod
    def get_visible(cls):
        return [w for w in cls.get_all() if w.visible]

    def __init__(self, handle):
        self._handle = handle

    def __eq__(self, other):
        return self._handle == getattr(other, "_handle", None)

    @classmethod
    def get_from_pid(cls, pid):
        for w in cls.get_all():
            if w.process.pid == pid:
                return w

    @property
    def title(self):
        return win32gui.GetWindowText(self._handle)

    @property
    def wclass(self):
        return win32gui.GetClassName(self._handle)

    @property
    def visible(self):
        return (
            win32gui.IsWindowVisible(self._handle)
            and
            self.rect != (0, 0, 0, 0)
        )

    @property
    def rect(self):  # left top right bottom
        return win32gui.GetWindowRect(self._handle)

    @rect.setter
    def rect(self, rect):
        xy_pos = rect[:2]
        xy_size = rect[2] - rect[0], rect[3] - rect[1]
        self.set_location(xy_pos, xy_size)

    @property
    def process(self) -> psutil.Process:
        _, pid = win32process.GetWindowThreadProcessId(self._handle)
        return psutil.Process(pid)

    @property
    def child_windows(self):
        windows = []
        win32gui.EnumChildWindows(
            self._handle,
            lambda x, w: w.append(x),
            windows,
        )

        return windows

    def minimize(self):
        win32gui.ShowWindow(self._handle, win32con.SW_MINIMIZE)

    def maximize(self):
        win32gui.ShowWindow(self._handle, win32con.SW_MAXIMIZE)

    def normalize(self):
        win32gui.ShowWindow(self._handle, win32con.SW_SHOWNORMAL)

    def show(self):
        win32gui.ShowWindow(self._handle, win32con.SW_SHOW)

    def hide(self):
        win32gui.ShowWindow(self._handle, win32con.SW_HIDE)

    def set_location(
        self,
        xy_pos=None,
        xy_size=None,
        order=None,
        show=True,
    ):
        flags = 0

        if xy_pos is None:
            flags |= win32con.SWP_NOMOVE
            x = 0
            y = 0
        else:
            x = xy_pos[0]
            y = xy_pos[1]

        if xy_size is None:
            flags |= win32con.SWP_NOSIZE
            cx = 0
            cy = 0
        else:
            cx = xy_size[0]
            cy = xy_size[1]

        if order is None:
            flags |= win32con.SWP_NOZORDER
            insert_after = 0
        else:
            insert_after = {
                Window.ORDER_FRONT: win32con.HWND_TOP,
                Window.ORDER_ALWAYS_FRONT: win32con.HWND_TOPMOST,
                Window.ORDER_BACK: win32con.HWND_BOTTOM,
            }[order]

        if show is None:
            flags |= win32con.SWP_NOACTIVATE
        elif show:
            flags |= win32con.SWP_SHOWWINDOW
        else:
            flags |= win32con.SWP_HIDEWINDOW

        win32gui.ShowWindow(self._handle, win32con.SW_NORMAL)
        win32gui.SetWindowPos(self._handle, insert_after, x, y, cx, cy, flags)
