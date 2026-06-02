import pandas as pd
import random
import uuid
import json
from datetime import datetime, timedelta
from faker import Faker

# Инициализация Faker
fake = Faker()

# Константы для генерации
PLATFORMS = ['iOS', 'Android']
APP_VERSIONS = ['1.0.0', '1.1.1','1.1.2','1.1.3','1.1.4', '1.2.0', '1.2.1']
GOALS = ['Для работы', 'Для путешествий', 'Для учебы', 'Хобби']
LEVELS = ['Beginner', 'Elementary', 'Intermediate', 'Advanced']
COUNTRIES = ['US', 'RU', 'DE', 'FR', 'ES', 'IT', 'BR']
LESSON_TYPES = ['Grammar', 'Vocabulary', 'Speaking']
IOS_DEVICES = [
    'iPhone 11', 'iPhone 12', 'iPhone 13', 'iPhone 13 mini', 
    'iPhone 14', 'iPhone 14 Pro', 'iPhone 15', 'iPhone 15 Pro', 'iPhone 15 Pro Max', 
    'iPhone 16', 'iPhone 16 Pro Max', 'iPhone 17', 'iPhone 17 Pro', 'iPhone 17 Pro Max'
]

ANDROID_DEVICES = [
    'Samsung Galaxy S22', 'Samsung Galaxy S23', 'Samsung Galaxy S24 Ultra', 
    'Samsung Galaxy S25', 'Samsung Galaxy S26 Ultra', 'Samsung Galaxy S24 FE',
    'Samsung Galaxy A54', 'Samsung Galaxy A55', 'Samsung Galaxy A35',
    'Samsung Galaxy Z Flip 6', 'Samsung Galaxy Z Fold 7',

    'Google Pixel 7', 'Google Pixel 8', 'Google Pixel 8a', 
    'Google Pixel 9 Pro', 'Google Pixel 10 XL',

    'Xiaomi 13', 'Xiaomi 14', 'Xiaomi 15', 'Redmi Note 13 Pro', 'Poco F6',

    'OnePlus 11', 'OnePlus 12', 'OnePlus 13', 
    'Nothing Phone (2a)', 'Nothing Phone (3)', 'Motorola Edge 50'
]

def generate_lessons_catalog(num_lessons=100):
    """Генерация справочника контента (уроков)"""
    lessons = []
    for i in range(1, num_lessons + 1):
        lessons.append({
            "lesson_id": f"l_{i}",
            "lesson_name": f"Lesson {i}: {fake.word().capitalize()}",
            "lesson_type": random.choice(LESSON_TYPES),
            "difficulty_level": random.randint(1, 10),
            # Первые 30 уроков бесплатные, остальные - премиум
            "is_premium": 0 if i <= 30 else 1
        })
    return lessons

