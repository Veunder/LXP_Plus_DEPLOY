"""Создаёт таблицы и наполняет базу демо-данными.

Запуск (из папки backend):  python seed.py

Данные подобраны под макет: 24 ноутбука, 6 заняты, из них 2 — у текущего
пользователя фронта (Фудулей М. С.), чтобы карточка "Мои бронирования" = 2.
"""
from datetime import timedelta

from app import create_app
from app.extensions import db
from app.models import (
    Teacher, Classroom, Laptop, Issue, IssueItem,
    STATUS_FREE, STATUS_ISSUED, utcnow,
)

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # ВАЖНО: фронт считает текущим пользователем преподавателя с полным именем
    # "Фудулей Мария Сергеевна" (это зашито в App.vue). Поэтому он обязательно
    # должен быть, иначе "Мои бронирования" не заработают.
    fudulei = Teacher(lname="Фудулей", fname="Мария", mname="Сергеевна", lesson="C#")
    kur1 = Teacher(lname="Высоцкий", fname="Данил", lesson="Куратор")
    kur2 = Teacher(lname="Родионов", fname="Федя", lesson="Куратор")
    kur3 = Teacher(lname="Лисина", fname="Кристина", lesson="Куратор")
    kur4 = Teacher(lname="Пудова", fname="Таня", lesson="Куратор")
    kur5 = Teacher(lname="Лютвайтес", fname="Артем", lesson="Куратор")
    kur6 = Teacher(lname="Снитко", fname="Маша", lesson="Куратор")
    kur7 = Teacher(lname="Тинчурина", fname="Динара", lesson="Куратор")
    kur8 = Teacher(lname="Муругова", fname="Лиза", lesson="Куратор")
    kur9 = Teacher(lname="Жарова", fname="Настя", lesson="Куратор")
    db.session.add_all([fudulei, kur1, kur2, kur3, kur4, kur5, kur6, kur7, kur8, kur9])

    rooms = {name: Classroom(name=name) for name in ("1", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9")}
    db.session.add_all(rooms.values())

    # 24 ноутбука с номерами 1..24, изначально все свободны, состояние "Норма".
    laptops = [Laptop(number=n, status=STATUS_FREE, condition="Норма") for n in range(1, 35)]
    db.session.add_all(laptops)

    db.session.flush()  # проставляем id всем объектам перед созданием выдач

    now = utcnow()

    def make_issue(teacher, room, subject, rows):
        issue = Issue(
            teacher_id=teacher.id, classroom_id=room.id, subject_name=subject,
            created_at=now, expires_at=now + timedelta(days=7),
        )
        db.session.add(issue)
        db.session.flush()
        for laptop, fio, group, condition, mouse, charger in rows:
            db.session.add(IssueItem(
                issue_id=issue.id, laptop_id=laptop.id,
                student_full_name=fio, student_group=group,
                condition=condition, has_mouse=mouse, has_charger=charger,
            ))
            laptop.status = STATUS_ISSUED
            if condition:
                laptop.condition = condition

    make_issue(fudulei, rooms["1.6"], "C#", [
        (laptops[2], "Юдин Максим", "ИСП9-kh24", "Норма", True, True),
        (laptops[8], "Вернигоров Георгий", "ИСП9-kh21", "Норма", True, False),
    ])

    db.session.commit()

    busy = Laptop.query.filter_by(status=STATUS_ISSUED).count()
    print(f"Готово. Преподавателей: 10, аудиторий: {len(rooms)}, "
          f"ноутбуков: {len(laptops)} (занято {busy}, свободно {len(laptops) - busy}).")
