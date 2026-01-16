# 📦 Nexus Manager

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen?style=for-the-badge)

**Nexus Manager** é uma solução completa e moderna para **Gestão de Inventário e Património**, desenvolvida para facilitar o controlo de equipamentos através de etiquetas **QR Code** e relatórios automáticos.

---

## ✨ Funcionalidades Principais

| Funcionalidade | Descrição |
| :--- | :--- |
| **📝 Cadastro Completo** | Registo de Nome, TAG/Património, Localização e Valor do ativo. |
| **📱 QR Code Automático** | Gera códigos QR únicos para cada item, com opção de **Download (PNG)** para impressão. |
| **📊 Relatórios Excel** | Exporta o inventário para planilhas formatadas (Tabela Azul) prontas para auditoria. |
| **📥 Importação Inteligente** | Importa dados de planilhas antigas (CSV/Excel) com mapeamento manual de colunas. |
| **🔍 Busca Avançada** | Pesquisa em tempo real por Nome, TAG ou Localização. |
| **🗂️ Ordenação** | Filtros para organizar por Preço (Maior/Menor), Nome (A-Z) ou Local. |
| **🌗 Aparência** | Interface moderna com suporte nativo a **Modo Escuro (Dark Mode)** e Claro. |
| **💾 Banco de Dados** | Sistema SQLite local (sem necessidade de internet). |

---

## 🛠️ Tecnologias Utilizadas

O projeto foi construído utilizando as melhores bibliotecas do ecossistema Python:

* **[Python 3.11](https://www.python.org/)** - Linguagem base.
* **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** - Interface Gráfica (GUI) moderna.
* **[Pandas](https://pandas.pydata.org/)** - Manipulação de dados e leitura de Excel/CSV.
* **[XlsxWriter](https://xlsxwriter.readthedocs.io/)** - Formatação avançada de planilhas Excel.
* **[Qrcode](https://pypi.org/project/qrcode/)** - Geração de códigos QR.
* **[SQLite3](https://www.sqlite.org/index.html)** - Banco de dados leve e integrado.
* **[PyInstaller](https://pyinstaller.org/)** - Compilação do executável (.exe).

---

## 📥 Download e Instalação (Windows)

Você não precisa ter o Python instalado para usar o Nexus Manager.

1.  Acesse a aba **[Releases](../../releases)** deste repositório.
2.  Baixe o arquivo `Nexus.exe` da versão mais recente (v1.0).
3.  Coloque o arquivo numa pasta de sua preferência.
4.  Execute o `Nexus.exe`.
    * *Nota: O sistema criará automaticamente o banco de dados e a pasta de imagens na primeira execução.*

---

## 💻 Como rodar o código fonte (Desenvolvedores)

Se deseja modificar o código ou contribuir:

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/joaorizzo0112/Nexus-Manager.git](https://github.com/joaorizzo0112/Nexus-Manager.git)
    cd Nexus-Manager
    ```

2.  **Crie um ambiente virtual (Recomendado):**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute o sistema:**
    ```bash
    python Nexus.py
    ```

---

## 🤝 Contribuição

Contribuições são bem-vindas!
1.  Faça um Fork do projeto.
2.  Crie uma Branch para sua Feature (`git checkout -b feature/NovaFeature`).
3.  Faça o Commit (`git commit -m 'Adiciona NovaFeature'`).
4.  Faça o Push (`git push origin feature/NovaFeature`).
5.  Abra um Pull Request.

---

## 📄 Licença

Este projeto está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<p align="center">
  Desenvolvido por <strong>João Rizzo</strong> 🚀
</p>
