from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from lms.models import Course, Lesson


class Command(BaseCommand):
    help = 'Создает группы и назначает права доступа'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🚀 Начинаем создание групп...'))

        # ==================== СОЗДАНИЕ ГРУППЫ МОДЕРАТОРОВ ====================
        moderator_group, created = Group.objects.get_or_create(name='moderators')

        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ Создана группа "moderators"'))
        else:
            self.stdout.write(self.style.SUCCESS('  ⚡ Группа "moderators" уже существует'))

        # Получаем ContentType для моделей Course и Lesson
        course_ct = ContentType.objects.get_for_model(Course)
        lesson_ct = ContentType.objects.get_for_model(Lesson)

        # Права для модераторов:
        # - могут просматривать (view)
        # - могут редактировать (change)
        # - НЕ могут создавать (add)
        # - НЕ могут удалять (delete)

        permissions = [
            Permission.objects.get(codename='view_course', content_type=course_ct),
            Permission.objects.get(codename='change_course', content_type=course_ct),
            Permission.objects.get(codename='view_lesson', content_type=lesson_ct),
            Permission.objects.get(codename='change_lesson', content_type=lesson_ct),
        ]

        # Назначаем права группе
        moderator_group.permissions.set(permissions)

        self.stdout.write(self.style.SUCCESS('  ✅ Права для модераторов настроены:'))
        self.stdout.write('     - Просмотр курсов и уроков')
        self.stdout.write('     - Редактирование курсов и уроков')
        self.stdout.write('     - НЕ могут создавать')
        self.stdout.write('     - НЕ могут удалять')

        # ==================== ИТОГИ ====================
        self.stdout.write(self.style.WARNING('\n' + '=' * 50))
        self.stdout.write(self.style.SUCCESS('🎉 ГРУППЫ УСПЕШНО СОЗДАНЫ!'))
        self.stdout.write(self.style.WARNING('=' * 50))

        self.stdout.write(self.style.WARNING('\n📊 СТАТИСТИКА:'))
        self.stdout.write(f'  👥 Групп в БД: {Group.objects.count()}')
        self.stdout.write(f'  🔐 Назначено прав: {moderator_group.permissions.count()}')

        self.stdout.write(self.style.WARNING('\n🔧 Как добавить пользователя в группу модераторов:'))
        self.stdout.write('  Через админ-панель:')
        self.stdout.write('    1. Зайдите в админку /admin/')
        self.stdout.write('    2. Выберите пользователя')
        self.stdout.write('    3. В разделе "Groups" выберите "moderators"')
        self.stdout.write('    4. Сохраните')
