from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create initial users (admin, kanishkan, preetha, velmurugan)'

    def handle(self, *args, **kwargs):
        # Create admin
        if not User.objects.filter(username='adminuser').exists():
            User.objects.create_superuser('adminuser', 'admin@example.com', 'KanishPreethaVela@081509')
            self.stdout.write(self.style.SUCCESS('Created admin user (username: adminuser, password: KanishPreethaVela@081509)'))
        
        # Create Kanishakan
        if not User.objects.filter(username='kanishkan').exists():
            User.objects.create_user('kanishkan', 'kanishkan@example.com', 'Kanishkan@2004')
            self.stdout.write(self.style.SUCCESS('Created user_1 (username: kanishkan, password: Kanishkan@2004)'))
        
        # Create Preetha
        if not User.objects.filter(username='preetha').exists():
            User.objects.create_user('preetha', 'preetha@example.com', 'Preetha@2005')
            self.stdout.write(self.style.SUCCESS('Created user_2 (username: preetha, password: Preetha@2005)'))
        
        # Create Velmurugan
        if not User.objects.filter(username='velmurugan').exists():
            User.objects.create_user('velmurugan', 'velmurugan@example.com', 'Velmurugan@2003')
            self.stdout.write(self.style.SUCCESS('Created user_2 (username: velmurugan, password: Velmurugan@2003)'))
        
        self.stdout.write(self.style.SUCCESS('All users created successfully!'))