def generate_data(num_users=10000, days_history=90):
    lessons_catalog = generate_lessons_catalog(100)
    
    users_data = []
    events_data = []
    learning_data = []
    payments_data = []
    
    now = datetime.utcnow()
    start_date = now - timedelta(days=days_history)

    print(f"Начинаем генерацию {num_users} пользователей. Это займет около минуты...")

    for i in range(num_users):
        # Прогресс-бар в консоль, чтобы понимать, что скрипт не завис
        if (i + 1) % 1000 == 0:
            print(f"Сгенерировано {i + 1} / {num_users} пользователей...")

        user_id = str(uuid.uuid4())
        
        current_platform = random.choice(PLATFORMS)
        current_device = random.choice(IOS_DEVICES) if current_platform == 'iOS' else random.choice(ANDROID_DEVICES)
        current_app_version = random.choice(APP_VERSIONS)
        
        country = random.choice(COUNTRIES)
        goal = random.choice(GOALS)
        level = random.choice(LEVELS)
        study_time = random.choice([5, 10, 15, 20, 30, 45, 60, 90, 120])
        name = fake.first_name()
        age = random.randint(16, 55)
        is_premium = 0 
        
        install_at = start_date + timedelta(
            days=random.randint(0, days_history - 1),
            minutes=random.randint(0, 1440)
        )
        
        current_time = install_at
        
        def add_event(event_name, properties=None):
            nonlocal current_time
            current_time += timedelta(seconds=random.randint(2, 15))
            events_data.append({
                "event_id": str(uuid.uuid4()),
                "event_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "user_id": user_id,
                "platform": current_platform,
                "device_model": current_device,
                "app_version": current_app_version,
                "event_name": event_name,
                "event_properties": json.dumps(properties or {})
            })

        # --- ЭТАП 1: Онбординг ---
        add_event("app_launched", {"is_first_launch": True, "traffic_source": "organic"})
        
        if random.random() < 0.8: 
            for step in range(1, 4):
                add_event("tutorial_step_viewed", {"step_index": step, "total_steps": 3})
                current_time += timedelta(seconds=random.randint(5, 20))
                add_event("tutorial_step_completed", {"step_index": step})
            add_event("tutorial_completed", {"total_time_spent": 45})
            
            # --- ЭТАП 2: Квиз и регистрация ---
            if random.random() < 0.7:
                add_event("quiz_started", {"quiz_id": "v1"})
                add_event("quiz_answer_selected", {"question_id": "goal", "answer_text": goal})
                add_event("quiz_completed", {"user_intent": goal, "assigned_level": level})
                add_event("registration_started", {"entry_point": "post_quiz"})
                add_event("registration_success", {"registration_method": "email"})
                
                # --- ЭТАП 3: Обучение ---
                # Увеличим вероятность активности, чтобы набрать больше событий
                days_active = random.randint(1, 20) 
                
                for day in range(days_active):
                    if day > 0:
                        current_time = install_at + timedelta(days=day, minutes=random.randint(0, 100))
                        if random.random() < 0.05:
                            current_app_version = '1.2.0'
                        add_event("app_launched", {"is_first_launch": False, "traffic_source": "direct"})
                    
                    # Проходит 1-4 урока в день
                    for _ in range(random.randint(1, 4)):
                        available_lessons = [l for l in lessons_catalog if l['is_premium'] == 0 or is_premium == 1]
                        lesson = random.choice(available_lessons)
                        
                        add_event("lesson_started", {"lesson_id": lesson['lesson_id']})
                        
                        start_time = current_time
                        duration = random.randint(60, 300)
                        current_time += timedelta(seconds=duration)
                        
                        if random.random() < 0.85: # 85% успешно завершают
                            score = random.randint(40, 100)
                            mistakes = random.randint(0, 5)
                            add_event("lesson_completed", {"lesson_id": lesson['lesson_id']})
                            
                            learning_data.append({
                                "user_id": user_id,
                                "lesson_id": lesson['lesson_id'],
                                "started_at": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                                "completed_at": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                                "status": "completed",
                                "score_percentage": float(score),
                                "time_spent_sec": duration,
                                "mistakes_count": mistakes
                            })
                        else:
                            add_event("lesson_failed", {"lesson_id": lesson['lesson_id'], "reason": "exit_button"})
                            learning_data.append({
                                "user_id": user_id,
                                "lesson_id": lesson['lesson_id'],
                                "started_at": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                                "completed_at": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                                "status": "failed",
                                "score_percentage": 0.0,
                                "time_spent_sec": duration // 2, 
                                "mistakes_count": 0
                            })

                    # --- ЭТАП 4: Монетизация ---
                    if is_premium == 0 and random.random() < 0.3:
                        add_event("paywall_viewed", {"source": "lock_icon"})
                        
                        if random.random() < 0.1: 
                            # Выбираем случайный недорогой тариф
                            plan = random.choice([
                                {"type": "monthly", "price": 299},
                                {"type": "quarterly", "price": 799},
                                {"type": "annual", "price": 1990}
                            ])
                            
                            add_event("purchase_initiated", {"plan_type": plan["type"], "price_rub": plan["price"]})
                            current_time += timedelta(seconds=10)
                            transaction_id = str(uuid.uuid4())
                            add_event("purchase_success", {"transaction_id": transaction_id})
                            
                            payments_data.append({
                                "transaction_id": transaction_id,
                                "user_id": user_id,
                                "event_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                                "plan_type": plan["type"],
                                "revenue_rub": plan["price"]
                            })
                            is_premium = 1

        users_data.append({
            "user_id": user_id,
            "install_time": install_at.strftime("%Y-%m-%d %H:%M:%S"),
            "name": name,
            "age": age,
            "country": country,
            "goal": goal,
            "onboarding_level": level,
            "plan_on_study_time": study_time,
            "is_premium": is_premium
        })

    return (
        pd.DataFrame(users_data),
        pd.DataFrame(lessons_catalog),
        pd.DataFrame(events_data),
        pd.DataFrame(learning_data),
        pd.DataFrame(payments_data)
    )

if __name__ == "__main__":
    print("Запускаем скрипт генерации Data Warehouse...")
    # ТУТ ЗАДАЕМ 10 000
    df_users, df_lessons, df_events, df_learning, df_payments = generate_data(num_users=10000, days_history=90)
    
    print("\nСохраняем файлы на диск")
    df_users.to_csv("dim_users.csv", index=False)
    df_lessons.to_csv("dim_lessons_catalog.csv", index=False)
    df_events.to_csv("raw_events.csv", index=False)
    df_learning.to_csv("fact_learning.csv", index=False)
    df_payments.to_csv("fact_payments.csv", index=False)
    
    print("\nГотово! Итоговая статистика:")
    print(f"Пользователи (dim_users): {len(df_users):,} строк")
    print(f"Уроки (dim_lessons_catalog): {len(df_lessons):,} строк")
    print(f"Сырые логи (raw_events): {len(df_events):,} строк")
    print(f"Факты обучения (fact_learning): {len(df_learning):,} строк")
    print(f"Факты оплат (fact_payments): {len(df_payments):,} строк")