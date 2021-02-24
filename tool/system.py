def get_browser_position(w_scale=1, h_scale=1, screen=1):
    """ 获取浏览器位置
    :param w_scale: 宽度比例
    :param h_scale: 高度比例
    :return: 窗口 win_x, win_y, win_w, win_h
    """

    if screen == "screen_3_main":
        # {'x': 2010, 'y': 297} {'width': 900, 'height': 624}
        return 2010, 297, 900, 624

    screen_x = -5120
    screen_y = 740
    screen_xx = -1707
    screen_yy = 2660
    screen_dpi = 1.5
    screen_w = screen_xx - screen_x
    screen_h = screen_yy - screen_y

    win_w = screen_w * w_scale
    win_h = screen_h * h_scale
    win_x = screen_x + (screen_w - win_w) / 2
    win_y = screen_y + (screen_h - win_h) / 2

    win_x = win_x / screen_dpi
    win_y = win_y / screen_dpi
    win_w = win_w / screen_dpi
    win_h = win_h / screen_dpi

    win_x = round(win_x)
    win_y = round(win_y)
    win_w = round(win_w)
    win_h = round(win_h)

    return win_x, win_y, win_w, win_h
