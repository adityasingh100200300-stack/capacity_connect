from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from profiles.models import Profile
from courses.models import Course, Enrollment
from announcements.models import Announcement

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds initial demo accounts, courses, and announcements for development and testing."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=========================================="))
        self.stdout.write(self.style.MIGRATE_HEADING("  Capacity Connect - Seeding Demo Data    "))
        self.stdout.write(self.style.MIGRATE_HEADING("=========================================="))

        # 1. Seed Users
        users_data = [
            {
                "username": "admin",
                "email": "admin@capacityconnect.com",
                "password": "admin123",
                "role": "ADMIN",
                "status": "ACTIVE",
                "is_staff": True,
                "is_superuser": True,
                "first_name": "System",
                "last_name": "Admin",
                "department": "Administration",
                "bio": "Platform Super Administrator",
            },
            {
                "username": "trainer",
                "email": "trainer@capacityconnect.com",
                "password": "trainer123",
                "role": "TRAINER",
                "status": "ACTIVE",
                "is_staff": False,
                "is_superuser": False,
                "first_name": "Demo",
                "last_name": "Trainer",
                "department": "Engineering Training",
                "bio": "Senior Technical Instructor specializing in Full-Stack Python and Django.",
            },
            {
                "username": "tr_tr",
                "email": "tr_tr@capacityconnect.com",
                "password": "trainer123",
                "role": "TRAINER",
                "status": "ACTIVE",
                "is_staff": False,
                "is_superuser": False,
                "first_name": "Alex",
                "last_name": "Rivera",
                "department": "Data Science",
                "bio": "Lead Data Science & ML Coach.",
            },
            {
                "username": "trainee",
                "email": "trainee@capacityconnect.com",
                "password": "trainee123",
                "role": "TRAINEE",
                "status": "ACTIVE",
                "is_staff": False,
                "is_superuser": False,
                "first_name": "Demo",
                "last_name": "Trainee",
                "department": "Junior Engineering",
                "bio": "Full-stack software developer trainee.",
            },
            {
                "username": "tr_2",
                "email": "tr2@capacityconnect.com",
                "password": "trainee123",
                "role": "TRAINEE",
                "status": "ACTIVE",
                "is_staff": False,
                "is_superuser": False,
                "first_name": "Jordan",
                "last_name": "Lee",
                "department": "Quality Assurance",
                "bio": "QA engineer trainee.",
            },
            {
                "username": "tr_le",
                "email": "tr_le@capacityconnect.com",
                "password": "trainee123",
                "role": "TRAINEE",
                "status": "ACTIVE",
                "is_staff": False,
                "is_superuser": False,
                "first_name": "Sam",
                "last_name": "Taylor",
                "department": "Product Operations",
                "bio": "Product and Operations trainee.",
            },
            {
                "username": "101akash",
                "email": "101akash@cap.com",
                "password": "trainee123",
                "role": "TRAINEE",
                "status": "ACTIVE",
                "is_staff": False,
                "is_superuser": False,
                "first_name": "Akash",
                "last_name": "Kumar",
                "department": "Engineering Trainee",
                "bio": "Software Engineering Trainee.",
            },
        ]

        seeded_users = {}
        for udata in users_data:
            username = udata["username"]
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": udata["email"],
                    "role": udata["role"],
                    "status": udata["status"],
                    "is_staff": udata["is_staff"],
                    "is_superuser": udata["is_superuser"],
                    "first_name": udata["first_name"],
                    "last_name": udata["last_name"],
                },
            )
            # Ensure password and status are always set properly
            user.set_password(udata["password"])
            user.role = udata["role"]
            user.status = udata["status"]
            user.is_staff = udata["is_staff"]
            user.is_superuser = udata["is_superuser"]
            user.save()

            # Profile
            profile, _ = Profile.objects.get_or_create(user=user)
            if not profile.department:
                profile.department = udata.get("department", "")
            if not profile.bio:
                profile.bio = udata.get("bio", "")
            profile.save()

            seeded_users[username] = user
            status_text = "Created" if created else "Updated password/role for"
            self.stdout.write(
                self.style.SUCCESS(f"  [OK] {status_text} user: {username} ({udata['role']})")
            )

        # 2. Seed Sample Courses
        primary_trainer = seeded_users.get("trainer")
        if primary_trainer:
            c1, c1_created = Course.objects.get_or_create(
                title="Full-Stack Web Development with Django & Python",
                defaults={
                    "description": "Learn modern web architecture, Django ORM, REST APIs, responsive templates, and enterprise patterns.",
                    "trainer": primary_trainer,
                    "is_active": True,
                },
            )
            if c1_created:
                self.stdout.write(self.style.SUCCESS(f"  [OK] Created course: {c1.title}"))

            c2, c2_created = Course.objects.get_or_create(
                title="Database Systems & SQL Optimization",
                defaults={
                    "description": "Master relational database design, indexing strategies, migrations, and high-performance querying.",
                    "trainer": primary_trainer,
                    "is_active": True,
                },
            )
            if c2_created:
                self.stdout.write(self.style.SUCCESS(f"  [OK] Created course: {c2.title}"))

            # Enroll trainees
            for trainee_uname in ["trainee", "tr_2", "101akash"]:
                trainee_user = seeded_users.get(trainee_uname)
                if trainee_user:
                    e1, _ = Enrollment.objects.get_or_create(trainee=trainee_user, course=c1)
                    e2, _ = Enrollment.objects.get_or_create(trainee=trainee_user, course=c2)

        # 3. Seed Announcements
        admin_user = seeded_users.get("admin")
        if admin_user and not Announcement.objects.filter(is_pinned=True).exists():
            ann = Announcement.objects.create(
                title="Welcome to Capacity Connect!",
                body="Welcome to the platform! Use your assigned portal to track your learning journey, submit doubts, and view competency metrics.",
                announcement_type="GENERAL",
                created_by=admin_user,
                is_pinned=True,
            )
            self.stdout.write(self.style.SUCCESS(f"  [OK] Created announcement: {ann.title}"))

        self.stdout.write(self.style.MIGRATE_HEADING("\n=========================================="))
        self.stdout.write(self.style.SUCCESS("[OK] Demo data successfully seeded!"))
        self.stdout.write(self.style.MIGRATE_HEADING("=========================================="))
        self.stdout.write("\nDefault Credentials:")
        self.stdout.write("  * Admin:   Username: admin    | Password: admin123")
        self.stdout.write("  * Trainer: Username: trainer  | Password: trainer123")
        self.stdout.write("  * Trainee: Username: trainee  | Password: trainee123")
        self.stdout.write("  * Trainee: Username: tr_2     | Password: trainee123")
        self.stdout.write("  * Trainee: Username: 101akash | Password: trainee123\n")
