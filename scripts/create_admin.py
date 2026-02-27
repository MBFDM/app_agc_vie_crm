import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import hashlib
import uuid
from datetime import datetime

#load_dotenv()

def create_admin_user():
    """Crée un utilisateur administrateur par défaut"""
    
    # Configuration de la connexion
    config = {
        'host': 'ecocapital-mbfdm.c.aivencloud.com',
        'port': '14431',
        'database': 'crm_db',
        'user': 'avnadmin',
        'password': 'AVNS_3a2plzaevzttmJ4Tcs9',
        'use_pure': True
    }
    
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Vérifier si l'utilisateur admin existe déjà
        cursor.execute("SELECT id FROM users WHERE email = 'admin@agc-vie.com'")
        existing = cursor.fetchone()
        
        if not existing:
            # Créer l'utilisateur admin
            admin_id = str(uuid.uuid4())
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()
            
            query = """
            INSERT INTO users (id, email, name, role, password_hash, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                admin_id,
                "admin@agc-vie.com",
                "Administrateur",
                "admin",
                password_hash,
                datetime.now()
            ))
            
            conn.commit()
            print("✅ Utilisateur admin créé avec succès!")
            print("📧 Email: admin@agc-vie.com")
            print("🔑 Mot de passe: admin123")
        else:
            print("ℹ️ L'utilisateur admin existe déjà")
        
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    create_admin_user()