def get_browser_position(w, h):
    """ 获取浏览器位置
    :param w: 宽度比例
    :param h: 高度比例
    :return: 窗口 x,y,w,h
    """
    screen_x = 0
    screen_y = 0
    screen_xx = 3840
    screen_yy = 2160
    screen_w = screen_xx - screen_x
    screen_h = screen_yy - screen_y
    screen_dpi = 2

    win_w = screen_w * w
    win_h = screen_h * h
    win_x = screen_x + (screen_w - win_w) / 2
    win_y = screen_y + (screen_h - win_h) / 2

    win_x = win_x / screen_dpi
    win_y = win_y / screen_dpi
    win_w = win_w / screen_dpi
    win_h = win_h / screen_dpi

    win_x = int(win_x)
    win_y = int(win_y)
    win_w = int(win_w)
    win_h = int(win_h)
    return win_x, win_y, win_w, win_h
