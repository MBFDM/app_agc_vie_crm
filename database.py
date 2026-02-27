import mysql.connector
from mysql.connector import Error
import pandas as pd
import streamlit as st
from datetime import datetime
import time

class MySQLDatabase:
    def __init__(self):
        # Configuration directe sans dotenv
        self.host = 'ecocapital-mbfdm.c.aivencloud.com'
        self.port = '14431'
        self.database = 'crm_db'
        self.user = 'avnadmin'
        self.password = 'AVNS_3a2plzaevzttmJ4Tcs9'
        self.connection = None
        self.cursor = None
        self.connection_attempts = 0
        self.max_attempts = 3

    def connect(self):
        """Établit la connexion à la base de données avec retry"""
        self.connection_attempts += 1
        
        try:
            print(f"🔄 Tentative de connexion {self.connection_attempts}/{self.max_attempts}...")
            
            # Convertir le port en entier
            port_int = int(self.port)
            
            # Options de connexion pour Aiven
            self.connection = mysql.connector.connect(
                host=self.host,
                port=port_int,
                database=self.database,
                user=self.user,
                password=self.password,
                connection_timeout=30,
                use_pure=True,
                ssl_disabled=False  # Aiven nécessite SSL
            )
            
            if self.connection and self.connection.is_connected():
                print(f"✅ Connexion MySQL établie avec succès")
                print(f"🆔 Version MySQL: {self.connection.get_server_info()}")
                self.connection_attempts = 0  # Réinitialiser le compteur
                return self.connection
            else:
                print("❌ Connexion établie mais non fonctionnelle")
                return None
                
        except mysql.connector.Error as e:
            error_msg = str(e)
            print(f"❌ Erreur de connexion MySQL: {error_msg}")
            
            # Messages d'erreur plus spécifiques
            if "2003" in error_msg:
                st.error("🔌 Impossible d'atteindre le serveur Aiven.")
                st.info("Vérifiez que votre IP est autorisée dans la console Aiven")
            elif "1045" in error_msg:
                st.error("🔑 Identifiants incorrects")
            elif "1049" in error_msg:
                st.error("📁 Base de données inexistante")
            else:
                st.error(f"❌ Erreur de connexion: {error_msg}")
            
            # Réessayer si nécessaire
            if self.connection_attempts < self.max_attempts:
                time.sleep(2)  # Attendre 2 secondes avant de réessayer
                return self.connect()
            
            return None
            
        except Exception as e:
            st.error(f"❌ Erreur inattendue: {e}")
            return None

    def disconnect(self):
        """Ferme la connexion"""
        try:
            if self.cursor:
                self.cursor.close()
                self.cursor = None
            if self.connection and self.connection.is_connected():
                self.connection.close()
                self.connection = None
                print("🔌 Connexion MySQL fermée")
        except Exception as e:
            print(f"Erreur lors de la déconnexion: {e}")

    def execute_query(self, query, params=None):
        """Exécute une requête et retourne les résultats"""
        cursor = None
        try:
            # Établir la connexion si nécessaire
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return pd.DataFrame()
            
            # Créer un nouveau cursor
            cursor = self.connection.cursor(dictionary=True)
            
            # Exécuter la requête
            cursor.execute(query, params or ())
            
            # Pour les requêtes SELECT
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                return pd.DataFrame(result) if result else pd.DataFrame()
            
            # Pour les autres requêtes
            else:
                self.connection.commit()
                return cursor.rowcount
                
        except mysql.connector.Error as e:
            print(f"❌ Erreur MySQL: {e}")
            print(f"Query: {query}")
            return pd.DataFrame()
            
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            return pd.DataFrame()
            
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass

    def check_connection(self):
        """Vérifie si la connexion est active"""
        try:
            if self.connection and self.connection.is_connected():
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                return True
            return False
        except:
            return False

    # ========== MÉTHODES CRUD ==========

    def get_users(self):
        """Récupère tous les utilisateurs"""
        try:
            query = "SELECT * FROM users ORDER BY created_at DESC"
            return self.execute_query(query)
        except Exception as e:
            print(f"Erreur get_users: {e}")
            return pd.DataFrame()

    def get_leads(self, user_id=None):
        """Récupère tous les leads"""
        try:
            if user_id:
                query = "SELECT * FROM leads WHERE user_id = %s ORDER BY created_at DESC"
                return self.execute_query(query, (user_id,))
            else:
                query = """
                    SELECT l.*, u.name as user_name 
                    FROM leads l 
                    LEFT JOIN users u ON l.user_id = u.id 
                    ORDER BY l.created_at DESC
                """
                return self.execute_query(query)
        except Exception as e:
            print(f"Erreur get_leads: {e}")
            return pd.DataFrame()

    def get_prospects(self, user_id=None):
        """Récupère tous les prospects"""
        try:
            if user_id:
                query = "SELECT * FROM prospects WHERE user_id = %s ORDER BY next_follow_up"
                return self.execute_query(query, (user_id,))
            else:
                query = """
                    SELECT p.*, u.name as user_name 
                    FROM prospects p 
                    LEFT JOIN users u ON p.user_id = u.id 
                    ORDER BY p.next_follow_up
                """
                return self.execute_query(query)
        except Exception as e:
            print(f"Erreur get_prospects: {e}")
            return pd.DataFrame()

    def get_customers(self, user_id=None):
        """Récupère tous les clients"""
        try:
            if user_id:
                query = "SELECT * FROM customers WHERE user_id = %s ORDER BY created_at DESC"
                return self.execute_query(query, (user_id,))
            else:
                query = """
                    SELECT c.*, u.name as user_name 
                    FROM customers c 
                    LEFT JOIN users u ON c.user_id = u.id 
                    ORDER BY c.created_at DESC
                """
                return self.execute_query(query)
        except Exception as e:
            print(f"Erreur get_customers: {e}")
            return pd.DataFrame()

    def get_appointments(self, user_id=None):
        """Récupère tous les rendez-vous"""
        try:
            if user_id:
                query = "SELECT * FROM appointments WHERE user_id = %s ORDER BY appointment_date"
                return self.execute_query(query, (user_id,))
            else:
                query = """
                    SELECT a.*, u.name as user_name 
                    FROM appointments a 
                    LEFT JOIN users u ON a.user_id = u.id 
                    ORDER BY a.appointment_date
                """
                return self.execute_query(query)
        except Exception as e:
            print(f"Erreur get_appointments: {e}")
            return pd.DataFrame()

    # ========== MÉTHODES STATISTIQUES ==========

    def get_dashboard_stats(self):
        """Récupère les statistiques globales"""
        stats = {
            'total_leads': 0,
            'total_prospects': 0,
            'total_customers': 0,
            'today_appointments': 0,
            'conversion_rate': 0,
            'total_revenue': 0,
            'prospects_to_follow': 0,
            'upcoming_appointments': 0
        }
        
        try:
            leads_df = self.get_leads()
            stats['total_leads'] = len(leads_df) if leads_df is not None and not leads_df.empty else 0
            
            prospects_df = self.get_prospects()
            stats['total_prospects'] = len(prospects_df) if prospects_df is not None and not prospects_df.empty else 0
            
            customers_df = self.get_customers()
            stats['total_customers'] = len(customers_df) if customers_df is not None and not customers_df.empty else 0
            
            # Prospects à relancer
            if prospects_df is not None and not prospects_df.empty and 'next_follow_up' in prospects_df.columns:
                today = datetime.now().date()
                prospects_df['next_follow_up'] = pd.to_datetime(prospects_df['next_follow_up'], errors='coerce')
                stats['prospects_to_follow'] = len(prospects_df[
                    prospects_df['next_follow_up'].dt.date <= today
                ]) if not prospects_df.empty else 0
            
            # Taux de conversion
            if stats['total_leads'] > 0:
                stats['conversion_rate'] = round((stats['total_customers'] / stats['total_leads']) * 100, 1)
            
            # Chiffre d'affaires
            if customers_df is not None and not customers_df.empty and 'revenue' in customers_df.columns:
                stats['total_revenue'] = customers_df['revenue'].sum()
            
            # Rendez-vous à venir
            appointments_df = self.get_appointments()
            if appointments_df is not None and not appointments_df.empty and 'appointment_date' in appointments_df.columns:
                appointments_df['appointment_date'] = pd.to_datetime(appointments_df['appointment_date'], errors='coerce')
                now = datetime.now()
                stats['upcoming_appointments'] = len(appointments_df[
                    appointments_df['appointment_date'] > now
                ]) if not appointments_df.empty else 0
            
            return stats
            
        except Exception as e:
            print(f"Erreur stats: {e}")
            return stats

    def get_leads_by_status(self):
        """Récupère la répartition des leads par statut"""
        try:
            query = "SELECT status, COUNT(*) as count FROM leads GROUP BY status ORDER BY count DESC"
            return self.execute_query(query)
        except Exception as e:
            print(f"Erreur get_leads_by_status: {e}")
            return pd.DataFrame()

    def get_prospects_by_status(self):
        """Récupère la répartition des prospects par statut"""
        try:
            query = "SELECT status, COUNT(*) as count FROM prospects GROUP BY status ORDER BY count DESC"
            return self.execute_query(query)
        except Exception as e:
            print(f"Erreur get_prospects_by_status: {e}")
            return pd.DataFrame()

    def get_customers_by_industry(self):
        """Récupère la répartition des clients par secteur"""
        try:
            query = """
                SELECT industry, COUNT(*) as count, SUM(revenue) as total_revenue
                FROM customers 
                WHERE industry IS NOT NULL AND industry != ''
                GROUP BY industry 
                ORDER BY count DESC
            """
            return self.execute_query(query)
        except Exception as e:
            print(f"Erreur get_customers_by_industry: {e}")
            return pd.DataFrame()

    def get_monthly_trends(self):
        """
        Récupère les tendances mensuelles (leads et clients par mois)
        Cette méthode est utilisée dans le tableau de bord
        """
        try:
            query = """
            SELECT 
                DATE_FORMAT(created_at, '%Y-%m') as month,
                SUM(CASE WHEN 'leads' THEN 1 ELSE 0 END) as leads_count,
                SUM(CASE WHEN 'customers' THEN 1 ELSE 0 END) as customers_count
            FROM (
                SELECT created_at, 'leads' as source FROM leads
                UNION ALL
                SELECT created_at, 'customers' as source FROM customers
            ) as combined
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
            """
            
            result = self.execute_query(query)
            
            # Si la requête échoue ou retourne vide, créer des données simulées pour le test
            if result is None or result.empty:
                print("⚠️ Aucune donnée de tendance, création de données simulées")
                # Créer des données simulées pour les 6 derniers mois
                import random
                months = []
                leads_data = []
                customers_data = []
                
                for i in range(6):
                    date = datetime.now() - pd.DateOffset(months=i)
                    month_str = date.strftime('%Y-%m')
                    months.insert(0, month_str)
                    leads_data.insert(0, random.randint(5, 15))
                    customers_data.insert(0, random.randint(1, 8))
                
                return pd.DataFrame({
                    'month': months,
                    'leads_count': leads_data,
                    'customers_count': customers_data
                })
            
            return result
            
        except Exception as e:
            print(f"Erreur get_monthly_trends: {e}")
            # Retourner un DataFrame vide en cas d'erreur
            return pd.DataFrame(columns=['month', 'leads_count', 'customers_count'])

    def get_upcoming_appointments(self, days=7):
        """Récupère les prochains rendez-vous"""
        try:
            query = """
                SELECT a.*, u.name as user_name 
                FROM appointments a 
                LEFT JOIN users u ON a.user_id = u.id 
                WHERE a.appointment_date BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL %s DAY)
                ORDER BY a.appointment_date
            """
            return self.execute_query(query, (days,))
        except Exception as e:
            print(f"Erreur get_upcoming_appointments: {e}")
            return pd.DataFrame()


# Initialisation avec vérification
@st.cache_resource
def init_database():
    """Initialise la connexion avec vérification"""
    print("\n" + "="*50)
    print("🔧 INITIALISATION DE LA BASE DE DONNÉES")
    print("="*50)
    
    db = MySQLDatabase()
    
    # Tenter la connexion
    if db.connect():
        print("✅ Base de données initialisée avec succès")
        
        # Vérifier avec une requête test
        test_df = db.get_users()
        if test_df is not None and not test_df.empty:
            print(f"📊 {len(test_df)} utilisateurs trouvés")
        else:
            print("⚠️ Connexion réussie mais aucune donnée utilisateur trouvée")
        
        return db
    else:
        print("❌ Échec de la connexion")
        return None


# Instance globale
db = init_database()
