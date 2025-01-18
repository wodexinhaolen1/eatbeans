from imports import *


def check_collision(shape_pos, bean_pos, radius=35) -> bool:
    """
    检查图案和豆儿是否发生碰撞
    :param shape_pos: 图案的位置
    :param bean_pos: 豆儿的位置
    :param radius: 适当大小，表示可被接受的范围
    :return: 如果碰撞返回 True，否则返回 False
    """
    dx = shape_pos[0] - bean_pos[0]
    dy = shape_pos[1] - bean_pos[1]
    distance = (dx ** 2 + dy ** 2) ** 0.5
    if distance < radius:
        return True
    return False


def draw_bean(frame, bean_pos, size=15):
    """
    绘制圆形豆儿
    :param frame: 图像帧
    :param bean_pos: 豆儿的位置 (x, y)
    :param size: 豆儿的大小
    """
    x, y = bean_pos
    cv2.circle(frame, (x, y), size, (0, 255, 255), -1)
