import sqlite3
import os

def init_db():
    try:
        conn = sqlite3.connect("inventario.db")
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tag_qr TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'Disponível'
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipamento_id INTEGER,
            data_leitura DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(equipamento_id) REFERENCES equipamentos(id)
        )
        """)
        
        conn.commit()
        print("✅ Banco de dados sincronizado com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao iniciar banco: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
