#!/usr/bin/env python3
"""
Script d'initialisation complet de la base de données
Création des tables et insertion des données de test
"""

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import hashlib
import uuid
from datetime import datetime, timedelta
import random

#load_dotenv()

class DatabaseInitializer:
    """Initialiseur de base de données"""
    
    def __init__(self):
        self.config = {
            'host': 'ecocapital-mbfdm.c.aivencloud.com',
            'port': '14431',
            'database': 'crm_db',
            'user': 'avnadmin',
            'password': 'AVNS_3a2plzaevzttmJ4Tcs9',
            'use_pure': True
        }
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Établit la connexion"""
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor()
            print("✅ Connexion établie")
            return True
        except Error as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    def disconnect(self):
        """Ferme la connexion"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("🔌 Connexion fermée")
    
    def create_tables(self):
        """Crée toutes les tables"""
        print("\n📦 Création des tables...")
        
        # Table users
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(255) PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            role VARCHAR(50) DEFAULT 'user',
            phone VARCHAR(50),
            department VARCHAR(100),
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_email (email),
            INDEX idx_role (role)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        print("  ✅ Table users créée")
        
        # Table leads
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id VARCHAR(255) PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            phone VARCHAR(50),
            company VARCHAR(255),
            status VARCHAR(50) DEFAULT 'Nouveau',
            source VARCHAR(100),
            interest_level INT DEFAULT 5,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user (user_id),
            INDEX idx_status (status),
            INDEX idx_created (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        print("  ✅ Table leads créée")
        
        # Table prospects
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS prospects (
            id VARCHAR(255) PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            phone VARCHAR(50),
            company VARCHAR(255),
            status VARCHAR(50) DEFAULT 'Nouveau',
            source VARCHAR(100),
            interest_level INT DEFAULT 5,
            notes TEXT,
            next_follow_up DATETIME,
            follow_up_strategy TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user (user_id),
            INDEX idx_next_follow_up (next_follow_up)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        print("  ✅ Table prospects créée")
        
        # Table customers
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id VARCHAR(255) PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            phone VARCHAR(50),
            company VARCHAR(255),
            address TEXT,
            industry VARCHAR(100),
            revenue DECIMAL(15,2),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user (user_id),
            INDEX idx_industry (industry)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        print("  ✅ Table customers créée")
        
        # Table appointments
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id VARCHAR(255) PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            appointment_date DATETIME NOT NULL,
            duration INT DEFAULT 60,
            location VARCHAR(255),
            status VARCHAR(50) DEFAULT 'Planifié',
            customer_id VARCHAR(255),
            customer_name VARCHAR(255),
            customer_company VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
            INDEX idx_user (user_id),
            INDEX idx_appointment_date (appointment_date),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        print("  ✅ Table appointments créée")
        
        # Table sessions
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id VARCHAR(255) PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            token VARCHAR(500) NOT NULL,
            device_info TEXT,
            expires_at DATETIME NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_token (token(255)),
            INDEX idx_expires (expires_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        print("  ✅ Table sessions créée")
        
        self.conn.commit()
        print("✅ Toutes les tables ont été créées")
    
    def insert_test_data(self):
        """Insère des données de test"""
        print("\n📊 Insertion des données de test...")
        
        # Création des utilisateurs
        users = [
            {
                'id': str(uuid.uuid4()),
                'email': 'admin@agc-vie.com',
                'name': 'Admin System',
                'role': 'admin',
                'password': 'admin123'
            },
            {
                'id': str(uuid.uuid4()),
                'email': 'commercial1@agc-vie.com',
                'name': 'Jean Dupont',
                'role': 'commercial',
                'phone': '0612345678',
                'department': 'Ventes',
                'password': 'commercial123'
            },
            {
                'id': str(uuid.uuid4()),
                'email': 'commercial2@agc-vie.com',
                'name': 'Marie Martin',
                'role': 'commercial',
                'phone': '0687654321',
                'department': 'Ventes',
                'password': 'commercial123'
            }
        ]
        
        for user in users:
            password_hash = hashlib.sha256(user['password'].encode()).hexdigest()
            self.cursor.execute("""
            INSERT IGNORE INTO users (id, email, name, role, phone, department, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                user['id'],
                user['email'],
                user['name'],
                user['role'],
                user.get('phone'),
                user.get('department'),
                password_hash
            ))
        
        print("  ✅ Utilisateurs créés")
        
        # Récupération des IDs utilisateurs
        self.cursor.execute("SELECT id FROM users")
        user_ids = [row[0] for row in self.cursor.fetchall()]
        
        # Création des leads de test
        lead_statuses = ['Nouveau', 'En contact', 'Qualifié']
        companies = ['TechCorp', 'Innovation SAS', 'Digital Factory', 'Smart Solutions', 'Future Lab']
        first_names = ['Pierre', 'Paul', 'Jacques', 'Sophie', 'Julie', 'Thomas', 'Nicolas']
        last_names = ['Martin', 'Bernard', 'Dubois', 'Thomas', 'Robert', 'Richard', 'Petit']
        
        for i in range(30):
            lead_id = str(uuid.uuid4())
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            email = f"{name.lower().replace(' ', '.')}@example.com"
            phone = f"0{random.randint(6,7)}{random.randint(10,99)}{random.randint(10,99)}{random.randint(10,99)}{random.randint(10,99)}"
            company = random.choice(companies)
            status = random.choice(lead_statuses)
            interest = random.randint(1, 5)
            created_at = datetime.now() - timedelta(days=random.randint(1, 90))
            user_id = random.choice(user_ids)
            
            self.cursor.execute("""
            INSERT INTO leads (id, user_id, name, email, phone, company, status, interest_level, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (lead_id, user_id, name, email, phone, company, status, interest, created_at))
        
        print("  ✅ Leads de test créés")
        
        # Création des prospects
        prospect_statuses = ['Nouveau', 'En cours', 'À relancer', 'Chaud']
        
        for i in range(25):
            prospect_id = str(uuid.uuid4())
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            email = f"{name.lower().replace(' ', '.')}@example.com"
            phone = f"0{random.randint(6,7)}{random.randint(10,99)}{random.randint(10,99)}{random.randint(10,99)}{random.randint(10,99)}"
            company = random.choice(companies)
            status = random.choice(prospect_statuses)
            interest = random.randint(1, 5)
            next_follow_up = datetime.now() + timedelta(days=random.randint(-5, 30))
            created_at = datetime.now() - timedelta(days=random.randint(1, 60))
            user_id = random.choice(user_ids)
            
            self.cursor.execute("""
            INSERT INTO prospects (id, user_id, name, email, phone, company, status, interest_level, next_follow_up, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (prospect_id, user_id, name, email, phone, company, status, interest, next_follow_up, created_at))
        
        print("  ✅ Prospects de test créés")
        
        # Création des clients
        industries = ['Technologie', 'Finance', 'Santé', 'Industrie', 'Services', 'Commerce']
        
        for i in range(20):
            customer_id = str(uuid.uuid4())
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            email = f"{name.lower().replace(' ', '.')}@example.com"
            phone = f"0{random.randint(6,7)}{random.randint(10,99)}{random.randint(10,99)}{random.randint(10,99)}{random.randint(10,99)}"
            company = random.choice(companies)
            industry = random.choice(industries)
            revenue = random.randint(50000, 5000000)
            created_at = datetime.now() - timedelta(days=random.randint(1, 365))
            user_id = random.choice(user_ids)
            
            self.cursor.execute("""
            INSERT INTO customers (id, user_id, name, email, phone, company, industry, revenue, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (customer_id, user_id, name, email, phone, company, industry, revenue, created_at))
        
        print("  ✅ Clients de test créés")
        
        # Création des rendez-vous
        appointment_titles = ['Démo produit', 'Négociation contrat', 'Suivi client', 'Présentation', 'Signature']
        
        for i in range(15):
            appointment_id = str(uuid.uuid4())
            title = random.choice(appointment_titles)
            appointment_date = datetime.now() + timedelta(days=random.randint(-15, 30), hours=random.randint(8, 18))
            duration = random.choice([30, 45, 60, 90, 120])
            status = random.choice(['Planifié', 'Confirmé'])
            user_id = random.choice(user_ids)
            
            self.cursor.execute("""
            INSERT INTO appointments (id, user_id, title, appointment_date, duration, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (appointment_id, user_id, title, appointment_date, duration, status, datetime.now()))
        
        print("  ✅ Rendez-vous de test créés")
        
        self.conn.commit()
        print("✅ Données de test insérées avec succès")
    
    def run(self):
        """Exécute l'initialisation complète"""
        print("🚀 Initialisation de la base de données CRM")
        print("=" * 50)
        
        if not self.connect():
            return False
        
        try:
            self.create_tables()
            self.insert_test_data()
            print("\n✅ Initialisation terminée avec succès!")
            return True
        except Error as e:
            print(f"\n❌ Erreur lors de l'initialisation: {e}")
            return False
        finally:
            self.disconnect()

if __name__ == "__main__":
    init = DatabaseInitializer()
    init.run()