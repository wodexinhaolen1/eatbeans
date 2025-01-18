import random
import cv2
import pygame  # 导入pygame库用于播放音效
import time
from mainGame import create_welcome_screen
from imports import *
from methods import check_collision, draw_bean


def play_sound(sound):
    """播放音效的函数"""
    sound.play()  # 播放音效


def load_high_score():
    """从文件中加载最高分"""
    try:
        with open("high_score.txt", "r") as file:
            return int(file.read())
    except FileNotFoundError:
        return 0  # 如果文件不存在，返回默认最高分0


def save_high_score(score):
    """将最高分保存到文件中"""
    with open("high_score.txt", "w") as file:
        file.write(str(score))


def nose_main():
    # 初始化pygame的音频模块
    pygame.mixer.init()

    # 初始化 MediaPipe 人体姿态计
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils
    # 初始化 MediaPipe 手部检测
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()

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
    recognition_time = 0  # 识别成功的时间
    recognition_duration = 5  # 识别成功后停留的时间

    # 加载最高分
    high_score = load_high_score()

    # 音效文件路径
    start_sound = pygame.mixer.Sound("Start.mp3")
    eat_sound = pygame.mixer.Sound("Fruit.mp3")
    end_sound = pygame.mixer.Sound("Winner.mp3")

    # 预设的多种豆儿位置
    all_bean_positions = [
        [(400, 300), (334, 258), (333, 204), (391, 168), (447, 177), (480, 215), (461, 326), (440, 432), (372, 427),
         (318, 385), (490, 374), (86, 184), (96, 262), (106, 340), (116, 420), (187, 262), (258, 420), (268, 342),
         (278, 264), (288, 184),
         (516, 420), (526, 342), (536, 264), (546, 184), (617, 342), (688, 184), (698, 264), (708, 342), (718, 420)],
        # 其他豆儿位置...
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

        # 显示最高分（在正上方）
        cv2.putText(frame, f"High Score: {high_score}", (screen_width // 2 - 100, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2)

        # 游戏未开始，显示提示信息
        if not game_started:
            cv2.putText(frame, "Show OK gesture to start the game",
                        (screen_width // 4, screen_height - 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (255, 255, 255), 2)

        # 检测到姿势标志，获取胸口的位置并在画面上以圆形标记
        if results_pose.pose_landmarks:
            landmarks = results_pose.pose_landmarks.landmark
            # 获取胸口位置（使用肩膀和臀部的中间点）
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
            right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

            # 计算胸口位置
            chest_x = (left_shoulder.x + right_shoulder.x + left_hip.x + right_hip.x) / 4
            chest_y = (left_shoulder.y + right_shoulder.y + left_hip.y + right_hip.y) / 4

            chest_pos = (int(chest_x * screen_width), int(chest_y * screen_height))
            cv2.circle(frame, chest_pos, 25, (0, 0, 255), -1)

            # 绘制人体的关键节点
            mp_drawing.draw_landmarks(frame, results_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # 手部OK检测
        if results_hands.multi_hand_landmarks:
            for hand_landmarks in results_hands.multi_hand_landmarks:
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                dist = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
                # 检测成功
                if dist < 0.05:
                    if not game_started and recognition_time == 0:
                        recognition_time = time.time()  # 记录识别成功的时间
                        play_sound(start_sound)  # 播放开始音效

        # 识别成功后显示提示信息并等待5秒
        if recognition_time > 0:
            if time.time() - recognition_time < recognition_duration:
                cv2.putText(frame, "Recognition Successful! Starting in...",
                            (screen_width // 2 - 200, screen_height // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                remaining_time = int(recognition_duration - (time.time() - recognition_time))
                cv2.putText(frame, f"{remaining_time}",
                            (screen_width // 2 - 50, screen_height // 2 + 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                # 5秒后开始游戏
                game_started = True
                start_time = time.time()
                bean_positions = random.choice(all_bean_positions)
                recognition_time = 0  # 重置识别时间

        if game_started:
            for bean_pos in bean_positions:
                draw_bean(frame, bean_pos)
            # 检查碰撞
            new_bean_positions = []
            for bean_pos in bean_positions:
                if not check_collision(chest_pos, bean_pos):
                    new_bean_positions.append(bean_pos)
                elif time.time() - start_time <= game_duration:
                    if not check_collision(chest_pos, bean_pos):
                        new_bean_positions.append(bean_pos)
                    else:
                        score += 1
                        play_sound(eat_sound)  # 播放吃豆子音效
            bean_positions = new_bean_positions
            # 显示得分和剩余时间
            cv2.putText(frame, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            remaining_time = max(0, game_duration - (time.time() - start_time))
            cv2.putText(frame, f"Time: {int(remaining_time)}s", (screen_width - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 255), 2)
            # 时间到之后的提示信息
            if time.time() - start_time > game_duration:
                # 更新最高分
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)  # 保存新的最高分

                cv2.putText(frame, "Time's up!", (screen_width // 2 - 50, screen_height // 2), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 2)
                cv2.putText(frame, f"Score: {score}", (screen_width // 2 - 50, screen_height // 2 + 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, "Show OK gesture to restart", (screen_width // 2 - 100, screen_height // 2 + 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                play_sound(end_sound)  # 播放结束音效
                game_started = False
                start_time = 0
                score = 0

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
