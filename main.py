import pandas as pd
import random
import uuid
import json
from datetime import datetime, timedelta
from faker import Faker

# Инициализация Faker для генерации фейковых данных
fake = Faker()

# Константы для генерации
PLATFORMS = ['iOS', 'Android']
APP_VERSIONS = ['1.0.0', '1.1.0', '1.2.0']
GOALS = ['Для работы', 'Для путешествий', 'Для учебы', 'Хобби']
LEVELS = ['Beginner', 'Elementary', 'Intermediate', 'Advanced']
COUNTRIES = ['US', 'RU', 'DE', 'FR', 'ES', 'IT', 'BR']
LESSON_TYPES = ['Grammar', 'Vocabulary', 'Speaking']

def generate_data(num_users=1000, days_history=90):
    users_data = []
    events_data = []
    
    now = datetime.utcnow()
    start_date = now - timedelta(days=days_history)

    for _ in range(num_users):
        user_id = str(uuid.uuid4())
        platform = random.choice(PLATFORMS)
        device_model = f"iPhone {random.randint(11, 15)}" if platform == 'iOS' else f"Samsung S{random.randint(21, 24)}"
        app_version = random.choice(APP_VERSIONS)
        country = random.choice(COUNTRIES)
        
        # Случайная дата установки в пределах истории
        install_at = start_date + timedelta(
            days=random.randint(0, days_history - 1),
            minutes=random.randint(0, 1440)
        )
        
        # Данные профиля (заполнятся, если пройдет регистрацию)
        goal = random.choice(GOALS)
        level = random.choice(LEVELS)
        study_time = random.choice([15, 30, 60])
        name = fake.first_name()
        age = random.randint(16, 55)
        is_premium = False 
        
        # --- ГЕНЕРАЦИЯ СОБЫТИЙ ДЛЯ ПОЛЬЗОВАТЕЛЯ ---
        current_time = install_at
        session_id = str(uuid.uuid4())
        
        def add_event(event_name, properties=None):
            nonlocal current_time
            
            current_time += timedelta(seconds=random.randint(2, 15))
            events_data.append({
                "event_id": str(uuid.uuid4()),
                "event_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "user_id": user_id,
                "app_version": app_version,
                "platform": platform,
                "device_model": device_model,
                "country": country,
                "session_id": session_id,
                "event_name": event_name,
                "event_properties": json.dumps(properties or {})
            })

        # 1. Онбординг
        add_event("app_launched", {"is_first_launch": True, "traffic_source": "organic"})
        
        # Вероятность пройти туториал 80%
        if random.random() < 0.8:
            for step in range(1, 4):
                add_event("tutorial_step_viewed", {"step_index": step, "total_steps": 3})
                # Имитация времени на шаге
                current_time += timedelta(seconds=random.randint(5, 20))
                add_event("tutorial_step_completed", {"step_index": step})
            add_event("tutorial_completed", {"total_time_spent": 45})
            
            # 2. Квиз и регистрация (Вероятность 70% от тех, кто прошел туториал)
            if random.random() < 0.7:
                add_event("quiz_started", {"quiz_id": "v1"})
                add_event("quiz_answer_selected", {"question_id": "goal", "answer_text": goal})
                add_event("quiz_answer_selected", {"question_id": "level", "answer_text": level})
                add_event("quiz_completed", {"user_intent": goal, "assigned_level": level})
                
                add_event("registration_started", {"entry_point": "post_quiz"})
                add_event("registration_success", {"registration_method": "email"})
                
                # 3. Уроки и подписка в первые и последующие дни
                days_active = random.randint(1, 14) # Сколько дней юзер заходил
                
                for day in range(days_active):
                    if day > 0:
                        # Новая сессия на следующий день
                        current_time = install_at + timedelta(days=day, minutes=random.randint(0, 100))
                        session_id = str(uuid.uuid4())
                        add_event("app_launched", {"is_first_launch": False, "traffic_source": "direct"})
                    
                    # Проходит 1-3 урока в день
                    for _ in range(random.randint(1, 3)):
                        lesson_id = f"lesson_{random.randint(1, 100)}"
                        l_type = random.choice(LESSON_TYPES)
                        add_event("lesson_started", {"lesson_id": lesson_id, "lesson_type": l_type, "is_premium_content": False})
                        
                        duration = random.randint(60, 300) # 1-5 минут на урок
                        current_time += timedelta(seconds=duration)
                        
                        # 90% что закончит успешно
                        if random.random() < 0.9:
                            score = random.randint(40, 100)
                            add_event("lesson_completed", {"lesson_id": lesson_id, "score_percentage": score, "duration_seconds": duration})
                        else:
                            add_event("lesson_failed", {"lesson_id": lesson_id, "reason": "exit_button"})

                    # 4. Монетизация  30% в любой из дней
                    if not is_premium and random.random() < 0.3:
                        add_event("paywall_viewed", {"source": "lock_icon", "available_plans": ["monthly", "annual"]})
                        
                        # Конверсия в покупку 10% от увидевших
                        if random.random() < 0.1:
                            add_event("purchase_initiated", {"product_id": "sub_annual", "price_local": 49.99})
                            current_time += timedelta(seconds=10)
                            add_event("purchase_success", {"transaction_id": str(uuid.uuid4()), "revenue_usd": 49.99})
                            is_premium = True # Обновляем профиль пользователя!

        # Добавляем пользователя в базу профилей
        users_data.append({
            "user_id": user_id,
            "platform": platform,
            "install_at": install_at.strftime("%Y-%m-%d %H:%M:%S"),
            "app_version": app_version,
            "is_premium": is_premium,
            "goal": goal,
            "onboarding_level": level,
            "plan_on_study_time": study_time,
            "name": name,
            "country": country,
            "age": age
        })

    # Конвертируем в датафрейм
    df_users = pd.DataFrame(users_data)
    df_events = pd.DataFrame(events_data)
    
    return df_users, df_events

if __name__ == "__main__":
    print("Генерация данных запущена. Это займет пару секунд...")
    # Генерируем пользователей
    users, events = generate_data(num_users=10000, days_history=90)
    

    users.to_csv("users.csv", index=False)
    events.to_csv("events.csv", index=False)
    
    print(f"Создано {len(users)} пользователей и {len(events)} событий.")