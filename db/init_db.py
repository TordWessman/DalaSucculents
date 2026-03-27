#!/usr/bin/env python3
"""Create and seed the Dala Succulents SQLite database with plant-centric schema."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'dala.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')


def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()

    # Apply schema
    with open(SCHEMA_PATH, 'r') as f:
        c.executescript(f.read())

    # --- Genera ---
    genera = [
        ('Adenia', 'Passifloraceae', 'adenia'),
        ('Ariocarpus', 'Cactaceae', 'ariocarpus'),
        ('Echeveria', 'Crassulaceae', 'echeveria'),
        ('Euphorbia', 'Euphorbiaceae', 'euphorbia'),
        ('Haworthia', 'Asphodelaceae', 'haworthia'),
    ]
    c.executemany(
        'INSERT INTO genera (name, family, slug) VALUES (?, ?, ?)', genera
    )

    # --- Countries ---
    countries = [
        ('ETH', 'Ethiopia', 'ET'),
        ('KEN', 'Kenya', 'KE'),
        ('SOM', 'Somalia', 'SO'),
        ('TZA', 'Tanzania', 'TZ'),
        ('MEX', 'Mexico', 'MX'),
        ('ZAF', 'South Africa', 'ZA'),
        ('MOZ', 'Mozambique', 'MZ'),
        ('NAM', 'Namibia', 'NA'),
    ]
    c.executemany(
        'INSERT INTO countries (alpha3, name, alpha2) VALUES (?, ?, ?)',
        countries,
    )

    # Build genus name→id lookup
    genus_ids = {}
    for row in c.execute('SELECT id, name FROM genera'):
        genus_ids[row[1]] = row[0]

    # --- Plants ---
    # (slug, genus, species, subspecies, variety, form, cultivar,
    #  field_number, field_location, author_citation,
    #  vegetation_period, substrate, winter_temp_range, watering, exposure,
    #  red_list_status, red_list_url, cites_listing, llifle_url,
    #  notes, sort_order)
    plants_data = [
        (
            'adenia-globosa', 'Adenia', 'globosa', None, None, None, None,
            None, None, 'Engl.',
            'Summer', 'Humus-rich succulent mix', '>15 °C', '💧💧💧',
            'Full sun to partial shade',
            'Least concern (LC)',
            'https://www.iucnredlist.org/species/185781/115744672',
            'None', 'http://www.llifle.com/Encyclopedia/SUCCULENTS/Family/Passifloraceae/33797/Adenia_globosa',
            None, 1,
        ),
        (
            'adenia-glauca', 'Adenia', 'glauca', None, None, None, None,
            None, None, 'Schinz',
            'Summer', 'Well-draining succulent mix', '>12 °C', '💧💧',
            'Full sun to partial shade',
            'Least concern (LC)', None, 'None', None,
            None, 2,
        ),
        (
            'ariocarpus-retusus', 'Ariocarpus', 'retusus', None, None, None, None,
            None, None, 'Scheidw.',
            'Summer', 'Mineral mix with limestone chips', '>5 °C', '💧',
            'Full sun',
            'Endangered (EN)',
            'https://www.iucnredlist.org/species/40822/121491625',
            'Appendix I',
            'http://www.llifle.com/Encyclopedia/CACTI/Family/Cactaceae/1226/Ariocarpus_retusus',
            'Extremely slow-growing. Requires excellent drainage.', 3,
        ),
        (
            'ariocarpus-fissuratus', 'Ariocarpus', 'fissuratus', None, None, None, None,
            'SB 430', 'Brewster County, Texas', '(Engelm.) K.Schum.',
            'Summer', 'Mineral mix with limestone chips', '>5 °C', '💧',
            'Full sun',
            'Vulnerable (VU)', None, 'Appendix I',
            'http://www.llifle.com/Encyclopedia/CACTI/Family/Cactaceae/1206/Ariocarpus_fissuratus',
            'Living rock cactus. Flat growth habit mimics surrounding stones.', 4,
        ),
        (
            'echeveria-laui', 'Echeveria', 'laui', None, None, None, None,
            None, None, 'Moran & J.Meyrán',
            'Summer', 'Well-draining succulent mix', '>5 °C', '💧💧',
            'Bright indirect light',
            'Critically endangered (CR)', None, 'None', None,
            'Highly sought after for its powdery blue-white farina.', 5,
        ),
        (
            'echeveria-agavoides', 'Echeveria', 'agavoides', None, None, None, None,
            None, None, 'Lem.',
            'Summer', 'Standard succulent mix', '>0 °C', '💧💧',
            'Full sun to bright indirect',
            'Least concern (LC)', None, 'None',
            'http://www.llifle.com/Encyclopedia/SUCCULENTS/Family/Crassulaceae/18685/Echeveria_agavoides',
            None, 6,
        ),
        (
            'euphorbia-obesa', 'Euphorbia', 'obesa', None, None, None, None,
            None, None, 'Hook.f.',
            'Summer', 'Mineral mix with perlite', '>10 °C', '💧',
            'Full sun',
            'Endangered (EN)',
            'https://www.iucnredlist.org/species/44392/121845853',
            'Appendix II',
            'http://www.llifle.com/Encyclopedia/SUCCULENTS/Family/Euphorbiaceae/8482/Euphorbia_obesa',
            'Baseball plant. Dioecious — male and female flowers on separate plants.', 7,
        ),
        (
            'euphorbia-horrida', 'Euphorbia', 'horrida', None, None, None, None,
            None, None, 'Boiss.',
            'Summer', 'Mineral mix', '>5 °C', '💧💧',
            'Full sun',
            'Least concern (LC)', None, 'Appendix II', None,
            None, 8,
        ),
        (
            'haworthia-cooperi', 'Haworthia', 'cooperi', None, 'truncata', None, None,
            None, None, 'Baker',
            'Winter', 'Humus-rich mineral mix', '>5 °C', '💧💧',
            'Bright indirect light',
            'Least concern (LC)', None, 'None',
            'http://www.llifle.com/Encyclopedia/SUCCULENTS/Family/Aloaceae/27236/Haworthia_cooperi',
            'Translucent leaf windows allow light into interior tissues.', 9,
        ),
        (
            'haworthia-truncata', 'Haworthia', 'truncata', None, None, None, None,
            None, None, 'Schönland',
            'Winter', 'Mineral mix with pumice', '>5 °C', '💧💧',
            'Bright indirect light',
            'Vulnerable (VU)', None, 'None', None,
            'Grows in fan-shaped arrangement. Leaves appear sliced off at tips.', 10,
        ),
    ]

    for p in plants_data:
        c.execute(
            '''INSERT INTO plants
               (slug, genus_id, species, subspecies, variety, form, cultivar,
                field_number, field_location, author_citation,
                vegetation_period, substrate, winter_temp_range, watering, exposure,
                red_list_status, red_list_url, cites_listing, llifle_url,
                notes, sort_order)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (p[0], genus_ids[p[1]], p[2], p[3], p[4], p[5], p[6],
             p[7], p[8], p[9],
             p[10], p[11], p[12], p[13], p[14],
             p[15], p[16], p[17], p[18],
             p[19], p[20]),
        )

    # Build plant slug→id lookup
    plant_ids = {}
    for row in c.execute('SELECT id, slug FROM plants'):
        plant_ids[row[1]] = row[0]

    # --- Plant ↔ Country relationships ---
    plant_countries = [
        ('adenia-globosa', ['ETH', 'KEN', 'SOM', 'TZA']),
        ('adenia-glauca', ['ZAF', 'NAM', 'MOZ']),
        ('ariocarpus-retusus', ['MEX']),
        ('ariocarpus-fissuratus', ['MEX']),
        ('echeveria-laui', ['MEX']),
        ('echeveria-agavoides', ['MEX']),
        ('euphorbia-obesa', ['ZAF']),
        ('euphorbia-horrida', ['ZAF']),
        ('haworthia-cooperi', ['ZAF']),
        ('haworthia-truncata', ['ZAF']),
    ]
    for slug, codes in plant_countries:
        pid = plant_ids[slug]
        for code in codes:
            c.execute(
                'INSERT INTO plant_countries (plant_id, country_alpha3) VALUES (?, ?)',
                (pid, code),
            )

    # --- Specimens ---
    # (plant_slug, specimen_code, specimen_suffix, for_sale, price, notes,
    #  propagation_date, propagation_method, specimen_origin,
    #  source_material_origin, provenance, image_url)
    specimens_data = [
        ('adenia-globosa', '0001-26s01', '26s01', 0, None,
         None, '2026-01-04', 'Seed', None, None, None, None),
        ('adenia-globosa', '0001-25c01', '25c01', 1, 35.00,
         'Rooted cutting, well-established', '2025-06-15', 'Cutting',
         None, None, None, None),
        ('ariocarpus-retusus', '0003-24s01', '24s01', 0, None,
         None, '2024-03-10', 'Seed', None, None, None, None),
        ('ariocarpus-retusus', '0003-24s02', '24s02', 1, 85.00,
         'Three-year seedling, well-rooted', '2024-03-10', 'Seed',
         None, None, None, None),
        ('echeveria-laui', '0005-25c01', '25c01', 1, 45.00,
         'Offset with intact farina', '2025-09-01', 'Offset',
         None, None, None, None),
        ('euphorbia-obesa', '0007-23s01', '23s01', 0, None,
         'Male specimen', '2023-07-20', 'Seed', None, None, None, None),
        ('euphorbia-obesa', '0007-23s02', '23s02', 1, 29.99,
         'Female specimen, flowering size', '2023-07-20', 'Seed',
         None, None, None, None),
        ('haworthia-cooperi', '0009-25d01', '25d01', 1, 18.50,
         'Division from mother plant', '2025-04-12', 'Division',
         None, None, None, None),
    ]

    for s in specimens_data:
        c.execute(
            '''INSERT INTO specimens
               (plant_id, specimen_code, specimen_suffix, for_sale, price, notes,
                propagation_date, propagation_method, specimen_origin,
                source_material_origin, provenance, image_url)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (plant_ids[s[0]], s[1], s[2], s[3], s[4], s[5],
             s[6], s[7], s[8], s[9], s[10], s[11]),
        )

    conn.commit()
    conn.close()
    print(f"Database created at {os.path.abspath(DB_PATH)}")
    print(f"  Genera: {len(genera)}")
    print(f"  Countries: {len(countries)}")
    print(f"  Plants: {len(plants_data)}")
    print(f"  Specimens: {len(specimens_data)}")


if __name__ == '__main__':
    init_db()
