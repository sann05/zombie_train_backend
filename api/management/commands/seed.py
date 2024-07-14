import os
import random
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from api.models import Region
from api.permissions import PLAYER_GROUP_NAME, ADMIN_GROUP_NAME
from api.utils import get_default_region
from score.models import Score, InfestationLevel
from score.permissions import ScorePermissions
from user.models import GameUser
from django.contrib.auth.models import Group, Permission

from user.permissions import UserPermissions
from zombie_train_backend.utils import get_codename


INFESTATION_LEVELS = [
    {"name": "low", "lower_bound": 0, "upper_bound": 1000},
    {"name": "medium", "lower_bound": 1001, "upper_bound": 1500},
    {"name": "high", "lower_bound": 1501, "upper_bound": 9999999},
]


MOCK_USERS = [
    'glangston0',
    'bturmell1',
    'mcleere2',
    'mbrunelli3',
    'labelwhite4',
    'rfratson5',
    'bhunnybun6',
    'etollit7',
    'ggeck8',
    'amallett9',
    'dandryseka',
    'cwooffb',
    'mgiorgettic',
    'mvigrassd',
    'gbasshame',
    'scabrerf',
    'fdivillg',
    'mchaffinh',
    'dvasei',
    'bdroganj',
    'aveartk',
    'fmcgrielel',
    'aheibelm',
    'eyssonn',
    'phemphillo',
    'lmcinultyp',
    'vsainsberryq',
    'ableezer',
    'jwinskills',
    'kjinkst',
    'twilloughbyu',
    'bsmewingsv',
    'mbroadfieldw',
    'bcrolex',
    'tdavidy',
    'rnewsteadz',
    'alisamore10',
    'ahaysman11',
    'eflack12',
    'tcrewe13',
    'nspurrier14',
    'cgeaney15',
    'thinchcliffe16',
    'jutting17',
    'dpetrollo18',
    'lhinkins19',
    'fcominello1a',
    'bwellsman1b',
    'tstranaghan1c',
    'morable1d',
    'gharniman1e',
    'kogus1f',
    'hfretwell1g',
    'ctindley1h',
    'cgreenhill1i',
    'ewymer1j',
    'seddington1k',
    'jhedau1l',
    'uhelstrom1m',
    'dduetsche1n',
    'kdhillon1o',
]

REGIONS = [
    "Africa",
    "Asia",
    "Europe",
    "North America",
    "South America",
    "Australia"
]


class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def add_arguments(self, parser):
        # Define command-line flags for each seeding operation
        parser.add_argument('--regions', action='store_true', help='Seed regions')
        parser.add_argument('--groups', action='store_true', help='Seed groups')
        parser.add_argument('--users', action='store_true', help='Seed users')
        parser.add_argument('--superuser', action='store_true', help='Create a superuser')
        parser.add_argument('--scores', action='store_true', help='Seed scores')
        parser.add_argument('--infestation_levels', action='store_true', help='Seed infestation levels')
        parser.add_argument('--all', action='store_true', help='Seed all data')

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        if options['all']:
            self.create_all()
        else:
            if options['regions']:
                self.create_regions()
            if options['groups']:
                self.create_groups()
            if options['users']:
                self.create_users()
            if options['superuser']:
                self.create_superuser()
            if options['scores']:
                self.create_scores()
            if options['infestation_levels']:
                self.create_infestation_levels()

        self.stdout.write('Data seeded successfully.')

    def create_all(self):
        self.create_regions()
        self.create_groups()
        self.create_users()
        self.create_superuser()
        self.create_scores()
        self.create_infestation_levels()

    def create_infestation_levels(self):
        objects = InfestationLevel.objects.all().count()
        if objects == 0:
            for level in INFESTATION_LEVELS:
                InfestationLevel.objects.create(
                    name=level['name'],
                    lower_bound=level['lower_bound'],
                    upper_bound=level['upper_bound']
                )
            self.stdout.write(
                self.style.SUCCESS('Successfully created Infestation Levels'))
        else:
            self.stdout.write(
                self.style.WARNING('Infestation Levels already exist'))


    def create_groups(self):
        player_group, created = Group.objects.get_or_create(
            name=PLAYER_GROUP_NAME)
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created Player group'))
            player_permissions = Permission.objects.filter(codename__in=[
                get_codename(ScorePermissions.ADD_SCORE),
            ])
            for player_permission in player_permissions:
                player_group.permissions.add(player_permission)
        else:
            self.stdout.write(self.style.WARNING('Player group already exists'))
        self.groups[PLAYER_GROUP_NAME] = player_group

        admin_group, created = Group.objects.get_or_create(
            name=ADMIN_GROUP_NAME)

        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created Admin group'))
            self.groups[ADMIN_GROUP_NAME] = admin_group
            admin_permissions = Permission.objects.filter(codename__in=list(
                get_codename(perm) for perm in [
                    ScorePermissions.VIEW_SCORE,
                    UserPermissions.VIEW_USER,
                    UserPermissions.DELETE_USER,
                    UserPermissions.CHANGE_USER
                ]))
            for admin_permission in admin_permissions:
                player_group.permissions.add(admin_permission)
        else:
            self.stdout.write(self.style.WARNING('Admin group already exists'))

    def create_superuser(self):
        admin_username = os.getenv("ADMIN_USERNAME")
        admin_password = os.getenv("ADMIN_PASSWORD")
        admin_user = GameUser.objects.filter(username=admin_username).first()
        if not GameUser.objects.filter(username=admin_username).exists():
            admin_user = GameUser.objects.create_superuser(
                username=admin_username,
                email='admin@example.com',
                password=admin_password,
                first_name='Admin',
                last_name='User',
            )
            self.stdout.write(
                self.style.SUCCESS('Successfully created super admin user'))
        else:
            self.stdout.write(
                self.style.WARNING('Super admin user already exists'))
        admin_user.current_region = get_default_region()
        admin_user.save()

    def create_users(self):
        usernames = MOCK_USERS
        for username in usernames:
            if not GameUser.objects.filter(username=username).exists():
                GameUser.objects.create_user(username=username,
                                             current_region=get_default_region(),
                                             password='password')

    def create_scores(self):
        users = GameUser.objects.all()
        regions = Region.objects.all()
        for user in users:
            for i in range(3):
                for j in range(3):  # Create 3 x 3 scores for each user
                    points = random.randint(1, 100)
                    region_id = random.randint(1, len(REGIONS))
                    score_ts = timezone.now() - timedelta(
                        days=j)
                    Score.objects.create(user=user,
                                         value=points,
                                         region=regions[region_id - 1],
                                         score_ts=score_ts)

    def create_regions(self):
        for region in REGIONS:
            Region.objects.create(name=region)
