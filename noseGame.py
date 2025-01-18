import cv2
import mediapipe as mp
import random
import time
import pygame
from imports import *
from methods import check_collision, draw_bean
from mainGame import create_welcome_screen  # 确保导入返回菜单的函数


def nose_main():
    # 初始化 MediaPipe 人体姿态计
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils

    # 初始化 MediaPipe 手部检测
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()

    # 初始化 pygame 音频模块
    pygame.mixer.init()
    # 加载音频文件
    start_sound = pygame.mixer.Sound("Start.mp3")
    fruit_sound = pygame.mixer.Sound("Fruit.mp3")
    winner_sound = pygame.mixer.Sound("Winner.mp3")
    winner_sound_played = False  # 标记是否已经播放过胜利音效

    # 打开摄像头
    cap = cv2.VideoCapture(0)
    # 设置屏幕宽度和高度
    screen_width = 800
    screen_height = 600

    # 初始化分数、游戏开始时间、游戏时长和游戏是否开始
    score = 0
    start_time = 0
    game_duration = 60
    game_started = False

    # 预设的多种豆儿位置
    all_bean_positions = [
        # 双箭头
        [(150, 300), (200, 300), (250, 300), (300, 300), (350, 300), (400, 300), (450, 300), (500, 300), (550, 300),
         (600, 300), (650, 300), (200, 250), (200, 350), (250, 200), (250, 400), (600, 250), (600, 350), (550, 200),
         (550, 400)],
        # 空心菱
        [(250, 250), (200, 300), (250, 300), (300, 300), (150, 350), (200, 350), (300, 350), (350, 350), (200, 400),
         (250, 400), (300, 400), (250, 450)],
        # 心形
        [(400, 300), (450, 300), (500, 300), (550, 300), (600, 300),
         (400, 350), (450, 350), (500, 350), (550, 350), (600, 350),
         (450, 400), (500, 400), (550, 400), (450, 250), (500, 450), (550, 250)],
        # 长方形
        [(100, 200), (150, 200), (200, 200), (250, 200), (300, 200), (350, 200), (400, 200), (450, 200),
         (100, 250), (150, 250), (200, 250), (250, 250), (300, 250), (350, 250), (400, 250), (450, 250),
         (100, 300), (150, 300), (200, 300), (250, 300), (300, 300), (350, 300), (400, 300), (450, 300),
         (100, 350), (150, 350), (200, 350), (250, 350), (300, 350), (350, 350), (400, 350), (450, 350)],
        # 三角形
        [(450, 200), (450, 250), (450, 300), (450, 350), (450, 400), (450, 450), (450, 500),
         (500, 250), (500, 300), (500, 350), (500, 400), (500, 450), (500, 500),
         (550, 300), (550, 350), (550, 400), (550, 450), (550, 500),
         (600, 350), (600, 400), (600, 450), (600, 500),
         (650, 400), (650, 450), (650, 500),
         (700, 450), (700, 500),
         (750, 500)],
        # wsm
        [(400, 300), (334, 258), (333, 204), (391, 168), (447, 177), (480, 215), (461, 326), (440, 432), (372, 427),
         (318, 385), (490, 374), (86, 184), (96, 262), (106, 340), (116, 420), (187, 262), (258, 420), (268, 342),
         (278, 264), (288, 184),
         (516, 420), (526, 342), (536, 264), (546, 184), (617, 342), (688, 184), (698, 264), (708, 342), (718, 420)],
        # 很棒的一条横线
        [(100, 300), (150, 300), (200, 300), (250, 300), (300, 300), (350, 300), (400, 300), (450, 300), (500, 300),
         (550, 300), (600, 300), (650, 300), (700, 300)],
        # 很棒的一条直线，竖的
        [(300, 150), (300, 200), (300, 250), (300, 300), (300, 350), (300, 400), (300, 450), (300, 500), (300, 550)],
        # zjy
        [(100, 170), (155, 170), (211, 170), (266, 170), (211, 256), (155, 342), (100, 428), (155, 428), (211, 428),
         (266, 428),
         (331, 384), (364, 416), (408, 436), (460, 412), (482, 367), (482, 302), (482, 235), (482, 170),
         (560, 170), (726, 170), (643, 270), (643, 349), (643, 428)],
        # lj
        [(200, 170), (200, 256), (200, 342), (200, 428), (283, 428), (366, 428),
         (431, 384), (464, 416), (508, 436), (560, 412), (582, 367), (582, 302), (582, 235), (582, 170)],
        # ml
        [(166, 420), (176, 342), (186, 264), (196, 184), (267, 342), (338, 184), (348, 264), (358, 342), (368, 420),
         (450, 170), (450, 256), (450, 342), (450, 428), (533, 428), (616, 428)],
        # lsf
        [(100, 170), (100, 256), (100, 342), (100, 428), (183, 428), (266, 428), (400, 300), (334, 258), (333, 204),
         (391, 168), (447, 177), (480, 215), (461, 326), (440, 432), (372, 427), (318, 385), (490, 374), (560, 170),
         (560, 270), (560, 342),
         (560, 428), (643, 170), (643, 270), (726, 170), (726, 270)],
        # 随便的三个点
        [(250, 250), (350, 350), (450, 450)]
    ]
    bean_positions = []

    # 游戏循环
    while cap.isOpened():
        # 读取一帧图像
        ret, frame = cap.read()
        if not ret:
            continue
        # 调整为指定的大小
        frame = cv2.resize(frame, (screen_width, screen_height))
        # 水平翻转
        frame = cv2.flip(frame, 1)
        # 将帧图像的颜色空间从BGR转换为RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # 姿势检测处理和手部检测处理
        results_pose = pose.process(rgb_frame)
        results_hands = hands.process(rgb_frame)

        # 游戏未开始，显示提示信息
        if not game_started:
            cv2.putText(frame, "Show OK gesture to start the game",
                        (screen_width // 4, screen_height - 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (255, 255, 255), 2)

        # 检测到姿势标志，获取鼻子的位置并在画面上以圆形标记
        if results_pose.pose_landmarks:
            landmarks = results_pose.pose_landmarks.landmark
            shape_pos = (int(landmarks[mp_pose.PoseLandmark.NOSE.value].x * screen_width),
                         int(landmarks[mp_pose.PoseLandmark.NOSE.value].y * screen_height))
            cv2.circle(frame, shape_pos, 25, (0, 0, 255), -1)

        # 手部OK检测
        if results_hands.multi_hand_landmarks:
            for hand_landmarks in results_hands.multi_hand_landmarks:
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                dist = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
                # 检测成功
                if dist < 0.05:
                    if not game_started:
                        game_started = True
                        winner_sound_played = False  # 胜利音效重新标记为否
                        # 开始
                        start_time = time.time()
                        # 随机选择一组豆儿位置
                        bean_positions = all_bean_positions[0]
                        # 播放开始音效
                        start_sound.play()
                    elif time.time() - start_time > game_duration:
                        # 游戏结束，重新开始逻辑
                        game_started = False
                        start_time = 0
                        score = 0

        if game_started:
            for bean_pos in bean_positions:
                draw_bean(frame, bean_pos)
            # 检查碰撞
            new_bean_positions = []
            for bean_pos in bean_positions:
                if not check_collision(shape_pos, bean_pos):
                    new_bean_positions.append(bean_pos)
                elif time.time() - start_time <= game_duration:
                    if not check_collision(shape_pos, bean_pos):
                        new_bean_positions.append(bean_pos)
                    else:
                        score += 1
                        # 播放吃到豆子的音效
                        fruit_sound.play()
            bean_positions = new_bean_positions
            # 显示得分和剩余时间
            cv2.putText(frame, f"Score: {score}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            remaining_time = max(0, game_duration - (time.time() - start_time))
            cv2.putText(frame, f"Time: {int(remaining_time)}s", (screen_width - 170, 40), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 255), 2)
            # 时间到之后的提示信息
            if time.time() - start_time > game_duration:
                cv2.putText(frame, "Time's up!", (screen_width // 2 - 90, screen_height // 2), cv2.FONT_HERSHEY_SIMPLEX,
                            1.2, (0, 0, 255), 2)
                cv2.putText(frame, f"Score: {score}", (screen_width // 2 - 65, screen_height // 2 + 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, "Show OK gesture to restart", (screen_width // 2 - 150, screen_height // 2 + 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                if not winner_sound_played:  # 胜利音效仅播放一遍
                    # 播放时间到的音效
                    winner_sound.play()
                    winner_sound_played = True
            # 当豆儿全部消失后，重新随机选择一组豆儿位置
            if len(bean_positions) == 0:
                bean_positions = random.choice(all_bean_positions)

        cv2.imshow('Game', frame)

        # 检测按键输入
        key = cv2.waitKey(1) & 0xFF
        if key == ord('r'):  # 按 'R' 返回菜单
            cap.release()
            cv2.destroyAllWindows()
            pygame.mixer.music.set_volume(1)  # 恢复音乐音量
            create_welcome_screen()  # 返回欢迎界面
            break
        elif key == 27:  # 使用 Esc 键退出
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    nose_main()
