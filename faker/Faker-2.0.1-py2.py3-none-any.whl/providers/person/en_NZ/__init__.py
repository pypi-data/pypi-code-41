# coding=utf-8
from __future__ import unicode_literals
from collections import OrderedDict

from .. import Provider as PersonProvider


class Provider(PersonProvider):
    formats = (
        '{{first_name_male}} {{last_name}}',
        '{{first_name_male}} {{last_name}}',
        '{{first_name_male}} {{last_name}}',
        '{{first_name_male}} {{last_name}}',
        '{{first_name_male}} {{last_name}}-{{last_name}}',
        '{{first_name_female}} {{last_name}}',
        '{{first_name_female}} {{last_name}}',
        '{{first_name_female}} {{last_name}}',
        '{{first_name_female}} {{last_name}}',
        '{{first_name_female}} {{last_name}}-{{last_name}}',
    )

    # Names compiled from the following sources:
    #
    # https://www.dia.govt.nz/diawebsite.nsf/wpg_URL/Services-Births-Deaths-and-Marriages-Most-Popular-Male-and-Female-First-Names

    first_names_male = OrderedDict((
        ("Aaron", 9912),
        ("Adam", 7639),
        ("Adrian", 2420),
        ("Aidan", 1521),
        ("Aiden", 782),
        ("Alan", 5689),
        ("Alex", 2819),
        ("Alexander", 7783),
        ("Alistair", 429),
        ("Allan", 3148),
        ("Allen", 51),
        ("Andre", 127),
        ("Andrew", 25593),
        ("Angus", 1680),
        ("Anthony", 12549),
        ("Antony", 1594),
        ("Archer", 381),
        ("Archie", 774),
        ("Arlo", 584),
        ("Arthur", 630),
        ("Asher", 319),
        ("Ashley", 861),
        ("Ashton", 1236),
        ("Austin", 688),
        ("Bailey", 1304),
        ("Barry", 3624),
        ("Beau", 491),
        ("Beauden", 125),
        ("Ben", 2427),
        ("Benjamin", 15497),
        ("Bernard", 657),
        ("Bevan", 634),
        ("Blair", 2863),
        ("Blake", 3500),
        ("Bodhi", 70),
        ("Brad", 450),
        ("Bradley", 3910),
        ("Brandon", 1000),
        ("Braxton", 741),
        ("Brayden", 317),
        ("Brendan", 2010),
        ("Brendon", 3163),
        ("Brent", 5564),
        ("Brett", 4598),
        ("Brian", 6247),
        ("Brodie", 216),
        ("Brooklyn", 406),
        ("Bruce", 6079),
        ("Bryan", 1435),
        ("Caleb", 5374),
        ("Callum", 2364),
        ("Cameron", 7756),
        ("Campbell", 422),
        ("Carl", 3304),
        ("Carlos", 122),
        ("Carter", 1308),
        ("Charles", 3933),
        ("Charlie", 2367),
        ("Chase", 174),
        ("Christian", 1138),
        ("Christopher", 23459),
        ("Clayton", 59),
        ("Clinton", 1004),
        ("Cody", 2482),
        ("Cohen", 99),
        ("Cole", 648),
        ("Colin", 3980),
        ("Connor", 4632),
        ("Conor", 54),
        ("Cooper", 2113),
        ("Corey", 1656),
        ("Cory", 129),
        ("Craig", 12702),
        ("Cruz", 52),
        ("Damian", 1084),
        ("Damon", 211),
        ("Daniel", 23515),
        ("Darren", 3143),
        ("Darrin", 217),
        ("Darryl", 1517),
        ("Darryn", 260),
        ("Daryl", 421),
        ("David", 36792),
        ("Dean", 6096),
        ("Declan", 108),
        ("Denis", 66),
        ("Dennis", 1129),
        ("Derek", 1307),
        ("Desmond", 224),
        ("Dillon", 63),
        ("Dion", 1283),
        ("Dominic", 801),
        ("Donald", 2405),
        ("Douglas", 2587),
        ("Duncan", 471),
        ("Dwayne", 57),
        ("Dylan", 6564),
        ("Edward", 4864),
        ("Eli", 961),
        ("Elijah", 2137),
        ("Elliot", 54),
        ("Eric", 808),
        ("Ethan", 6578),
        ("Ezra", 309),
        ("Felix", 769),
        ("Finn", 2084),
        ("Fletcher", 447),
        ("Flynn", 1577),
        ("Francis", 420),
        ("Frank", 46),
        ("Fraser", 51),
        ("Frederick", 49),
        ("Gabriel", 739),
        ("Gareth", 2087),
        ("Garry", 1840),
        ("Gary", 5520),
        ("Gavin", 3197),
        ("Geoffrey", 4439),
        ("George", 7320),
        ("Gerald", 104),
        ("Gerard", 614),
        ("Glen", 2709),
        ("Glenn", 3983),
        ("Gordon", 1444),
        ("Graeme", 4705),
        ("Graham", 3746),
        ("Grant", 8355),
        ("Grayson", 259),
        ("Gregory", 7916),
        ("Hamish", 5758),
        ("Harley", 403),
        ("Harrison", 2800),
        ("Harry", 2454),
        ("Harvey", 192),
        ("Hayden", 5209),
        ("Henry", 3111),
        ("Hudson", 281),
        ("Hugh", 101),
        ("Hugo", 543),
        ("Hunter", 3044),
        ("Ian", 7592),
        ("Isaac", 4208),
        ("Isaiah", 349),
        ("Israel", 52),
        ("Ivan", 236),
        ("Jack", 9468),
        ("Jackson", 3088),
        ("Jacob", 8612),
        ("Jake", 2421),
        ("Jakob", 46),
        ("James", 27224),
        ("Jamie", 5064),
        ("Jared", 2840),
        ("Jarrod", 773),
        ("Jason", 14737),
        ("Jasper", 246),
        ("Jaxon", 623),
        ("Jayden", 4541),
        ("Jeffrey", 2826),
        ("Jeremy", 4775),
        ("Jesse", 3965),
        ("Joel", 2932),
        ("John", 26867),
        ("Jonathan", 7957),
        ("Jonathon", 349),
        ("Jordan", 6499),
        ("Joseph", 10061),
        ("Josh", 56),
        ("Joshua", 17109),
        ("Josiah", 52),
        ("Julian", 232),
        ("Justin", 3882),
        ("Kaleb", 492),
        ("Kane", 1236),
        ("Karl", 3822),
        ("Kayden", 123),
        ("Keanu", 54),
        ("Keegan", 351),
        ("Keith", 2175),
        ("Kelly", 58),
        ("Kelvin", 1262),
        ("Kenneth", 3240),
        ("Kerry", 2404),
        ("Kevin", 9358),
        ("Kieran", 1525),
        ("Kim", 125),
        ("Kingston", 692),
        ("Kurt", 515),
        ("Kyle", 2568),
        ("Lachlan", 2965),
        ("Lance", 2958),
        ("Lawrence", 226),
        ("Lee", 872),
        ("Leo", 1872),
        ("Leon", 967),
        ("Leonard", 102),
        ("Leslie", 1126),
        ("Levi", 2986),
        ("Lewis", 324),
        ("Liam", 8629),
        ("Lincoln", 857),
        ("Lindsay", 883),
        ("Lloyd", 46),
        ("Logan", 5063),
        ("Louis", 863),
        ("Luca", 1318),
        ("Lucas", 3329),
        ("Luka", 119),
        ("Lukas", 70),
        ("Luke", 8296),
        ("Malcolm", 2398),
        ("Marcus", 1129),
        ("Mark", 23154),
        ("Martin", 4260),
        ("Mason", 2613),
        ("Mathew", 3107),
        ("Matthew", 23181),
        ("Maurice", 385),
        ("Max", 3988),
        ("Maxwell", 172),
        ("Mervyn", 162),
        ("Micah", 52),
        ("Michael", 40099),
        ("Micheal", 49),
        ("Mitchell", 2730),
        ("Morgan", 58),
        ("Murray", 4843),
        ("Nate", 48),
        ("Nathan", 8920),
        ("Nathaniel", 329),
        ("Neil", 3392),
        ("Neville", 1268),
        ("Nicholas", 13132),
        ("Nigel", 4435),
        ("Nikau", 53),
        ("Nixon", 219),
        ("Noah", 3511),
        ("Noel", 778),
        ("Norman", 221),
        ("Oliver", 6515),
        ("Oscar", 1987),
        ("Owen", 484),
        ("Patrick", 6219),
        ("Paul", 22959),
        ("Peter", 23996),
        ("Philip", 7036),
        ("Phillip", 5977),
        ("Phoenix", 882),
        ("Quentin", 67),
        ("Quinn", 742),
        ("Raymond", 4404),
        ("Regan", 1182),
        ("Reuben", 1678),
        ("Rex", 561),
        ("Rhys", 967),
        ("Richard", 17664),
        ("Ricky", 806),
        ("Riley", 2771),
        ("Robert", 19791),
        ("Robin", 1431),
        ("Rodney", 1936),
        ("Roger", 2612),
        ("Roman", 429),
        ("Ronald", 1769),
        ("Rory", 220),
        ("Ross", 4823),
        ("Roy", 101),
        ("Russell", 2863),
        ("Ryan", 9965),
        ("Ryder", 727),
        ("Sam", 2347),
        ("Samuel", 15565),
        ("Scott", 9481),
        ("Sean", 5201),
        ("Sebastian", 1031),
        ("Seth", 780),
        ("Shane", 10213),
        ("Shannon", 1082),
        ("Shaun", 4397),
        ("Shayne", 296),
        ("Simon", 9846),
        ("Sione", 165),
        ("Spencer", 52),
        ("Stefan", 52),
        ("Stephen", 18603),
        ("Steven", 11007),
        ("Stewart", 499),
        ("Stuart", 4662),
        ("Taine", 204),
        ("Taylor", 1356),
        ("Terence", 1154),
        ("Terry", 860),
        ("Theo", 311),
        ("Theodore", 429),
        ("Thomas", 15382),
        ("Timothy", 10924),
        ("Toby", 1490),
        ("Todd", 1264),
        ("Tom", 47),
        ("Tony", 5670),
        ("Travis", 65),
        ("Trent", 524),
        ("Trevor", 3194),
        ("Tristan", 111),
        ("Troy", 2423),
        ("Tyler", 3765),
        ("Tyrone", 231),
        ("Tyson", 531),
        ("Vaughan", 322),
        ("Vincent", 907),
        ("Walter", 57),
        ("Warren", 3223),
        ("Warwick", 295),
        ("Wayne", 8542),
        ("William", 18322),
        ("Wyatt", 58),
        ("Xavier", 1879),
        ("Zac", 111),
        ("Zachary", 2569),
        ("Zane", 761),
        ("Zion", 217),

        ("Anaru", 735),
        ("Ari", 984),
        ("Ariki", 1178),
        ("Hemi", 1360),
        ("Hoani", 574),
        ("Ihaia", 476),
        ("Kahu", 700),
        ("Kahurangi", 939),
        ("Kauri", 1613),
        ("Manaaki", 574),
        ("Manaia", 1434),
        ("Manawa", 536),
        ("Matiu", 455),
        ("Mikaere", 1413),
        ("Nikau", 1942),
        ("Niko", 972),
        ("Nikora", 1766),
        ("Rawiri", 1553),
        ("Tai", 793),
        ("Tama", 1257),
        ("Tamati", 1766),
        ("Tane", 1698),
        ("Tangaroa", 605),
        ("Te Ariki", 1423),
        ("Te Koha", 537),
        ("Tiare", 476),
        ("Wiremu", 1923),
    ))

    first_names_female = OrderedDict((
        ("Aaliyah", 1042),
        ("Abbey", 40),
        ("Abby", 503),
        ("Abigail", 2017),
        ("Addison", 538),
        ("Adrienne", 625),
        ("Aimee", 2315),
        ("Alana", 1194),
        ("Aleisha", 102),
        ("Alexandra", 2689),
        ("Alexis", 789),
        ("Alice", 3252),
        ("Alicia", 683),
        ("Alison", 3444),
        ("Alyssa", 1032),
        ("Amaia", 45),
        ("Amanda", 7667),
        ("Amber", 3661),
        ("Amelia", 4060),
        ("Amy", 7061),
        ("Anahera", 140),
        ("Andrea", 5003),
        ("Angel", 695),
        ("Angela", 9634),
        ("Angelina", 43),
        ("Anika", 46),
        ("Anita", 1526),
        ("Ann", 1834),
        ("Anna", 9371),
        ("Annabelle", 457),
        ("Anne", 3879),
        ("Annette", 2348),
        ("April", 49),
        ("Arabella", 42),
        ("Aria", 1025),
        ("Ariana", 473),
        ("Aroha", 50),
        ("Ashlee", 464),
        ("Ashleigh", 3158),
        ("Ashley", 2477),
        ("Aurora", 251),
        ("Ava", 2487),
        ("Ayla", 612),
        ("Bailey", 150),
        ("Barbara", 3531),
        ("Belinda", 1254),
        ("Bella", 1238),
        ("Beverley", 996),
        ("Billie", 45),
        ("Brenda", 2451),
        ("Briana", 49),
        ("Brianna", 740),
        ("Bridget", 1611),
        ("Britney", 64),
        ("Brittany", 1239),
        ("Bronwyn", 2406),
        ("Brooke", 3634),
        ("Brooklyn", 782),
        ("Caitlin", 3370),
        ("Caitlyn", 454),
        ("Carla", 323),
        ("Carmen", 233),
        ("Carol", 3626),
        ("Caroline", 2530),
        ("Carolyn", 3212),
        ("Casey", 1097),
        ("Cassandra", 489),
        ("Catherine", 7765),
        ("Chantelle", 55),
        ("Charlie", 215),
        ("Charlotte", 7759),
        ("Chelsea", 1943),
        ("Cherie", 1064),
        ("Cheryl", 1781),
        ("Cheyenne", 345),
        ("Chloe", 4582),
        ("Christina", 2675),
        ("Christine", 10604),
        ("Cindy", 65),
        ("Claire", 3174),
        ("Clara", 41),
        ("Clare", 55),
        ("Claudia", 804),
        ("Colleen", 1367),
        ("Courtney", 2941),
        ("Crystal", 828),
        ("Daisy", 197),
        ("Danielle", 4151),
        ("Dawn", 62),
        ("Debbie", 1389),
        ("Deborah", 8819),
        ("Debra", 3094),
        ("Denise", 3577),
        ("Destiny", 190),
        ("Diana", 977),
        ("Diane", 3952),
        ("Dianne", 2314),
        ("Donna", 7054),
        ("Dorothy", 303),
        ("Eden", 1578),
        ("Eilish", 52),
        ("Elaine", 381),
        ("Eleanor", 155),
        ("Elise", 48),
        ("Elizabeth", 11869),
        ("Ella", 5301),
        ("Ellen", 124),
        ("Ellie", 443),
        ("Elsie", 97),
        ("Emilia", 145),
        ("Emily", 7766),
        ("Emma", 13245),
        ("Erin", 1624),
        ("Esther", 88),
        ("Eva", 1637),
        ("Evelyn", 634),
        ("Evie", 419),
        ("Faith", 735),
        ("Fiona", 6039),
        ("Florence", 291),
        ("Frances", 1212),
        ("Frankie", 195),
        ("Freya", 218),
        ("Gabriella", 94),
        ("Gabrielle", 808),
        ("Gail", 1253),
        ("Gaylene", 82),
        ("Gemma", 2120),
        ("Georgia", 5613),
        ("Georgina", 786),
        ("Gillian", 1388),
        ("Gina", 301),
        ("Glenda", 859),
        ("Glenys", 410),
        ("Gloria", 127),
        ("Grace", 6036),
        ("Haley", 173),
        ("Hannah", 9082),
        ("Harmony", 300),
        ("Harper", 1186),
        ("Harriet", 210),
        ("Hayley", 4951),
        ("Hazel", 814),
        ("Heather", 4351),
        ("Heidi", 353),
        ("Helen", 7775),
        ("Holly", 4402),
        ("Hope", 142),
        ("Imogen", 293),
        ("Indi", 42),
        ("Indie", 494),
        ("Irene", 166),
        ("Isabel", 499),
        ("Isabella", 4257),
        ("Isabelle", 1182),
        ("Isla", 2246),
        ("Isobel", 85),
        ("Ivy", 577),
        ("Jacqueline", 5559),
        ("Jade", 3234),
        ("Jaime", 61),
        ("Jamie", 1066),
        ("Jan", 1587),
        ("Jane", 4932),
        ("Janet", 2253),
        ("Janette", 69),
        ("Janice", 1881),
        ("Janine", 2641),
        ("Jasmine", 3786),
        ("Jean", 64),
        ("Jeanette", 900),
        ("Jemma", 200),
        ("Jenna", 1162),
        ("Jennifer", 9991),
        ("Jessica", 12989),
        ("Jessie", 1123),
        ("Jill", 455),
        ("Jillian", 1571),
        ("Joan", 199),
        ("Joanna", 2716),
        ("Joanne", 9329),
        ("Jocelyn", 557),
        ("Jodi", 56),
        ("Jodie", 359),
        ("Jolene", 313),
        ("Jordan", 797),
        ("Jorja", 456),
        ("Josephine", 570),
        ("Joy", 487),
        ("Judith", 4677),
        ("Julia", 2092),
        ("Julie", 8289),
        ("Justine", 1127),
        ("Kaitlin", 45),
        ("Kaitlyn", 358),
        ("Karen", 13524),
        ("Karla", 62),
        ("Karyn", 429),
        ("Kate", 5782),
        ("Katelyn", 294),
        ("Katherine", 3912),
        ("Kathleen", 2503),
        ("Kathryn", 5104),
        ("Katie", 3455),
        ("Katrina", 3184),
        ("Kay", 1205),
        ("Kaye", 227),
        ("Kayla", 2806),
        ("Keira", 759),
        ("Kellie", 66),
        ("Kelly", 6137),
        ("Kelsey", 718),
        ("Kerry", 1917),
        ("Khloe", 98),
        ("Kim", 5667),
        ("Kimberley", 1578),
        ("Kiri", 130),
        ("Kirsten", 1183),
        ("Kirsty", 2083),
        ("Kristy", 172),
        ("Krystal", 650),
        ("Kyla", 41),
        ("Kylie", 3692),
        ("Laura", 4669),
        ("Lauren", 3275),
        ("Layla", 536),
        ("Leah", 1894),
        ("Leanne", 3478),
        ("Leonie", 52),
        ("Lesley", 1453),
        ("Libby", 48),
        ("Lilly", 813),
        ("Lily", 3546),
        ("Linda", 6288),
        ("Lisa", 11891),
        ("Lois", 278),
        ("Lola", 343),
        ("Lorraine", 1675),
        ("Louise", 4580),
        ("Lucia", 235),
        ("Lucy", 4938),
        ("Luna", 53),
        ("Lydia", 335),
        ("Lynda", 1972),
        ("Lynette", 3666),
        ("Lynley", 228),
        ("Lynn", 53),
        ("Lynne", 1025),
        ("Lynnette", 120),
        ("MacKenzie", 67),
        ("Mackenzie", 1039),
        ("Maddison", 1846),
        ("Madeleine", 780),
        ("Madeline", 184),
        ("Madison", 3128),
        ("Maia", 1937),
        ("Manaia", 204),
        ("Maree", 2270),
        ("Margaret", 5517),
        ("Maria", 5541),
        ("Marian", 60),
        ("Marie", 2582),
        ("Marilyn", 546),
        ("Marion", 370),
        ("Mary", 5891),
        ("Matilda", 570),
        ("Maureen", 1099),
        ("Maya", 432),
        ("Megan", 5869),
        ("Melanie", 4476),
        ("Melissa", 6898),
        ("Mia", 2627),
        ("Michaela", 687),
        ("Michele", 1082),
        ("Michelle", 12961),
        ("Mikaela", 48),
        ("Mikayla", 1492),
        ("Mila", 1139),
        ("Millie", 711),
        ("Molly", 1590),
        ("Monica", 56),
        ("Monique", 1859),
        ("Morgan", 646),
        ("Mya", 352),
        ("Nadine", 126),
        ("Naomi", 421),
        ("Natalie", 4112),
        ("Natasha", 5533),
        ("Nevaeh", 673),
        ("Ngaire", 116),
        ("Niamh", 49),
        ("Nicola", 10395),
        ("Nicole", 6011),
        ("Nikita", 1263),
        ("Nikki", 57),
        ("Nina", 379),
        ("Olive", 525),
        ("Olivia", 8816),
        ("Paige", 3719),
        ("Pamela", 2677),
        ("Paris", 551),
        ("Patricia", 5007),
        ("Paula", 3667),
        ("Pauline", 2404),
        ("Payton", 44),
        ("Penelope", 1213),
        ("Peyton", 621),
        ("Philippa", 1359),
        ("Phoebe", 1380),
        ("Piper", 580),
        ("Pippa", 416),
        ("Poppy", 842),
        ("Quinn", 213),
        ("Rachael", 3210),
        ("Rachel", 9769),
        ("Rachelle", 64),
        ("Raewyn", 3039),
        ("Rebecca", 11608),
        ("Rebekah", 1255),
        ("Renee", 3387),
        ("Rhonda", 131),
        ("Riley", 676),
        ("Robyn", 5598),
        ("Rochelle", 2086),
        ("Rose", 1384),
        ("Rosemary", 1918),
        ("Ruby", 4332),
        ("Ruth", 1616),
        ("Sadie", 151),
        ("Sally", 2445),
        ("Samantha", 7549),
        ("Sandra", 7429),
        ("Sara", 1121),
        ("Sarah", 19901),
        ("Sasha", 44),
        ("Savannah", 443),
        ("Scarlett", 1045),
        ("Shakira", 52),
        ("Shania", 338),
        ("Shannon", 2446),
        ("Sharlene", 220),
        ("Sharon", 7243),
        ("Shelley", 2569),
        ("Sheree", 169),
        ("Sheryl", 1688),
        ("Shirley", 1673),
        ("Shona", 1210),
        ("Sienna", 1358),
        ("Sinead", 53),
        ("Skye", 97),
        ("Skyla", 105),
        ("Skylar", 41),
        ("Sofia", 630),
        ("Sonia", 246),
        ("Sonya", 632),
        ("Sophia", 2595),
        ("Sophie", 7868),
        ("Stacey", 3037),
        ("Stella", 1323),
        ("Stephanie", 5794),
        ("Summer", 1477),
        ("Susan", 12686),
        ("Suzanne", 4705),
        ("Tamara", 312),
        ("Tania", 6879),
        ("Tanya", 1595),
        ("Tara", 503),
        ("Tayla", 1823),
        ("Taylor", 1499),
        ("Tegan", 318),
        ("Teresa", 2294),
        ("Tessa", 1439),
        ("Thea", 279),
        ("Tiana", 388),
        ("Tina", 2124),
        ("Toni", 2572),
        ("Tori", 50),
        ("Tracey", 6914),
        ("Tracy", 3999),
        ("Trinity", 401),
        ("Tyla", 98),
        ("Valerie", 394),
        ("Vanessa", 3941),
        ("Vicki", 3171),
        ("Vicky", 198),
        ("Victoria", 4823),
        ("Violet", 506),
        ("Virginia", 54),
        ("Vivienne", 802),
        ("Wendy", 6832),
        ("Whitney", 50),
        ("Willow", 743),
        ("Yvonne", 1822),
        ("Zara", 1292),
        ("Zoe", 3973),
        ("Zoey", 165),

        ("Amaia", 667),
        ("Ana", 730),
        ("Anahera", 1760),
        ("Anika", 1432),
        ("Aria", 1960),
        ("Ariana", 1729),
        ("Aroha", 1796),
        ("Ataahua", 876),
        ("Awhina", 583),
        ("Hana", 536),
        ("Hinewai", 536),
        ("Huia", 528),
        ("Kahurangi", 730),
        ("Kaia", 1576),
        ("Kora", 878),
        ("Mahi", 556),
        ("Maia", 1960),
        ("Manaia", 912),
        ("Maraea", 703),
        ("Mareikura", 948),
        ("Mereana", 637),
        ("Miriama", 614),
        ("Nia", 667),
        ("Ria", 703),
        ("Terina", 528),
        ("Tia", 1695),
        ("Tiare", 671),
        ("Tui", 1251),
        ("Waimarie", 671),
        ("Wikitoria", 583),
    ))

    first_names = first_names_male.copy()
    first_names.update(first_names_female)

    # New Zealand surnames compiled (and cleaned up) from the following sources:
    #
    # NZ Cemetery plot data:
    #    https://catalogue.data.govt.nz/dataset?q=cemetery+plots

    last_names = OrderedDict((
        ("Smith", 948),
        ("Anderson", 394),
        ("Jones", 386),
        ("Taylor", 364),
        ("Brown", 350),
        ("Williams", 337),
        ("Thompson", 295),
        ("Scott", 266),
        ("Harris", 253),
        ("Mitchell", 217),
        ("Thomas", 214),
        ("Campbell", 193),
        ("Jackson", 191),
        ("Stewart", 188),
        ("Martin", 186),
        ("Turner", 174),
        ("Moore", 173),
        ("Simpson", 171),
        ("Hart", 166),
        ("Bell", 163),
        ("Evans", 161),
        ("Hansen", 160),
        ("Gray", 156),
        ("Henderson", 155),
        ("Edwards", 153),
        ("McDonald", 152),
        ("Davis", 150),
        ("Ward", 150),
        ("Cameron", 149),
        ("Wood", 149),
        ("MacDonald", 148),
        ("Reid", 140),
        ("Cook", 138),
        ("Bailey", 137),
        ("Adams", 136),
        ("Mason", 136),
        ("Baker", 135),
        ("Green", 134),
        ("Jensen", 134),
        ("Parker", 132),
        ("Neal", 131),
        ("Russell", 131),
        ("Carter", 128),
        ("Allen", 127),
        ("Roberts", 127),
        ("Knight", 126),
        ("Morgan", 126),
        ("Murphy", 126),
        ("Miller", 124),
        ("Morris", 124),
        ("McKay", 122),
        ("Morrison", 121),
        ("Wallace", 121),
        ("Stevens", 119),
        ("Johnston", 113),
        ("Jenkins", 111),
        ("Lewis", 110),
        ("Davies", 109),
        ("Oliver", 109),
        ("Ryan", 109),
        ("Marshall", 108),
        ("Webb", 108),
        ("Patchett", 107),
        ("Hughes", 106),
        ("Graham", 104),
        ("Wells", 104),
        ("Harrison", 103),
        ("Larsen", 103),
        ("Matthews", 103),
        ("Phillips", 102),
        ("Clarke", 100),
        ("Gibson", 99),
        ("Lucas", 99),
        ("Price", 97),
        ("O'Sullivan", 96),
        ("Barnes", 94),
        ("Gardiner", 92),
        ("Richards", 91),
        ("Boyce", 90),
        ("Duncan", 89),
        ("Fisher", 89),
        ("Gill", 89),
        ("O'Brien", 89),
        ("Gordon", 88),
        ("Olsen", 88),
        ("Powell", 86),
        ("Black", 85),
        ("Kennedy", 85),
        ("Dixon", 84),
        ("Jamieson", 84),
        ("O'Connor", 84),
        ("Sinclair", 84),
        ("Perry", 83),
        ("Williamson", 83),
        ("Day", 82),
        ("Pedersen", 81),
        ("Currie", 80),
        ("Grant", 80),
        ("Rush", 80),
        ("McEwen", 79),
        ("Wilton", 79),
        ("Kelly", 78),
        ("Nicholson", 77),
        ("Coleman", 76),
        ("Davidson", 76),
        ("Gardner", 76),
        ("Saunders", 76),
        ("Rogers", 75),
        ("Bryant", 74),
        ("Ferguson", 74),
        ("Ford", 73),
        ("Fowler", 73),
        ("McLean", 73),
        ("Holland", 72),
        ("Lloyd", 72),
        ("Page", 72),
        ("Francis", 71),
        ("Smart", 71),
        ("Weston", 71),
        ("Chapman", 70),
        ("Crawford", 70),
        ("Shaw", 70),
        ("Sullivan", 70),
        ("Webster", 70),
        ("Millar", 69),
        ("Burton", 68),
        ("Fuller", 68),
        ("Hamilton", 68),
        ("West", 68),
        ("Burns", 67),
        ("Cox", 67),
        ("Cresswell", 67),
        ("Holdaway", 67),
        ("Hodson", 66),
        ("Kerr", 66),
        ("Brooks", 64),
        ("Fletcher", 64),
        ("McCallum", 64),
        ("Allan", 63),
        ("Buchanan", 63),
        ("Carr", 63),
        ("Lee", 63),
        ("Pickering", 63),
        ("Pope", 63),
        ("Rowe", 63),
        ("Woolley", 63),
        ("McLeod", 62),
        ("Barnett", 61),
        ("Berry", 61),
        ("Lane", 61),
        ("Tapp", 61),
        ("Bartlett", 60),
        ("Elliott", 60),
        ("Pearson", 60),
        ("Wilkinson", 60),
        ("Atkinson", 59),
        ("Butler", 59),
        ("Douglas", 59),
        ("Pratt", 59),
        ("Cole", 58),
        ("Hayward", 58),
        ("Little", 58),
        ("Newman", 58),
        ("Simmons", 58),
        ("Barrett", 57),
        ("Cooksley", 57),
        ("Freeman", 57),
        ("Higgins", 57),
        ("Hope", 57),
        ("McGregor", 57),
        ("McMillan", 57),
        ("Rose", 57),
        ("Sutton", 57),
        ("Wong", 57),
        ("Harper", 56),
        ("Osborne", 56),
        ("Stevenson", 56),
        ("Bird", 55),
        ("Boyd", 55),
        ("Dick", 55),
        ("Field", 55),
        ("Greer", 55),
        ("Greig", 55),
        ("Nielsen", 55),
        ("Reynolds", 55),
        ("Forrest", 54),
        ("Bradley", 53),
        ("Gibbons", 53),
        ("Howard", 53),
        ("MacKenzie", 53),
        ("Nelson", 53),
        ("Todd", 53),
        ("Waters", 53),
        ("Ball", 52),
        ("Davey", 52),
        ("Holmes", 52),
        ("Rodgers", 52),
        ("Stratford", 52),
        ("Griffiths", 51),
        ("Small", 51),
        ("Watt", 51),
        ("Andrew", 50),
        ("Bishop", 50),
        ("Dunn", 50),
        ("Goodwin", 50),
        ("Gore", 50),
        ("Healy", 50),
        ("May", 50),
        ("Munro", 50),
        ("Parsons", 50),
        ("Poole", 50),
        ("Watts", 50),
        ("Hills", 49),
        ("Peters", 49),
        ("Vercoe", 49),
        ("Armstrong", 48),
        ("Bright", 48),
        ("Burgess", 48),
        ("Collis", 48),
        ("O'Neill", 48),
        ("Spencer", 48),
        ("Ritchie", 47),
        ("Alexander", 46),
        ("Curtis", 46),
        ("Freeth", 46),
        ("Nicol", 46),
        ("Robson", 46),
        ("Satherley", 46),
        ("Stuart", 46),
        ("Waugh", 46),
        ("Woods", 46),
        ("Coley", 45),
        ("Fitzgerald", 45),
        ("Fleming", 45),
        ("Herd", 45),
        ("Morton", 45),
        ("Beattie", 44),
        ("Clifford", 44),
        ("Costello", 44),
        ("Dawson", 44),
        ("Donaldson", 44),
        ("Fox", 44),
        ("Hay", 44),
        ("Jellyman", 44),
        ("Joe", 44),
        ("Johansen", 44),
        ("Knowles", 44),
        ("Lawson", 44),
        ("O'Donnell", 44),
        ("Patterson", 44),
        ("Payne", 44),
        ("Read", 44),
        ("Casey", 43),
        ("Chandler", 43),
        ("Donald", 43),
        ("Gilchrist", 43),
        ("Hyde", 43),
        ("McIntosh", 43),
        ("Paton", 43),
        ("Robb", 43),
        ("Rutherford", 43),
        ("Pike", 42),
        ("Dillon", 41),
        ("Drummond", 41),
        ("Hickey", 41),
        ("Hooper", 41),
        ("Jordan", 41),
        ("Judd", 41),
        ("Kenny", 41),
        ("Low", 41),
        ("Marfell", 41),
        ("Newton", 41),
        ("O'Leary", 41),
        ("Tucker", 41),
        ("Carson", 40),
        ("Dean", 40),
        ("Dickson", 40),
        ("George", 40),
        ("Ham", 40),
        ("McCarthy", 40),
        ("McIntyre", 40),
        ("Moran", 40),
        ("O'Connell", 40),
        ("Parkes", 40),
        ("Short", 40),
        ("Barr", 39),
        ("Baxter", 39),
        ("Dalton", 39),
        ("Forbes", 39),
        ("Hawkins", 39),
        ("Ireland", 39),
        ("Miles", 39),
        ("Nash", 39),
        ("Owen", 39),
        ("Perano", 39),
        ("Sowman", 39),
        ("Whyte", 39),
        ("Bush", 38),
        ("Drake", 38),
        ("Eden", 38),
        ("Giles", 38),
        ("Hoare", 38),
        ("Hubbard", 38),
        ("Hudson", 38),
        ("MacKay", 38),
        ("McKinnon", 38),
        ("Mears", 38),
        ("Prentice", 38),
        ("Schwass", 38),
        ("Simonsen", 38),
        ("Walton", 38),
        ("Wheeler", 38),
        ("Wratt", 38),
        ("Avery", 37),
        ("Barker", 37),
        ("Blake", 37),
        ("Conway", 37),
        ("Holloway", 37),
        ("Horton", 37),
        ("Manning", 37),
        ("Nolan", 37),
        ("Pritchard", 37),
        ("Bishell", 36),
        ("Blair", 36),
        ("Christiansen", 36),
        ("Fulton", 36),
        ("Gibbs", 36),
        ("Griffin", 36),
        ("Hook", 36),
        ("McGill", 36),
        ("Mercer", 36),
        ("Middleton", 36),
        ("Rayner", 36),
        ("Stone", 36),
        ("Terry", 36),
        ("Walsh", 36),
        ("Craig", 35),
        ("Craven", 35),
        ("Ellery", 35),
        ("Findlay", 35),
        ("Maxwell", 35),
        ("North", 35),
        ("Reardon", 35),
        ("Tait", 35),
        ("Baldwin", 34),
        ("Butcher", 34),
        ("Caldwell", 34),
        ("Doyle", 34),
        ("Eaton", 34),
        ("Flood", 34),
        ("Gifford", 34),
        ("Guy", 34),
        ("Jennings", 34),
        ("Leslie", 34),
        ("McMahon", 34),
        ("McNabb", 34),
        ("Paterson", 34),
        ("Porter", 34),
        ("Reeves", 34),
        ("Seymour", 34),
        ("Trask", 34),
        ("Warren", 34),
        ("Watkins", 34),
        ("Wills", 34),
        ("Best", 33),
        ("Bull", 33),
        ("Dawick", 33),
        ("Dobson", 33),
        ("Gledhill", 33),
        ("Hardy", 33),
        ("Hayes", 33),
        ("Kendall", 33),
        ("McCormick", 33),
        ("McPherson", 33),
        ("Pollard", 33),
        ("Rasmussen", 33),
        ("Shailer", 33),
        ("Shepherd", 33),
        ("Sheridan", 33),
        ("Simmonds", 33),
        ("Steele", 33),
        ("Booth", 32),
        ("Edmonds", 32),
        ("Gunn", 32),
        ("Hood", 32),
        ("Humphrey", 32),
        ("Hutchinson", 32),
        ("Laurenson", 32),
        ("Long", 32),
        ("Lowe", 32),
        ("Manson", 32),
        ("McGrath", 32),
        ("McKenna", 32),
        ("Muir", 32),
        ("O'Keefe", 32),
        ("Potter", 32),
        ("Searle", 32),
        ("Stubbs", 32),
        ("Wall", 32),
        ("Wallis", 32),
        ("Browne", 31),
        ("Carroll", 31),
        ("Cunningham", 31),
        ("Foley", 31),
        ("Franklin", 31),
        ("Furness", 31),
        ("Gilbert", 31),
        ("Hopkins", 31),
        ("Jefferies", 31),
        ("Johnstone", 31),
        ("Linton", 31),
        ("Mann", 31),
        ("Norton", 31),
        ("Rees", 31),
        ("Rowlands", 31),
        ("Sanders", 31),
        ("Bond", 30),
        ("Chambers", 30),
        ("Cragg", 30),
        ("Davison", 30),
        ("Gee", 30),
        ("Gleeson", 30),
        ("Gullery", 30),
        ("Hadfield", 30),
        ("Haines", 30),
        ("Hepburn", 30),
        ("Howell", 30),
        ("Jeffries", 30),
        ("Lamb", 30),
        ("Law", 30),
        ("MacPherson", 30),
        ("McIsaac", 30),
        ("Millard", 30),
        ("Paul", 30),
        ("Pearce", 30),
        ("Prouse", 30),
        ("Ramsay", 30),
        ("Rowland", 30),
        ("Spelman", 30),
        ("Waghorn", 30),
        ("Willis", 30),
        ("Zimmerman", 30),
        ("Aitken", 29),
        ("Booker", 29),
        ("Bruce", 29),
        ("Burrell", 29),
        ("Burt", 29),
        ("Funnell", 29),
        ("Gilmore", 29),
        ("Guthrie", 29),
        ("Hewitt", 29),
        ("Hogg", 29),
        ("Lammas", 29),
        ("Lang", 29),
        ("Lyons", 29),
        ("McDowall", 29),
        ("Neilson", 29),
        ("Norman", 29),
        ("Reed", 29),
        ("Rickard", 29),
        ("Stokes", 29),
        ("Stratton", 29),
        ("Strawbridge", 29),
        ("York", 29),
        ("Alve", 28),
        ("Baldick", 28),
        ("Banks", 28),
        ("Beard", 28),
        ("Bowden", 28),
        ("Boyle", 28),
        ("Carpenter", 28),
        ("Connolly", 28),
        ("Cooke", 28),
        ("Craw", 28),
        ("Cumming", 28),
        ("Drew", 28),
        ("Fairhall", 28),
        ("Gillespie", 28),
        ("Gillies", 28),
        ("Healey", 28),
        ("Horn", 28),
        ("Ingram", 28),
        ("Knox", 28),
        ("Lancaster", 28),
        ("Landon-Lane", 28),
        ("Marsh", 28),
        ("Mortimer", 28),
        ("Riley", 28),
        ("Sixtus", 28),
        ("Turnbull", 28),
        ("Warner", 28),
        ("Aldridge", 27),
        ("Allerby", 27),
        ("Arnold", 27),
        ("Blackwell", 27),
        ("Blick", 27),
        ("Boon", 27),
        ("Bowater", 27),
        ("Broughan", 27),
        ("Davenport", 27),
        ("Foote", 27),
        ("Forsyth", 27),
        ("Laing", 27),
        ("Mayo", 27),
        ("McFarlane", 27),
        ("McMurray", 27),
        ("Monk", 27),
        ("Orr", 27),
        ("Procter", 27),
        ("Shannon", 27),
        ("Southee", 27),
        ("Stace", 27),
        ("Waller", 27),
        ("Webby", 27),
        ("Arnott", 26),
        ("Baird", 26),
        ("Bary", 26),
        ("Bassett", 26),
        ("Buckley", 26),
        ("Burke", 26),
        ("Claridge", 26),
        ("Clunies-Ross", 26),
        ("Croad", 26),
        ("Dyer", 26),
        ("Ewart", 26),
        ("Faulkner", 26),
        ("Fenton", 26),
        ("Gibb", 26),
        ("Huddleston", 26),
        ("Jarvis", 26),
        ("Kay", 26),
        ("Kemp", 26),
        ("McLachlan", 26),
        ("Middlemiss", 26),
        ("Moody", 26),
        ("Mudgway", 26),
        ("Nicholas", 26),
        ("Reader", 26),
        ("Robert", 26),
        ("Steer", 26),
        ("Thornton", 26),
        ("Toms", 26),
        ("Twidle", 26),
        ("Vincent", 26),
        ("Way", 26),
        ("Whittaker", 26),
        ("Batchelar", 25),
        ("Boniface", 25),
        ("Botham", 25),
        ("Buick", 25),
        ("Burnett", 25),
        ("Ching", 25),
        ("Christie", 25),
        ("Corlett", 25),
        ("Coutts", 25),
        ("Eglinton", 25),
        ("Enright", 25),
        ("Foot", 25),
        ("Frost", 25),
        ("Gaskin", 25),
        ("Hanson", 25),
        ("Hardie", 25),
        ("Henry", 25),
        ("Hoskins", 25),
        ("Lambert", 25),
        ("Learmonth", 25),
        ("Logan", 25),
        ("Matheson", 25),
        ("McManaway", 25),
        ("Meads", 25),
        ("Meredith", 25),
        ("Montgomery", 25),
        ("Murdoch", 25),
        ("Orchard", 25),
        ("Perrin", 25),
        ("Peterson", 25),
        ("Priest", 25),
        ("Rossiter", 25),
        ("Shand", 25),
        ("Skinner", 25),
        ("Soper", 25),
        ("Street", 25),
        ("Tanner", 25),
        ("Aberhart", 24),
        ("Berkahn", 24),
        ("Burr", 24),
        ("Cairns", 24),
        ("Corbett", 24),
        ("Dalziel", 24),
        ("Doherty", 24),
        ("Esson", 24),
        ("Farland", 24),
        ("Godfrey", 24),
        ("Guard", 24),
        ("Hume", 24),
        ("Irving", 24),
        ("Jacques", 24),
        ("Kirk", 24),
        ("Love", 24),
        ("Lyon", 24),
    ))
