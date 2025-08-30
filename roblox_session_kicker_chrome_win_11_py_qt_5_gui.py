import flet as ft
import json
import os
from datetime import datetime
import hashlib
import random

# Файлы для хранения данных
ACCOUNTS_FILE = "accounts.json"
USERS_FILE = "users.json"
SUPPORT_FILE = "support_requests.json"

class DataManager:
    @staticmethod
    def load_json(filename, default):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default
    
    @staticmethod
    def save_json(filename, data):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

class Account:
    def __init__(self, name, status="Bronze", avatar="👤", login_data="", points=0):
        self.name = name
        self.status = status
        self.avatar = avatar
        self.login_data = login_data
        self.points = points
    
    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "avatar": self.avatar,
            "login_data": self.login_data,
            "points": self.points
        }

def main(page: ft.Page):
    page.title = "RentMyWaifu"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0a0a0a"
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    
    # Состояние приложения
    current_user = {"username": None, "is_admin": False, "points": 0, "status": "Bronze"}
    accounts = DataManager.load_json(ACCOUNTS_FILE, [])
    users = DataManager.load_json(USERS_FILE, {
        "RentMyWaifu": {
            "password": hashlib.md5("YTREWQ".encode()).hexdigest(),
            "is_admin": True,
            "points": 9999,
            "status": "Ultimate"
        }
    })
    
    # Анимации
    def animate_hover(e):
        if e.data == "true":
            e.control.scale = 1.05
            e.control.elevation = 10
        else:
            e.control.scale = 1.0
            e.control.elevation = 5
        e.control.update()
    
    def animate_click(e):
        e.control.scale = 0.95
        page.update()
        import time
        time.sleep(0.1)
        e.control.scale = 1.0
        page.update()
    
    # Компонент для карточки аккаунта
    def create_account_card(acc, editable=False):
        status_colors = {
            "Bronze": "#CD7F32",
            "Silver": "#C0C0C0",
            "Gold": "#FFD700",
            "Ultimate": "#B444FF"
        }
        
        status_dropdown = ft.Dropdown(
            value=acc.get("status", "Bronze"),
            options=[
                ft.dropdown.Option("Bronze"),
                ft.dropdown.Option("Silver"),
                ft.dropdown.Option("Gold"),
                ft.dropdown.Option("Ultimate"),
            ],
            width=120,
            visible=editable and current_user["is_admin"],
            on_change=lambda e: update_account_status(acc["name"], e.control.value)
        )
        
        avatar_field = ft.TextField(
            value=acc.get("avatar", "👤"),
            width=60,
            visible=editable and current_user["is_admin"],
            on_change=lambda e: update_account_avatar(acc["name"], e.control.value)
        )
        
        card = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text(acc.get("avatar", "👤"), size=40) if not editable or not current_user["is_admin"] else avatar_field,
                    alignment=ft.alignment.center,
                    width=80,
                    height=80,
                    bgcolor=status_colors.get(acc.get("status", "Bronze")),
                    border_radius=40,
                ),
                ft.Text(acc.get("name", "Unknown"), size=16, weight=ft.FontWeight.BOLD),
                status_dropdown if editable and current_user["is_admin"] else ft.Container(
                    content=ft.Text(acc.get("status", "Bronze"), color="white", size=12),
                    bgcolor=status_colors.get(acc.get("status", "Bronze")),
                    padding=5,
                    border_radius=5,
                ),
                ft.Text(f"Баллы: {acc.get('points', 0)}", size=12, color="#888"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            width=200,
            height=250,
            padding=20,
            bgcolor="#1a1a1a",
            border_radius=15,
            elevation=5,
            animate_scale=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
            on_hover=animate_hover,
        )
        
        return card
    
    def update_account_status(name, new_status):
        nonlocal accounts
        for acc in accounts:
            if acc["name"] == name:
                acc["status"] = new_status
                break
        DataManager.save_json(ACCOUNTS_FILE, accounts)
        show_accounts_section()
    
    def update_account_avatar(name, new_avatar):
        nonlocal accounts
        for acc in accounts:
            if acc["name"] == name:
                acc["avatar"] = new_avatar
                break
        DataManager.save_json(ACCOUNTS_FILE, accounts)
        show_accounts_section()
    
    # Навигационная панель
    def create_nav_bar():
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text("🎮 RentMyWaifu", size=24, weight=ft.FontWeight.BOLD),
                    on_click=lambda _: show_home(),
                ),
                ft.Row([
                    ft.TextButton("Главная", on_click=lambda _: show_home()),
                    ft.TextButton("Аккаунты", on_click=lambda _: show_accounts_section()),
                    ft.TextButton("Превосходство", on_click=lambda _: show_superiority()),
                    ft.TextButton("FAQ", on_click=lambda _: show_faq()),
                    ft.TextButton("Поддержка", on_click=lambda _: show_support()),
                    ft.TextButton("Гаранты", on_click=lambda _: show_guarantors()),
                ]),
                ft.Row([
                    ft.Text(f"👤 {current_user['username']}" if current_user['username'] else "", visible=current_user['username'] is not None),
                    ft.Text(f"💎 {current_user['points']}" if current_user['username'] else "", visible=current_user['username'] is not None),
                    ft.ElevatedButton(
                        "Админ-панель" if current_user["is_admin"] else "Личный кабинет",
                        on_click=lambda _: show_admin_panel() if current_user["is_admin"] else show_profile(),
                        visible=current_user['username'] is not None,
                        bgcolor="#B444FF" if current_user["is_admin"] else "#2196F3",
                    ),
                    ft.ElevatedButton(
                        "Выход" if current_user['username'] else "Вход",
                        on_click=lambda _: logout() if current_user['username'] else show_login(),
                        bgcolor="#FF4444" if current_user['username'] else "#4CAF50",
                    ),
                ]),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor="#1a1a1a",
            padding=20,
            border_radius=0,
        )
    
    # Главная страница
    def show_home():
        content.controls.clear()
        
        hero = ft.Container(
            content=ft.Column([
                ft.Text("🎮 RentMyWaifu", size=60, weight=ft.FontWeight.BOLD,
                       animate_opacity=ft.animation.Animation(1000, ft.AnimationCurve.EASE_IN)),
                ft.Text("Премиум аккаунты для игр", size=24, color="#888"),
                ft.Row([
                    ft.ElevatedButton("Начать сейчас", bgcolor="#B444FF", color="white",
                                    on_click=lambda _: show_accounts_section()),
                    ft.OutlinedButton("Узнать больше", on_click=lambda _: show_superiority()),
                ], alignment=ft.MainAxisAlignment.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
            padding=100,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=["#1a1a1a", "#2a2a2a"],
            ),
            border_radius=20,
            margin=20,
        )
        
        features = ft.Row([
            create_feature_card("🚀", "Быстрый доступ", "Мгновенный доступ к премиум аккаунтам"),
            create_feature_card("🔒", "Безопасность", "Полная защита ваших данных"),
            create_feature_card("💎", "Качество", "Только проверенные аккаунты"),
            create_feature_card("🎯", "Поддержка", "24/7 техническая поддержка"),
        ], wrap=True, alignment=ft.MainAxisAlignment.CENTER)
        
        content.controls.extend([hero, features])
        page.update()
    
    def create_feature_card(icon, title, desc):
        return ft.Container(
            content=ft.Column([
                ft.Text(icon, size=40),
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
                ft.Text(desc, size=14, color="#888", text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            width=250,
            padding=30,
            bgcolor="#1a1a1a",
            border_radius=15,
            elevation=5,
            margin=10,
            animate_scale=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
            on_hover=animate_hover,
        )
    
    # Раздел аккаунтов
    def show_accounts_section():
        content.controls.clear()
        
        title = ft.Text("🎮 Доступные аккаунты", size=32, weight=ft.FontWeight.BOLD)
        
        if not accounts:
            accounts_grid = ft.Text("Нет доступных аккаунтов", size=20, color="#888")
        else:
            accounts_grid = ft.Row(
                [create_account_card(acc, editable=current_user["is_admin"]) for acc in accounts],
                wrap=True,
                alignment=ft.MainAxisAlignment.CENTER,
            )
        
        add_btn = ft.ElevatedButton(
            "➕ Добавить аккаунт",
            on_click=lambda _: show_add_account_dialog(),
            bgcolor="#4CAF50",
            visible=current_user["is_admin"],
        )
        
        content.controls.extend([title, accounts_grid, add_btn])
        page.update()
    
    def show_add_account_dialog():
        name_field = ft.TextField(label="Имя аккаунта", autofocus=True)
        status_field = ft.Dropdown(
            label="Статус",
            options=[
                ft.dropdown.Option("Bronze"),
                ft.dropdown.Option("Silver"),
                ft.dropdown.Option("Gold"),
                ft.dropdown.Option("Ultimate"),
            ],
            value="Bronze",
        )
        avatar_field = ft.TextField(label="Аватар (эмодзи)", value="👤")
        points_field = ft.TextField(label="Баллы", value="0", keyboard_type=ft.KeyboardType.NUMBER)
        
        def add_account(e):
            nonlocal accounts
            new_acc = {
                "name": name_field.value,
                "status": status_field.value,
                "avatar": avatar_field.value,
                "points": int(points_field.value or 0),
            }
            accounts.append(new_acc)
            DataManager.save_json(ACCOUNTS_FILE, accounts)
            dialog.open = False
            show_accounts_section()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Добавить новый аккаунт"),
            content=ft.Column([name_field, status_field, avatar_field, points_field], spacing=10),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
                ft.ElevatedButton("Добавить", on_click=add_account),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    # Раздел "Абсолютное превосходство"
    def show_superiority():
        content.controls.clear()
        
        title = ft.Container(
            content=ft.Text("⚡ Абсолютное превосходство", size=40, weight=ft.FontWeight.BOLD),
            gradient=ft.LinearGradient(
                colors=["#B444FF", "#FFD700"],
            ),
            padding=20,
        )
        
        benefits = [
            ("🚀", "Мгновенный доступ", "Получите доступ к аккаунту сразу после оплаты"),
            ("💎", "Премиум качество", "Только проверенные аккаунты высшего уровня"),
            ("🔒", "100% Безопасность", "Полная защита ваших данных и транзакций"),
            ("🎯", "Эксклюзивные бонусы", "Доступ к уникальным предложениям и скидкам"),
            ("⚡", "Приоритетная поддержка", "Ответ в течение 5 минут"),
            ("🎮", "Широкий выбор", "Более 1000+ аккаунтов различных игр"),
            ("💰", "Выгодные цены", "Лучшие цены на рынке"),
            ("🔄", "Гарантия замены", "Замена аккаунта в случае проблем"),
        ]
        
        benefits_grid = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Text(icon, size=50),
                    ft.Column([
                        ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(desc, size=14, color="#888"),
                    ], spacing=5),
                ], spacing=20),
                padding=20,
                bgcolor="#1a1a1a",
                border_radius=10,
                margin=ft.margin.only(bottom=10),
                animate_scale=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
                on_hover=animate_hover,
            ) for icon, title, desc in benefits
        ])
        
        content.controls.extend([title, benefits_grid])
        page.update()
    
    # FAQ
    def show_faq():
        content.controls.clear()
        
        title = ft.Text("❓ Часто задаваемые вопросы", size=32, weight=ft.FontWeight.BOLD)
        
        faq_items = [
            ("Как начать пользоваться сервисом?", "Зарегистрируйтесь, выберите нужный аккаунт и оплатите доступ."),
            ("Какие гарантии вы предоставляете?", "Мы гарантируем работоспособность всех аккаунтов и предоставляем замену в случае проблем."),
            ("Как связаться с поддержкой?", "Используйте форму обратной связи или напишите гарантам в личные сообщения."),
            ("Какие способы оплаты доступны?", "Мы принимаем все популярные способы оплаты. Детали уточняйте у гарантов."),
        ]
        
        faq_list = ft.Column([
            ft.ExpansionTile(
                title=ft.Text(question, size=16, weight=ft.FontWeight.BOLD),
                subtitle=ft.Text("Нажмите для ответа", color="#888"),
                controls=[ft.Container(
                    content=ft.Text(answer, size=14),
                    padding=20,
                    bgcolor="#1a1a1a",
                    border_radius=10,
                )],
            ) for question, answer in faq_items
        ])
        
        content.controls.extend([title, faq_list])
        page.update()
    
    # Поддержка
    def show_support():
        content.controls.clear()
        
        title = ft.Text("📧 Техническая поддержка", size=32, weight=ft.FontWeight.BOLD)
        
        info = ft.Container(
            content=ft.Column([
                ft.Text("⚠️ ВАЖНО:", size=18, weight=ft.FontWeight.BOLD, color="#FF4444"),
                ft.Text("• По вопросам оплаты обращайтесь к гарантам в личные сообщения", size=14),
                ft.Text("• Форма только для технических вопросов", size=14),
                ft.Text("• Исключение: проблемы с долгим ответом в чате", size=14),
            ]),
            bgcolor="#1a1a1a",
            padding=20,
            border_radius=10,
            margin=20,
        )
        
        email_field = ft.TextField(
            label="Email для связи *",
            hint_text="your@email.com",
            required=True,
            width=400,
        )
        
        subject_field = ft.TextField(
            label="Тема обращения",
            hint_text="Кратко опишите проблему",
            width=400,
        )
        
        message_field = ft.TextField(
            label="Сообщение",
            multiline=True,
            min_lines=5,
            max_lines=10,
            width=400,
        )
        
        def send_support_request(e):
            if not email_field.value:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Пожалуйста, укажите email"),
                    bgcolor="#FF4444",
                )
                page.snack_bar.open = True
                page.update()
                return
            
            request = {
                "email": email_field.value,
                "subject": subject_field.value,
                "message": message_field.value,
                "date": datetime.now().isoformat(),
                "user": current_user["username"] or "Guest",
            }
            
            requests = DataManager.load_json(SUPPORT_FILE, [])
            requests.append(request)
            DataManager.save_json(SUPPORT_FILE, requests)
            
            email_field.value = ""
            subject_field.value = ""
            message_field.value = ""
            
            page.snack_bar = ft.SnackBar(
                content=ft.Text("✅ Запрос отправлен! Мы свяжемся с вами в ближайшее время."),
                bgcolor="#4CAF50",
            )
            page.snack_bar.open = True
            page.update()
        
        send_btn = ft.ElevatedButton(
            "Отправить запрос",
            on_click=send_support_request,
            bgcolor="#2196F3",
            color="white",
        )
        
        form = ft.Column([email_field, subject_field, message_field, send_btn], spacing=20)
        
        content.controls.extend([title, info, form])
        page.update()
    
    # Гаранты
    def show_guarantors():
        content.controls.clear()
        
        title = ft.Text("🛡️ Наши гаранты", size=32, weight=ft.FontWeight.BOLD)
        
        guarantors = [
            ("@guarantor1", "Telegram", "Основной гарант", "https://t.me/guarantor1"),
            ("@guarantor2", "Discord", "Резервный гарант", "https://discord.com/users/guarantor2"),
            ("@guarantor3", "VK", "Гарант по СНГ", "https://vk.com/guarantor3"),
        ]
        
        cards = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.SHIELD, size=40, color="#4CAF50"),
                    ft.Text(name, size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(platform, size=14, color="#888"),
                    ft.Text(desc, size=12, color="#666"),
                    ft.ElevatedButton(
                        "Связаться",
                        on_click=lambda e, url=url: page.launch_url(url),
                        bgcolor="#4CAF50",
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                width=250,
                padding=30,
                bgcolor="#1a1a1a",
                border_radius=15,
                elevation=5,
                margin=10,
                animate_scale=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
                on_hover=animate_hover,
            ) for name, platform, desc, url in guarantors
        ], wrap=True, alignment=ft.MainAxisAlignment.CENTER)
        
        info = ft.Container(
            content=ft.Text(
                "💰 По всем вопросам оплаты обращайтесь только к официальным гарантам!",
                size=16,
                color="#FFD700",
                text_align=ft.TextAlign.CENTER,
            ),
            bgcolor="#1a1a1a",
            padding=20,
            border_radius=10,
            margin=20,
        )
        
        content.controls.extend([title, info, cards])
        page.update()
    
    # Логин
    def show_login():
        content.controls.clear()
        
        username_field = ft.TextField(
            label="Логин",
            hint_text="Введите логин",
            autofocus=True,
            width=300,
        )
        
        password_field = ft.TextField(
            label="Пароль",
            hint_text="Введите пароль",
            password=True,
            can_reveal_password=True,
            width=300,
        )
        
        def handle_login(e):
            nonlocal current_user
            username = username_field.value
            password = password_field.value
            
            if username in users:
                if users[username]["password"] == hashlib.md5(password.encode()).hexdigest():
                    current_user["username"] = username
                    current_user["is_admin"] = users[username].get("is_admin", False)
                    current_user["points"] = users[username].get("points", 0)
                    current_user["status"] = users[username].get("status", "Bronze")
                    
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"✅ Добро пожаловать, {username}!"),
                        bgcolor="#4CAF50",
                    )
                    page.snack_bar.open = True
                    update_nav_bar()
                    show_home()
                else:
                    show_error("Неверный пароль")
            else:
                show_error("Пользователь не найден")
        
        def show_error(message):
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"❌ {message}"),
                bgcolor="#FF4444",
            )
            page.snack_bar.open = True
            page.update()
        
        def handle_register(e):
            username = username_field.value
            password = password_field.value
            
            if not username or not password:
                show_error("Заполните все поля")
                return
            
            if username in users:
                show_error("Пользователь уже существует")
                return
            
            users[username] = {
                "password": hashlib.md5(password.encode()).hexdigest(),
                "is_admin": False,
                "points": 100,
                "status": "Bronze"
            }
            DataManager.save_json(USERS_FILE, users)
            
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✅ Аккаунт {username} создан! Теперь войдите."),
                bgcolor="#4CAF50",
            )
            page.snack_bar.open = True
            page.update()
        
        login_form = ft.Container(
            content=ft.Column([
                ft.Text("🔐 Вход в систему", size=24, weight=ft.FontWeight.BOLD),
                username_field,
                password_field,
                ft.Row([
                    ft.ElevatedButton("Войти", on_click=handle_login, bgcolor="#4CAF50"),
                    ft.OutlinedButton("Регистрация", on_click=handle_register),
                ], spacing=10),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
            padding=40,
            bgcolor="#1a1a1a",
            border_radius=20,
            width=400,
            alignment=ft.alignment.center,
        )
        
        content.controls.append(ft.Container(
            content=login_form,
            alignment=ft.alignment.center,
            expand=True,
        ))
        page.update()
    
    # Личный кабинет
    def show_profile():
        content.controls.clear()
        
        if not current_user["username"]:
            show_login()
            return
        
        status_colors = {
            "Bronze": "#CD7F32",
            "Silver": "#C0C0C0",
            "Gold": "#FFD700",
            "Ultimate": "#B444FF"
        }
        
        profile_card = ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.ACCOUNT_CIRCLE, size=100, color=status_colors.get(current_user["status"], "#888")),
                ft.Text(f"👤 {current_user['username']}", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Text(current_user["status"], color="white"),
                    bgcolor=status_colors.get(current_user["status"], "#888"),
                    padding=10,
                    border_radius=5,
                ),
                ft.Text(f"💎 Баллы: {current_user['points']}", size=18),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
            padding=40,
            bgcolor="#1a1a1a",
            border_radius=20,
            width=400,
        )
        
        content.controls.append(ft.Container(
            content=profile_card,
            alignment=ft.alignment.center,
            expand=True,
        ))
        page.update()
    
    # Админ-панель
    def show_admin_panel():
        content.controls.clear()
        
        if not current_user["is_admin"]:
            show_home()
            return
        
        title = ft.Text("🔧 Панель администратора", size=32, weight=ft.FontWeight.BOLD)
        
        # Управление пользователями
        users_section = ft.Container(
            content=ft.Column([
                ft.Text("👥 Управление пользователями", size=20, weight=ft.FontWeight.BOLD),
                ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Text(f"👤 {username}", expand=True),
                            ft.Text(f"Статус: {data.get('status', 'Bronze')}"),
                            ft.Text(f"Баллы: {data.get('points', 0)}"),
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                on_click=lambda e, u=username: edit_user(u),
                            ),
                        ]),
                        bgcolor="#2a2a2a",
                        padding=10,
                        border_radius=5,
                        margin=ft.margin.only(bottom=5),
                    ) for username, data in users.items()
                ]),
            ]),
            padding=20,
            bgcolor="#1a1a1a",
            border_radius=10,
            margin=10,
        )
        
        def edit_user(username):
            def save_changes(e):
                users[username]["points"] = int(points_field.value)
                users[username]["status"] = status_field.value
                DataManager.save_json(USERS_FILE, users)
                dialog.open = False
                show_admin_panel()
            
            points_field = ft.TextField(
                label="Баллы",
                value=str(users[username].get("points", 0)),
                keyboard_type=ft.KeyboardType.NUMBER,
            )
            
            status_field = ft.Dropdown(
                label="Статус",
                value=users[username].get("status", "Bronze"),
                options=[
                    ft.dropdown.Option("Bronze"),
                    ft.dropdown.Option("Silver"),
                    ft.dropdown.Option("Gold"),
                    ft.dropdown.Option("Ultimate"),
                ],
            )
            
            dialog = ft.AlertDialog(
                title=ft.Text(f"Редактировать {username}"),
                content=ft.Column([points_field, status_field], spacing=10),
                actions=[
                    ft.TextButton("Отмена", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
                    ft.ElevatedButton("Сохранить", on_click=save_changes),
                ],
            )
            
            page.dialog = dialog
            dialog.open = True
            page.update()
        
        # Запросы в поддержку
        support_requests = DataManager.load_json(SUPPORT_FILE, [])
        
        requests_section = ft.Container(
            content=ft.Column([
                ft.Text("📧 Запросы в поддержку", size=20, weight=ft.FontWeight.BOLD),
                ft.Column([
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"От: {req.get('user', 'Guest')}", weight=ft.FontWeight.BOLD),
                                ft.Text(f"Email: {req.get('email', 'N/A')}", color="#888"),
                            ]),
                            ft.Text(f"Тема: {req.get('subject', 'Без темы')}", size=14),
                            ft.Text(f"Сообщение: {req.get('message', '')[:100]}...", size=12, color="#666"),
                            ft.Text(f"Дата: {req.get('date', 'N/A')[:10]}", size=11, color="#555"),
                        ]),
                        bgcolor="#2a2a2a",
                        padding=10,
                        border_radius=5,
                        margin=ft.margin.only(bottom=5),
                    ) for req in support_requests[-5:]  # Показываем последние 5 запросов
                ]) if support_requests else [ft.Text("Нет запросов", color="#888")],
            ]),
            padding=20,
            bgcolor="#1a1a1a",
            border_radius=10,
            margin=10,
        )
        
        # Статистика
        stats_section = ft.Container(
            content=ft.Column([
                ft.Text("📊 Статистика", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("👥", size=30),
                            ft.Text(f"{len(users)}", size=24, weight=ft.FontWeight.BOLD),
                            ft.Text("Пользователей", size=12, color="#888"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=20,
                        bgcolor="#2a2a2a",
                        border_radius=10,
                        width=150,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("🎮", size=30),
                            ft.Text(f"{len(accounts)}", size=24, weight=ft.FontWeight.BOLD),
                            ft.Text("Аккаунтов", size=12, color="#888"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=20,
                        bgcolor="#2a2a2a",
                        border_radius=10,
                        width=150,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📧", size=30),
                            ft.Text(f"{len(support_requests)}", size=24, weight=ft.FontWeight.BOLD),
                            ft.Text("Запросов", size=12, color="#888"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=20,
                        bgcolor="#2a2a2a",
                        border_radius=10,
                        width=150,
                    ),
                ], spacing=20),
            ]),
            padding=20,
            bgcolor="#1a1a1a",
            border_radius=10,
            margin=10,
        )
        
        content.controls.extend([title, stats_section, users_section, requests_section])
        page.update()
    
    # Выход
    def logout():
        nonlocal current_user
        current_user = {"username": None, "is_admin": False, "points": 0, "status": "Bronze"}
        update_nav_bar()
        show_home()
        
        page.snack_bar = ft.SnackBar(
            content=ft.Text("👋 До свидания!"),
            bgcolor="#2196F3",
        )
        page.snack_bar.open = True
        page.update()
    
    def update_nav_bar():
        nav_bar.content = create_nav_bar().content
        page.update()
    
    # Инициализация
    nav_bar = create_nav_bar()
    content = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    
    # Добавляем демо-аккаунты если их нет
    if not accounts:
        demo_accounts = [
            {"name": "GenshinPro", "status": "Gold", "avatar": "⚡", "points": 500},
            {"name": "ValorantMaster", "status": "Ultimate", "avatar": "🎯", "points": 1000},
            {"name": "MinecraftVIP", "status": "Silver", "avatar": "⛏️", "points": 250},
            {"name": "FortniteLegend", "status": "Gold", "avatar": "🏆", "points": 750},
            {"name": "ApexPredator", "status": "Bronze", "avatar": "🦅", "points": 100},
        ]
        DataManager.save_json(ACCOUNTS_FILE, demo_accounts)
        accounts = demo_accounts
    
    # Главный контейнер с анимированным градиентом
    main_container = ft.Container(
        content=ft.Column([
            nav_bar,
            content,
        ], spacing=0),
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=["#0a0a0a", "#1a1a1a", "#0a0a0a"],
            tile_mode=ft.GradientTileMode.MIRROR,
        ),
    )
    
    page.add(main_container)
    show_home()

ft.app(target=main, port=8000, view=ft.AppView.WEB_BROWSER)