import cv2
import mediapipe as mp
import random
import time
import pygame
from methods import check_collision, draw_bean  # 假设这两个方法已定义
from mainGame import create_welcome_screen  # 确保导入返回菜单的函数

screen_height = 600

class Bean:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.active = False

    def reset(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.active = True

    def update(self):
        if self.active:
            self.y += self.speed
            if self.y > screen_height:
                self.active = False
                return True  # 豆子到达底部，游戏失败
        return False

    def draw(self, frame):
        if self.active:
            draw_bean(frame, (self.x, self.y))

def bean_falling_main():
    pygame.init()  # 初始化pygame
    bean_sound = pygame.mixer.Sound('Fruit.mp3')  # 豆子消除音效
    start_sound = pygame.mixer.Sound('Start.mp3')  # 开始游戏音效
    end_sound = pygame.mixer.Sound('Winner.mp3')  # 结束游戏音效

    mp_pose = mp.solutions.pose
    mp_hands = mp.solutions.hands
    pose = mp_pose.Pose()
    hands = mp_hands.Hands()
    cap = cv2.VideoCapture(0)  # 确保使用正确的摄像头索引

    screen_width = 800
    screen_height = 600
    score = 0
    high_score = 0
    game_started = False
    bean_speed = 5
    initial_bean_spawn_rate = 2  # 初始豆子生成概率
    bean_spawn_rate_increase_rate = 0.05  # 随时间增加的概率

    bean_pool = [Bean(0, 0, bean_speed) for _ in range(100)]
    active_beans = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (screen_width, screen_height))
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results_pose = pose.process(rgb_frame)
        results_hands = hands.process(rgb_frame)

        if not game_started:
            cv2.putText(frame, "Show OK gesture to start the game", (screen_width // 4, screen_height - 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        if results_pose.pose_landmarks:
            landmarks = results_pose.pose_landmarks.landmark
            shape_pos = (int(landmarks[mp_pose.PoseLandmark.NOSE.value].x * screen_width),
                         int(landmarks[mp_pose.PoseLandmark.NOSE.value].y * screen_height))
            cv2.circle(frame, shape_pos, 25, (0, 0, 255), -1)

        if results_hands.multi_hand_landmarks:
            for hand_landmarks in results_hands.multi_hand_landmarks:
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

                # 计算拇指和食指指尖的距离
                dist_thumb_index = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
                # 计算其他手指指尖与手掌中心的距离
                dist_middle = ((middle_tip.x - hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x) ** 2 + (middle_tip.y - hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y) ** 2) ** 0.5
                dist_ring = ((ring_tip.x - hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x) ** 2 + (ring_tip.y - hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y) ** 2) ** 0.5
                dist_pinky = ((pinky_tip.x - hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x) ** 2 + (pinky_tip.y - hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y) ** 2) ** 0.5

                # 判断是否为OK手势
                if dist_thumb_index < 0.05 and dist_middle > 0.1 and dist_ring > 0.1 and dist_pinky > 0.1:
                    if not game_started:
                        game_started = True
                        start_time = time.time()
                        score = 0
                        for bean in bean_pool:
                            bean.active = False
                        active_beans.clear()
                        pygame.mixer.Sound.play(start_sound)  # 播放开始游戏音效

        if game_started:
            for bean in active_beans:
                if bean.update():  # 检查豆子是否到达底部
                    pygame.mixer.Sound.play(end_sound)  # 播放结束游戏音效
                    game_started = False
                    cv2.putText(frame, "Game Over!", (screen_width // 2 - 50, screen_height // 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.putText(frame, f"Score: {score}", (screen_width // 2 - 50, screen_height // 2 + 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    cv2.imshow('Game', frame)
                    cv2.waitKey(2000)
                    score = 0
                    active_beans.clear()
                    break

            if game_started:
                elapsed_time = time.time() - start_time

                # 增加豆子生成概率
                bean_spawn_chance = initial_bean_spawn_rate + (bean_spawn_rate_increase_rate * elapsed_time)
                if random.randint(0, 100) < bean_spawn_chance:
                    for bean in bean_pool:
                        if not bean.active:
                            bean.reset(random.randint(0, screen_width), 0, bean_speed)
                            active_beans.append(bean)
                            break

                for bean in active_beans:
                    bean.draw(frame)

                active_beans = [bean for bean in active_beans if bean.active]

                for bean in active_beans:
                    if check_collision(shape_pos, (bean.x, bean.y)):
                        score += 1
                        bean.active = False
                        pygame.mixer.Sound.play(bean_sound)  # 播放豆子消除音效

                cv2.putText(frame, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

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
    pygame.quit()  # 退出pygame

if __name__ == "__main__":
    bean_falling_main()
