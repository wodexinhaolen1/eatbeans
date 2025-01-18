import tkinter as tk
import pygame
from PIL import Image, ImageTk


# 启动游戏的函数
def start_nose_game():
    """启动 60 秒限时挑战游戏"""
    pygame.mixer.music.set_volume(0)  # 设置背景音乐音量为零
    game_root.destroy()  # 销毁欢迎页面窗口

    try:
        from noseGame import nose_main
        nose_main()
    except Exception as e:
        print(f"An error occurred in Nose Game: {e}")
        with open("error.log", "a") as f:
            f.write(f"Nose Game: {e}\n")


def start_plane_game():
    """启动 飞机大战游戏"""
    pygame.mixer.music.set_volume(0)  # 设置背景音乐音量为零
    game_root.destroy()  # 销毁欢迎页面窗口
    try:
        from beanFallingGame import bean_falling_main
        bean_falling_main()
    except Exception as e:
        print(f"An error occurred in Plane Game: {e}")
        with open("error.log", "a") as f:
            f.write(f"Plane Game: {e}\n")


def start_third_game():
    """启动 第三个游戏"""
    pygame.mixer.music.set_volume(0)  # 设置背景音乐音量为零
    game_root.destroy()  # 销毁欢迎页面窗口
    try:
        from allGame import nose_main
        nose_main()
    except Exception as e:
        print(f"An error occurred in Third Game: {e}")
        with open("error.log", "a") as f:
            f.write(f"Third Game: {e}\n")


# 创建欢迎界面
def create_welcome_screen():
    global game_root
    game_root = tk.Tk()
    game_root.title("豆你玩儿")

    # 设置窗口大小
    game_root.geometry("800x600")

    # 添加背景音乐
    pygame.mixer.init()
    pygame.mixer.music.load("backmusic.mp3")
    pygame.mixer.music.play(-1)

    # 添加背景图片
    background_image = Image.open("backimage.jpg")
    background_image = background_image.resize((800, 600), Image.LANCZOS)
    background_image = ImageTk.PhotoImage(background_image)
    background_label = tk.Label(game_root, image=background_image)
    background_label.place(relwidth=1, relheight=1)

    # 添加一个空标签以增加间距
    spacer = tk.Label(game_root, text="", bg='blue')
    spacer.pack(pady=(80, 0))

    # 按钮
    btn_nose_game = tk.Button(game_root, text="模式1: 头部限时挑战", command=start_nose_game, width=30, height=2)
    btn_nose_game.pack(pady=10)

    btn_plane_game = tk.Button(game_root, text="模式2: 下落挑战", command=start_plane_game, width=30, height=2)
    btn_plane_game.pack(pady=10)

    btn_third_game = tk.Button(game_root, text="模式3: 全身限时挑战", command=start_third_game, width=30, height=2)
    btn_third_game.pack(pady=10)

    # 添加返回菜单的提示
    return_hint = tk.Label(game_root, text="进入游戏后,按下 'R' 键可以返回菜单", font=("Arial", 8), bg='lightblue', fg='black', highlightthickness=0)
    return_hint.pack(pady=20)

    # 按下 'R' 键的事件
    game_root.bind('<r>', lambda event: restart())

    game_root.mainloop()


def restart():
    """重新启动欢迎界面"""
    pygame.mixer.music.stop()  # 停止背景音乐
    game_root.destroy()  # 销毁当前窗口
    create_welcome_screen()  # 重新创建欢迎界面


if __name__ == "__main__":
    create_welcome_screen()
